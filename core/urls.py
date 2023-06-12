from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from core import views


urlpatterns = [
    path("rates/", views.RateList.as_view()),
    path("rates/<base>/", views.RateWithBase.as_view()),
    path("rates/<base>/<target>/", views.RateWithBaseAndTarget.as_view()),
    path("seed/", views.Seed.as_view()),
    path("register/", views.RegisterView.as_view()),
    path("login/", views.MyObtainTokenPairView.as_view()),
]