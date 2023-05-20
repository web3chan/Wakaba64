import datetime

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from board.models import Status
from godmode.models import Ban

class Command(BaseCommand):
    help = "Purge user account and data by status_id"

    def add_arguments(self, parser):
        parser.add_argument('status_id', type=int, help="status id")

    def handle(self, *args, **options):
        # TODO: write form.cleaned_data["reason"] to the modlog
        try:
            status = Status.objects.get(status_id=options["status_id"])
        except Status.DoesNotExist:
            print("no such status in the database")
            return
        
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

        print("die motherfucker!")