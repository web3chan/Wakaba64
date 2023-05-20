from django.test import TestCase
from unittest.mock import MagicMock

from mastoapi.models import Instance, MastoApi
from .cache import cached_call

class FakeApi:
    id = 312

    def account_verify_credentials(self):
        return {"foo": "bar"}

    def account_statuses(self, *args, **kwargs):
        return []

class MastoApiTestCase(TestCase):
    
    def test_example(self):
        instance = Instance(base_url="https://example.com", client_secret="test", client_id="foobar")
        instance.save()
        api = MastoApi(access_token="fake", instance=instance)
        api.save()
        self.assertEqual(instance.client_id, "foobar")

        api.api = MagicMock(return_value=FakeApi())
        result = api.account_verify_credentials()
        self.assertEqual(result["foo"], "bar")

        result = api.account_statuses("123", "321", "20")
        self.assertEqual(result, [])

        result = cached_call("foo-bar", api.account_statuses, "123", "321", "20", timeout=30)
        self.assertEqual(result, [])