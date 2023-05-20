from mastodon import MastodonIllegalArgumentError

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from mastoapi.models import MastoApi

class Command(BaseCommand):
    help = "Execute MastodonAPI methods"

    def add_arguments(self, parser):
        parser.add_argument('name', type=str, help="MastoApi name")
        parser.add_argument('method', type=str, help="method to call")
        parser.add_argument("_args", nargs="*", default=[])
        parser.add_argument("-k", "--kwargs", action="extend", nargs="*", default=[])

    def handle(self, *args, **options):
        # TODO: parse kwargs
        try:
            api = MastoApi.objects.get(name=options["name"])
            print(getattr(api, options["method"])(*options["_args"]))
        except Exception as e:
            print("exception:", type(e), e)