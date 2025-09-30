from dataclasses import field

from django.http import JsonResponse
from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from analytics.tasks import create_event
from analytics.models import Event
from analytics.serializers import CreateEventSerializer, EventSerializer
from django.db.models import Sum, Avg, DateTimeField, Count, Min, Max, F, FloatField, TextField, Value
from django.db.models.functions import Trunc, Cast, Coalesce, NullIf

AGGREGATE_FUNCS = {
    'sum': Sum,
    'avg': Avg,
    'min': Min,
    'max': Max,
    'count': Count,
}



class CreateEvent(generics.CreateAPIView):
    serializer_class = CreateEventSerializer
    def perform_create(self, serializer):
        data =serializer.validated_data
        create_event.delay(data)

def get_analytics_queryset(data):
    serializer = EventSerializer(data=data)

    if serializer.is_valid():
        filters = {}

        metric = serializer.validated_data.get('metric')
        user_id = serializer.validated_data.get('user_id')
        session_id = serializer.validated_data.get('session_id')
        start_time = serializer.validated_data.get('from_date')
        end_time = serializer.validated_data.get('to_date')

        # Group by :
        group_by = serializer.validated_data.get('group_by')
        # Aggregate
        aggregate = serializer.validated_data.get('aggregate')
        field = serializer.validated_data.get('field')

        # Metadata fields
        metadata_fields = ['device', 'browser', 'page', 'referer', 'product_id', 'product', 'price']
        for metadata_field in metadata_fields:
            if serializer.validated_data.get(field):
                filters[f'metadata__{metadata_field}'] = serializer.validated_data[metadata_field]

        if metric:
            filters['event_name'] = metric
        if user_id:
            filters['user_id'] = user_id
        if session_id:
            filters['session_id'] = session_id
        sort_by = serializer.validated_data.get('sort_by')
        if sort_by == 'timestamp':
            sort_by = 'client_timestamp'
        order = serializer.validated_data.get('order')

        queryset = Event.objects.filter(**filters).values()
        if start_time:
            queryset = queryset.filter(client_timestamp__gte=start_time)
        if end_time:
            queryset = queryset.filter(client_timestamp__lte=end_time)
        field_name = None
        if field:
            queryset = queryset.annotate(
                **{field + '_numeric': Cast(F(f'metadata__{field}'), FloatField())}
            )
            field_name = field + '_numeric'
        if group_by:
            queryset = queryset.annotate(date=Trunc('client_timestamp', group_by, output_field=DateTimeField()))
            queryset = queryset.values('date')

            if aggregate in ['sum', 'avg', 'min', 'max', 'count']:
                agg_func = AGGREGATE_FUNCS[aggregate]
                key = f"{aggregate}_{field}" if aggregate != 'count' else 'count'
                queryset = queryset.annotate(**{key : agg_func(field_name)})

            else:
                queryset = queryset.annotate(count=Count('id'))

            if sort_by:
                order_pre = '' if order =='asc' else '-'
                queryset = queryset.order_by(order_pre + sort_by)
            else:
                queryset = queryset.order_by('-date')
        else:
            if aggregate in ['sum', 'avg', 'min', 'max']:
                agg_func = AGGREGATE_FUNCS[aggregate]
                key = f"{aggregate}_{field}" if aggregate != 'count' else 'count'
                queryset = queryset.aggregate(**{key : agg_func(field_name)})
            elif aggregate == 'count':
                queryset = queryset.aggregate(count=Count('id'))
        return True,queryset

    return False, serializer.errors


@api_view(['GET', 'POST'])
def analytics_view(request):
    if request.method == 'GET':
        success ,data = get_analytics_queryset(data=request.GET)
        if success:
            return Response({'request' : request.GET ,'analytics' :data}, status=status.HTTP_200_OK)
        return Response({'errors' : data}, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'POST':
        success ,data = get_analytics_queryset(data=request.data)
        if success:
            return Response({'request' : request.data ,'analytics' :data}, status=status.HTTP_200_OK)
        return Response({'errors' : data}, status=status.HTTP_400_BAD_REQUEST)

    return JsonResponse({'error': 'Invalid request.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)