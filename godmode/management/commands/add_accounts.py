from mastodon import MastodonIllegalArgumentError

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from django.db import IntegrityError

from django.contrib.auth.models import User

from mastoapi.models import MastoApi
from accounts.models import Account

from godmode.views import random_string

class Command(BaseCommand):
    help = "Add accounts"

    def add_arguments(self, parser):
        parser.add_argument('name', type=str, help="MastoApi name")
        parser.add_argument('amount', type=int, help="number of accounts")
        parser.add_argument('--note', type=str, default="", help="note")
        parser.add_argument('-m', '--with-media', action='store_true', default=False, help="enable media uploads?")


    def handle(self, *args, **options):
        api = MastoApi.objects.get(name=options["name"]) # TODO: handle MastoApi.DoesNotExist in validation
        passcodes = []

        while options["amount"] > len(passcodes):
            try:
                username, password = random_string(16), random_string(16)
                user = User.objects.create_user(username, 'fake@localhost', password)
                Account.objects.create(user=user, api=api, media_uploads=options["with_media"], note=options["note"])
                passcodes.append(username + password)
            except IntegrityError:
                pass
        print("\n".join(passcodes))
