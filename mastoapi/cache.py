from django.core.cache import cache
from django.conf import settings

DEFAULT_CACHE_TIMEOUT = 30

def cached_call(cache_key, func, *args, timeout=DEFAULT_CACHE_TIMEOUT, **kwargs):
    result = cache.get(cache_key)

    if result is not None:
        return result
    else:
        result = func(*args, **kwargs)
        cache.set(cache_key, result, timeout)
        return result

def status(api, status_id):
    # TODO: if MastodonNotFound or MastodonInternalServerError is raised, cache the reply
    return cached_call(
        f"{api.name}-status-{status_id}",
        api.status, status_id, timeout=settings.CACHE_STATUS
    )

def status_context(api, status_id):
    return cached_call(
        f"{api.name}-status_context-{status_id}",
        api.status_context, status_id, timeout=settings.CACHE_STATUS_CONTEXT
    )

def account_by_acct(api, acct):
    account = cache.get(f"{api.name}-account-{acct}")
    if account is None:
        results = cached_call(
            f"{api.name}-search-{acct}", 
            api.search, acct, resolve=False, result_type="accounts", 
            timeout=settings.CACHE_ACCOUNT
        )

        for a in results["accounts"]:
            if a["acct"] == acct:
                account = a
                set_account(api, account)
                break

    # TODO: cache the None value somehow
    return account

def set_account(api, account):
    """cache account object for a given API instance"""
    cache.set(f"{api.name}-account-{account['acct']}", account, settings.CACHE_ACCOUNT)

def home_timeline(api, max_id):
    return cached_call(
        f"{api.name}-home-timeline-{max_id}",
        api.timeline, timeline="home", max_id=max_id, limit=settings.TIMELINE_PAGINATION, 
        timeout=settings.CACHE_TIMELINE
    )

def account_timeline(api, account, max_id):
    return cached_call(
        f"{api.name}-account-timeline-{account['acct']}-{max_id}",
        api.account_statuses, account["id"], max_id=max_id, limit=settings.TIMELINE_PAGINATION, 
        timeout=settings.CACHE_TIMELINE
    )

def hashtag_timeline(api, hashtag, max_id):
    return cached_call(
        f"{api.name}-hashtag-timeline-{hashtag}-{max_id}",
        api.timeline_hashtag, hashtag, max_id=max_id, limit=settings.TIMELINE_PAGINATION,
        timeout=settings.CACHE_TIMELINE
    )