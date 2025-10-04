from django.http import JsonResponse
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

from rest_framework import generics, status , mixins
from rest_framework.decorators import api_view
from rest_framework.response import Response

from analytics.tasks import *
from analytics.models import Event
from analytics.serializers import EventSerializer, AnalyticsSerializer
from analytics.utils.analytics_utils import get_analytics_queryset
from analytics.utils.cache_utils import get_cache, save_cache

class CreateEvent(generics.ListCreateAPIView):
    serializer_class = EventSerializer
    queryset = Event.objects.all()
    def perform_create(self, serializer):
        data =serializer.validated_data
        create_event.delay(data)

    @method_decorator(cache_page(60*15, key_prefix='event_list'))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
class RetrieveDestroyEvent(mixins.RetrieveModelMixin,
                           mixins.DestroyModelMixin,
                           generics.GenericAPIView):

    queryset = Event.objects.all()
    serializer_class = EventSerializer

    def get(self,request,*args,**kwargs):
        return self.retrieve(request,*args,**kwargs)
    def delete(self,request,*args,**kwargs):
        return self.destroy(request,*args,**kwargs)

@api_view(['GET', 'POST'])
def analytics_view(request):
    if request.method == 'GET':
        cached_data =get_cache(request.GET)
        if cached_data :
            return Response({'request' : request.GET ,'analytics' :cached_data}, status=status.HTTP_200_OK)
        else:
            success ,data = get_analytics_queryset(request.GET)
            if success:
                save_cache(request.GET, data)
                return Response({'request': request.GET, 'analytics': data}, status=status.HTTP_200_OK)
            return Response({'errors' : data}, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'POST':
        cached_data = get_cache(request.data)
        if cached_data :
            return Response({'request' : request.data ,'analytics' :cached_data}, status=status.HTTP_200_OK)

        success, data = get_analytics_queryset(request.data)
        if success:
            save_cache(request.data, data)
            return Response({'request': request.data, 'analytics': data}, status=status.HTTP_200_OK)
        return Response({'errors' : data}, status=status.HTTP_400_BAD_REQUEST)

    return JsonResponse({'error': 'Invalid request.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)