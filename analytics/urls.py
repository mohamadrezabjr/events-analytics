from django.urls import path
from analytics import views
urlpatterns = [
    path('events/', views.CreateEvent.as_view(), name='events'),
    path('analytics/', views.analytics_view, name='analytics'),
    path('events/<int:pk>/', views.RetrieveDestroyEvent.as_view(), name='retrieve-event'),
]