from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("beers/", views.beer_list, name="beer_list"),
    path("beers/<int:beer_id>/", views.beer_detail, name="beer_detail"),
    path("beers/<int:beer_id>/review/create/",
         views.create_review, name="create_review"),
    # Ruta para crear reseña sin elegir una cerveza preexistente (entrada libre)
    path("beers/review/create/", views.create_review, name="create_review_free"),

    path("reviews/<int:review_id>/delete/",
         views.review_delete, name="review_delete"),

    path("threads/", views.threads_list_create, name="threads_list"),
    path("threads/<int:thread_id>/",
         views.thread_detail_reply, name="thread_detail"),
    path("threads/<int:thread_id>/delete/",
         views.thread_delete, name="thread_delete"),

    path("signup/", views.signup_view, name="signup"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    path("report/<str:object_type>/<int:object_id>/",
         views.report_create, name="report_create"),
    path("moderation/", views.moderation_list, name="moderation_list"),
    path("moderation/<int:report_id>/<str:action>/",
         views.moderation_action, name="moderation_action"),

    path("admin/metrics/", views.admin_metrics, name="admin_metrics"),
]
