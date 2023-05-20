from django.urls import path

from . import views

urlpatterns = [
    path('', views.Index.as_view(), name='godmode-index'),
    path('add-mastoapi', views.AddMastoapi.as_view(extra_context={'title': 'Add MastoApi'}), name='add-mastoapi'),
    path('add-accounts', views.AddAccounts.as_view(extra_context={'title': 'Add Accounts'}), name='add-accounts'),
    path('banhammer', views.Banhammer.as_view(extra_context={'title': 'BANHAMMER'}), name='banhammer'),
    path('purge', views.Purge.as_view(extra_context={'title': 'PURGE'}), name='purge'),
    path('unban', views.Unban.as_view(extra_context={'title': 'Remove ban'}), name='unban'),
    path('block', views.Block.as_view(extra_context={'title': 'Block remote user/instance'}), name='block'),
    path('follow', views.Follow.as_view(extra_context={'title': 'Follow/unfollow accounts'}), name='follow'),
]