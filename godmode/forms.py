from django import forms
from django.core.exceptions import ValidationError

from django.conf import settings


class AddMastoapi(forms.Form):
    name = forms.CharField(label='MastoApi name', initial=settings.ANONYMOUS_MASTOAPI)
    base_url = forms.CharField(label='API base URL (i.e. https://mastodon.social)')
    email = forms.EmailField(label='email')
    password = forms.CharField(label='password')

class AddAccounts(forms.Form):
    name = forms.CharField(label='MastoApi name', initial=settings.ANONYMOUS_MASTOAPI)
    amount = forms.IntegerField(label="amount", initial=1, min_value=1, max_value=10000)
    media_uploads = forms.BooleanField(label="allow media uploads?", initial=True, required=False)
    note = forms.CharField(label='note', initial="", required=False, max_length=140)

class Banhammer(forms.Form):
    reason = forms.CharField(label='reason', initial="offtopic", max_length=140)
    status_id = forms.CharField(label='status id', min_length=18, max_length=18)
    duration = forms.IntegerField(label="duration (hours)", initial=24, min_value=1)
    remove = forms.BooleanField(label="remove status?", initial=False, required=False)

class Purge(forms.Form):
    reason = forms.CharField(label='reason', initial="spam", max_length=140)
    status_id = forms.CharField(label='status id', min_length=18, max_length=18)

class Unban(forms.Form):
    ban_id = forms.IntegerField(label="ban id", min_value=1)

class Block(forms.Form):
    name = forms.CharField(label='MastoApi name', initial=settings.ANONYMOUS_MASTOAPI)
    status_id = forms.CharField(label='status id', min_length=18, max_length=18)
    domain = forms.BooleanField(label="block domain?", initial=False, required=False)

class Follow(forms.Form):
    name = forms.CharField(label='MastoApi name', initial=settings.ANONYMOUS_MASTOAPI)
    account = forms.CharField(label='fediverse account', max_length=200)
    unfollow = forms.BooleanField(label="unfollow?", initial=False, required=False)