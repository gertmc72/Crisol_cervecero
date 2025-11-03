from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("beer/<int:beer_id>/", views.beer_detail, name="beer_detail"),

    path("beers/<int:beer_id>/threads/", views.threads_list_create, name="threads_list"),
    path("threads/<int:thread_id>/", views.thread_detail_reply, name="thread_detail"),

    path("report/<str:object_type>/<int:object_id>/", views.report_create, name="report_create"),
    path("moderation/", views.moderation_list, name="moderation_list"),
    path("moderation/<int:report_id>/<str:action>/", views.moderation_action, name="moderation_action"),

    path("admin/metrics/", views.admin_metrics, name="admin_metrics"),
]
