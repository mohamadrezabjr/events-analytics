from django.urls import path
from analytics import views
urlpatterns = [
    path('events/', views.CreateEvent.as_view(), name='events'),
]