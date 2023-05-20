from django.views.generic import TemplateView
from django.conf import settings


class Page(TemplateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["settings"] = settings
        return context

class Rules(Page):
    template_name = settings.RULES_TEMPLATE

class About(Page):
    template_name = settings.ABOUT_TEMPLATE
