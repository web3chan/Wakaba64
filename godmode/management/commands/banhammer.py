import datetime

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from board.models import Status
from godmode.models import Ban

class Command(BaseCommand):
    help = "Ban user"

    def add_arguments(self, parser):
        parser.add_argument('status_id', type=int, help="status id")
        parser.add_argument('-d', "--duration", type=int, default=24, help="ban duration (hours)")
        parser.add_argument('--reason', type=str, default="offtopic", help="reason")
        parser.add_argument('-r', '--remove-status', action='store_true', default=False, help="remove status?")


    def handle(self, *args, **options):
        try:
            status = Status.objects.get(status_id=options["status_id"])
        except Status.DoesNotExist:
            print("no such status in the database")
            return 

        expires = datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(hours=options["duration"])

        Ban.objects.create(user=status.user, expires=expires, reason=options["reason"])

        if options["remove_status"]:
            try:
                status.user.account.api.status_delete(options["status_id"])
            except Exception as e:
                print(type(e), e)
