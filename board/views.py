import logging
import datetime

from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseServerError, Http404
from django.conf import settings
from django.urls import reverse
from django.views.generic.edit import FormView
from django.core.cache import cache

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from mastodon import MastodonNotFoundError, MastodonInternalServerError

from .models import Status, MediaUpload
from .forms import CreateStatus, ReportForm, STATUS_ID_RE, USER_ID_RE

from godmode.models import Ban
from mastoapi.models import MastoApi

import mastoapi.cache

#### Helpers

def _get_pagination(statuses, paginate_by):
    pagination = {}
    if len(statuses) == paginate_by:
        if hasattr(statuses[-1], "_pagination_next"):
            pagination["max_id"] = statuses[-1]._pagination_next["max_id"]
    return pagination

def _ratelimited(request):
    if settings.LIMIT_POSTS_PER_DAY:
        postcount = Status.objects.filter(user=request.user, created__gte=datetime.date.today()).count()
        if postcount >= settings.LIMIT_POSTS_PER_DAY:
            return True

    return False

def _create_status_form_handler(request, form):
    """Handle valid CreateStatus form submitted by a user"""
    api = MastoApi.get_api(request.user)

    ## file upload
    media_id = None
    if request.user.account.media_uploads and "media" in request.FILES:
        media_id = api.media_post(request.FILES["media"].read(),
            mime_type=request.FILES["media"].content_type)["id"]
        MediaUpload.objects.create(user=request.user, media_id=media_id)
        logging.info(f"MediaUpload created: {media_id} by {request.user}")
    ## /end file upload

    ## create status
    status_id = api.status_post(
        form.cleaned_data["comment"],
        spoiler_text=form.cleaned_data["topic"] or None,
        in_reply_to_id=form.cleaned_data["in_reply_to_id"] or None,
        media_ids=media_id,
        visibility=settings.STATUS_VISIBILITY
    )["id"]
    Status.objects.create(user=request.user, status_id=status_id)
    logging.info(f"Status created: {status_id} by {request.user}")
    ## /end create status

    return redirect(reverse("read-status", args=[status_id]) + "#SS")

#### EndHelpers


#### Views

def home_timeline(request):
    api = MastoApi.get_api(request.user)

    max_id = request.GET.get("max_id")
    if max_id and not STATUS_ID_RE.fullmatch(max_id):
        raise Http404

    statuses = mastoapi.cache.home_timeline(api, max_id)
    pagination = _get_pagination(statuses, settings.TIMELINE_PAGINATION)

    return render(request, 'board/home_timeline.html',
                {"settings": settings, "statuses": statuses, "pagination": pagination})

def account_timeline(request, acct):
    api = MastoApi.get_api(request.user)

    max_id = request.GET.get("max_id")
    if max_id and not STATUS_ID_RE.fullmatch(max_id):
        raise Http404

    account = mastoapi.cache.account_by_acct(api, acct)
    if account is None:
        raise Http404

    statuses = mastoapi.cache.account_timeline(api, account, max_id)
    pagination = _get_pagination(statuses, settings.TIMELINE_PAGINATION)

    return render(request, 'board/account_timeline.html', 
                {"settings": settings, "statuses": statuses, "pagination": pagination, "account": account})

def hashtag_timeline(request, hashtag):
    api = MastoApi.get_api(request.user)

    max_id = request.GET.get("max_id")
    if max_id and not STATUS_ID_RE.fullmatch(max_id):
        raise Http404

    statuses = mastoapi.cache.hashtag_timeline(api, hashtag, max_id)
    pagination = _get_pagination(statuses, settings.TIMELINE_PAGINATION)

    return render(request, 'board/hashtag_timeline.html',
                {"settings": settings, "statuses": statuses, "pagination": pagination, "hashtag": hashtag})

def read_status(request, status_id):
    api = MastoApi.get_api(request.user)

    try:
        status = mastoapi.cache.status(api, status_id)
        context = mastoapi.cache.status_context(api, status_id)
    except (MastodonNotFoundError, MastodonInternalServerError):
        raise Http404

    return render(request, 'board/read_status.html',
                {"settings": settings, "status": status, "context": context})

#### Wakaba.pl

@login_required
def create_status(request):
    bans = Ban.objects.filter(user=request.user, expires__date__gt=datetime.datetime.now())
    if bans:
        return render(request, 'board/banned.html', {'settings': settings, 'bans': bans})

    if _ratelimited(request):
        return HttpResponseForbidden("You are posting too much")

    if request.method == "GET":
        board = None
        parent = None

        if "board" in request.GET:
            board = request.GET["board"]  # TODO: validation
        elif "in_reply_to_id" in request.GET:
            parent_id = request.GET["in_reply_to_id"]
            if not STATUS_ID_RE.fullmatch(parent_id):
                raise Http404

            try:
                api = MastoApi.get_api(request.user)
                parent = mastoapi.cache.status(api, parent_id)
            except MastodonNotFoundError:
                raise Http404

        return render(request, 'board/wakaba.html', 
                    {"settings": settings, "board": board, "parent": parent})
    elif request.method == "POST":
        form = CreateStatus(request.POST, request.FILES)
        if form.is_valid():
            return _create_status_form_handler(request, form)
        else:
            return HttpResponseServerError(form.errors.as_json(escape_html=True))

#### EndWakaba.pl

class Report(LoginRequiredMixin, FormView):
    template_name = 'board/report.html'
    form_class = ReportForm
    success_url = 'report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["settings"] = settings
        return context

    def get_initial(self):
        data = super().get_initial()
        data["status_id"] = self.request.GET.get("status_id")
        return data

    def form_valid(self, form):
        if self._ratelimited():
            return HttpResponseServerError("You are reporting too fast!")
        api = MastoApi.get_api(self.request.user)

        try:
            status = mastoapi.cache.status(api, form.cleaned_data["status_id"])
        except MastodonNotFoundError:
            raise Http404

        comment = "{} -- reported by {}".format(form.cleaned_data["comment"], self.request.user)
        api.report(status['account']['id'], status_ids=[form.cleaned_data["status_id"]], comment=comment)

        return HttpResponse("Report sent. Thanks!")

    def _ratelimited(self):
        """limit to 1 report per minute from a user"""
        last_report = self.request.session.get("last_report")
        if last_report and (datetime.datetime.now().timestamp() - last_report) < 60:
            return True
        self.request.session["last_report"] = datetime.datetime.now().timestamp()
        return False

#### EndViews