import re
from django import forms
from django.core.exceptions import ValidationError

STATUS_ID_RE = re.compile("^[A-Za-z0-9]{18}$")
USER_ID_RE = re.compile("^[A-Za-z0-9]{1,18}$")

class ReportForm(forms.Form):
    status_id = forms.RegexField(STATUS_ID_RE, label="status_id")
    comment = forms.CharField(label='comment', max_length=140, widget=forms.Textarea)

## wakaba.pl form

class CreateStatus(forms.Form):
    topic = forms.CharField(label='topic', max_length=140, required=False)
    comment = forms.CharField(label='comment', max_length=5000, required=False)
    in_reply_to_id = forms.RegexField(STATUS_ID_RE, label="in_reply_to_id", required=False)
    media = forms.FileField(label="file", required=False)

    def clean(self):
        data = super().clean()

        if ("in_reply_to_id" not in data or not data["in_reply_to_id"]) and \
           ("topic" not in data or not data["topic"]):
            raise ValidationError("topic is required for new threads")

        if not data["media"] and not data["comment"]:
            raise ValidationError("image or comment required")