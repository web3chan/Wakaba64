from mastodon import MastodonIllegalArgumentError

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from mastoapi.models import MastoApi

class Command(BaseCommand):
    help = "Add Mastodon API account"

    def add_arguments(self, parser):
        parser.add_argument('name', type=str, help="MastoApi name")
        parser.add_argument('base_url', type=str, help="API base URL (i.e. https://mastodon.social)")
        parser.add_argument('email', type=str, help="account email")
        parser.add_argument('password', type=str, help="account password")

    def handle(self, *args, **options):
        try:
            api = MastoApi.log_in(options["name"], options["base_url"], options["email"], options["password"])
        except MastodonIllegalArgumentError as e:
            print(type(e), e)
            return

        print(f"{options['name']} added!")
