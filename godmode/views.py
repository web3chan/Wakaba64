import random
import string
import datetime

from django.shortcuts import render
from django.http import HttpResponse
from django.db import IntegrityError
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from django.conf import settings

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.models import User

from board.models import Status, MediaUpload
from mastoapi.models import MastoApi
from accounts.models import Account
from .models import Ban
from . import forms

nft_chars = string.ascii_lowercase + string.ascii_uppercase + string.digits

def random_string(length):
    return "".join(random.choices(nft_chars, k=length))

class StaffMemberRequired(UserPassesTestMixin):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["settings"] = settings
        return context

    def test_func(self):
        return self.request.user.is_staff


class Index(StaffMemberRequired, TemplateView):
    template_name = 'godmode/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        date_24h = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=24)
        date_1h = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=1)

        context["users"] = User.objects.all().count()
        context["statuses"] = Status.objects.all().count()
        context["statuses_24h"] = Status.objects.filter(created__gte=date_24h).count()
        context["statuses_1h"] = Status.objects.filter(created__gte=date_1h).count()

        context["uploads"] = MediaUpload.objects.all().count()
        context["uploads_24h"] = MediaUpload.objects.filter(created__gte=date_24h).count()
        context["uploads_1h"] = MediaUpload.objects.filter(created__gte=date_1h).count()

        return context


class AddMastoapi(StaffMemberRequired, FormView):
    template_name = 'godmode/form.html'
    form_class = forms.AddMastoapi
    success_url = 'add-mastoapi'

    def form_valid(self, form):
        try:
            api = MastoApi.log_in(form.cleaned_data["name"], form.cleaned_data["base_url"], form.cleaned_data["email"], form.cleaned_data["password"])
        except Exception as e:
            return HttpResponse("{}: {}".format(type(e), e))

        return super().form_valid(form)

class AddAccounts(StaffMemberRequired, FormView):
    template_name = 'godmode/form.html'
    form_class = forms.AddAccounts
    success_url = 'add-accounts'

    def form_valid(self, form):
        api = MastoApi.objects.get(name=form.cleaned_data["name"]) # TODO: handle MastoApi.DoesNotExist in validation
        passcodes = []

        while form.cleaned_data["amount"] > len(passcodes):
            try:
                username, password = random_string(16), random_string(16)
                user = User.objects.create_user(username, 'fake@localhost', password)
                Account.objects.create(user=user, api=api, media_uploads=form.cleaned_data["media_uploads"], note=form.cleaned_data["note"])
                passcodes.append(username + password)
            except IntegrityError:
                pass
        return HttpResponse("\n".join(passcodes), content_type="text/plain")

class Banhammer(StaffMemberRequired, FormView):
    template_name = 'godmode/form.html'
    form_class = forms.Banhammer
    success_url = 'banhammer'

    def form_valid(self, form):
        try:
            status = Status.objects.get(status_id=form.cleaned_data["status_id"])
        except Status.DoesNotExist:
            return HttpResponse("no such status in the database")

        expires = datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(hours=form.cleaned_data["duration"])

        Ban.objects.create(user=status.user, expires=expires, reason=form.cleaned_data["reason"])

        if form.cleaned_data["remove"]:
            try:
                status.user.account.api.status_delete(form.cleaned_data["status_id"])
            except Exception as e:
                print(type(e), e)

        return super().form_valid(form)

class Purge(StaffMemberRequired, FormView):
    template_name = 'godmode/form.html'
    form_class = forms.Purge
    success_url = 'purge'

    def form_valid(self, form):
        # TODO: write form.cleaned_data["reason"] to the modlog
        try:
            status = Status.objects.get(status_id=form.cleaned_data["status_id"])
        except Status.DoesNotExist:
            return HttpResponse("no such status in the database")
        user = status.user
        user.set_password("purged")
        user.is_active = False
        user.save()
        # TODO: remove media (not implemented in Mastodon.py?)
        # MediaUpload.objects.filter(user=user).delete()

        for s in Status.objects.filter(user=user):
            try:
                user.account.api.status_delete(s.status_id)
            except Exception as e:
                print(type(e), e)

        # Status.objects.filter(user=user).delete()
        return super().form_valid(form)

class Unban(StaffMemberRequired, FormView):
    template_name = 'godmode/form.html'
    form_class = forms.Unban
    success_url = 'unban'

    def form_valid(self, form):
        Ban.objects.get(id=form.cleaned_data["ban_id"]).delete()
        return super().form_valid(form)

class Block(StaffMemberRequired, FormView):
    template_name = 'godmode/form.html'
    form_class = forms.Block
    success_url = 'block'

    def form_valid(self, form):
        api = MastoApi.objects.get(name=form.cleaned_data["name"])
        status = api.status(form.cleaned_data["status_id"])
        if form.cleaned_data["domain"]:
            domain = status["account"]["acct"].split("@")[1]
            api.domain_block(domain)
        else: 
            api.account_block(status["account"]["id"])

        return super().form_valid(form)

class Follow(StaffMemberRequired, FormView):
    template_name = 'godmode/form.html'
    form_class = forms.Follow
    success_url = 'follow'

    def form_valid(self, form):
        api = MastoApi.objects.get(name=form.cleaned_data["name"])
        accs = api.account_search(form.cleaned_data["account"])

        if len(accs) > 0:
            if form.cleaned_data["unfollow"]:
                api.account_unfollow(accs[0]["id"])
            else: 
                api.account_follow(accs[0]["id"])

        return super().form_valid(form)
