from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from godmode.models import Ban

class Command(BaseCommand):
    help = "Unban user"

    def add_arguments(self, parser):
        parser.add_argument('ban_id', type=int, help="ban id")

    def handle(self, *args, **options):
        try:
            Ban.objects.get(id=options["ban_id"]).delete()
        except:
            print("ban does not exist")
