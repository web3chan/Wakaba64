from django.db import models
from django.conf import settings

from mastodon import Mastodon

DEFAULT_APP_NAME = "Wakaba64"
MASTODON_VERSION = "2.7.2"

class Instance(models.Model):
    base_url = models.CharField(max_length=200)
    client_id = models.CharField(max_length=43)
    client_secret = models.CharField(max_length=43)

    def __str__(self):
        return self.base_url

    @staticmethod
    def register(base_url, app_name=DEFAULT_APP_NAME):
        client_id, client_secret = Mastodon.create_app(app_name, api_base_url=base_url)
        return Instance.objects.create(base_url=base_url, 
                                    client_id=client_id, client_secret=client_secret)

class MastoApi(models.Model):
    name = models.CharField(max_length=200, unique=True)
    access_token = models.CharField(max_length=43)
    instance = models.ForeignKey(Instance, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def api(self):
        """Cached Mastodon api object"""
        # TODO: actually cache it OR find why it's so slow to init
        return Mastodon(access_token=self.access_token,
                    api_base_url=self.instance.base_url,
                    mastodon_version=MASTODON_VERSION)

    @staticmethod
    def log_in(name, base_url, email, password):
        try:
            instance = Instance.objects.get(base_url=base_url)
        except Instance.DoesNotExist:
            instance = Instance.register(base_url)

        api = Mastodon(client_id=instance.client_id, client_secret=instance.client_secret, api_base_url=base_url)
        access_token = api.log_in(email, password)

        return MastoApi.objects.create(name=name, access_token=access_token, instance=instance)

    @staticmethod
    def get_default():
        return MastoApi.objects.get(name=settings.ANONYMOUS_MASTOAPI)

    @staticmethod
    def get_api(user):
        if user.is_anonymous:
            return MastoApi.get_default()
        else:
            return user.account.api

    def __getattr__(self, name):
        api = self.api()
        if hasattr(api, name):
            return getattr(api, name)
        else:
            raise AttributeError
