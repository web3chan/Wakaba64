from django.urls import path, re_path

from . import views, pages

urlpatterns = [
    path('', views.home_timeline, name='home-timeline'),
    re_path(r'^@(?P<acct>[\w@\-\.]+)/$', views.account_timeline, name='account-timeline'),
    re_path(r'^tag/(?P<hashtag>\w+)/$', views.hashtag_timeline, name='hashtag-timeline'),
    re_path(r'^res/(?P<status_id>\w{1,18}).html$', views.read_status, name='read-status'),
    path('wakaba.pl', views.create_status, name='create-status'),
    path('report.html', views.Report.as_view(), name='report.html'),
]

pages = {
    'pages/rules.html': pages.Rules.as_view(),
    'pages/about.html': pages.About.as_view()
}

for page, func in pages.items():
    urlpatterns.append(path(page, func, name=page))