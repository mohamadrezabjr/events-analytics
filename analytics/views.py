from django.http import JsonResponse

from rest_framework import generics, status , mixins
from rest_framework.decorators import api_view
from rest_framework.response import Response

from analytics.tasks import *
from analytics.models import Event

from analytics.serializers import EventSerializer, AnalyticsSerializer
from django.db.models import Sum, Avg, DateTimeField, Count, Min, Max, F, FloatField
from django.db.models.functions import Trunc, Cast



AGGREGATE_FUNCS = {
    'sum': Sum,
    'avg': Avg,
    'min': Min,
    'max': Max,
    'count': Count,
}

FIELDS = {
    'day': '-date',
    'week': '-date',
    'month': '-date',
    'year': '-date',
    'device': 'metadata__device',
    'referrer': 'metadata__referrer',
    'page': 'metadata__page',
    'browser': 'metadata__browser',
    'product': 'metadata__product',
    'product_id': 'metadata__product_id',
    'metric' : 'event_name',
    'user_id': 'user_id',
    'session_id': 'session_id',
    'price' : 'metadata__price',
    'timestamp' : 'client_timestamp',

}

def get_cache(key):
    con = get_redis_connection('default')
    hashed_key = hash_data(key)
    cached = con.get(f'request:{hashed_key}')

    if cached:
        cached = json.loads(cached)
        cached['hits'] += 1
        cached['last_used'] = datetime.now()
        con.set(f'request:{hashed_key}', json.dumps(cached, cls=DjangoJSONEncoder))
        return cached.get('data')
    else:
        return None

def save_cache(key, data):
    if not isinstance(data, dict):
        data = list(data)
    save_cache_task.delay(key, data)



class CreateEvent(generics.ListCreateAPIView):
    serializer_class = EventSerializer
    queryset = Event.objects.all()
    def perform_create(self, serializer):
        data =serializer.validated_data
        create_event.delay(data)
class RetrieveDestroyEvent(mixins.RetrieveModelMixin,
                           mixins.DestroyModelMixin,
                           generics.GenericAPIView):

    queryset = Event.objects.all()
    serializer_class = EventSerializer

    def get(self,request,*args,**kwargs):
        return self.retrieve(request,*args,**kwargs)
    def delete(self,request,*args,**kwargs):
        return self.destroy(request,*args,**kwargs)

def get_analytics_queryset(data):
    serializer = AnalyticsSerializer(data=data)

    if serializer.is_valid():
        filters = {}
        # Serializer fields filter
        serializer_fields = ['device', 'browser', 'page', 'referrer', 'product_id', 'product', 'price', 'metric',
                             'even_name']
        for serializer_field in serializer_fields:
            if serializer.validated_data.get(serializer_field):
                filters[FIELDS.get(serializer_field)] = serializer.validated_data[serializer_field]

        start_time = serializer.validated_data.get('from_date')
        end_time = serializer.validated_data.get('to_date')

        # Group by :
        group_by = serializer.validated_data.get('group_by')
        # Aggregate
        aggregate = serializer.validated_data.get('aggregate')
        field = serializer.validated_data.get('field')

        sort_by = serializer.validated_data.get('sort_by')

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

        if group_by in FIELDS:

            if group_by in ['day', 'week', 'month', 'year']:
                queryset = queryset.annotate(date=Trunc('client_timestamp', group_by, output_field=DateTimeField()))
                queryset = queryset.values('date')
            else :
                queryset = queryset.values(FIELDS.get(group_by))

            if aggregate in ['sum', 'avg', 'min', 'max']:
                agg_func = AGGREGATE_FUNCS[aggregate]
                key = f"{aggregate}_{field}"
                queryset = queryset.annotate(**{key : agg_func(field_name)})

            else:
                queryset = queryset.annotate(count=Count('id'))

            if sort_by in FIELDS:
                order_pre = '' if order =='asc' else '-'
                queryset = queryset.order_by(order_pre + FIELDS.get(sort_by))
            elif sort_by:
                queryset = queryset.order_by(sort_by)
        else:
            if aggregate in ['sum', 'avg', 'min', 'max']:
                agg_func = AGGREGATE_FUNCS[aggregate]
                key = f"{aggregate}_{field}" if aggregate != 'count' else 'count'
                queryset = queryset.aggregate(**{key : agg_func(field_name)})

            elif aggregate == 'count':
                queryset = queryset.aggregate(count=Count('id'))

            elif sort_by:
                order_pre = '' if order =='asc' else '-'
                queryset = queryset.order_by(order_pre + FIELDS.get(sort_by))
        return True,queryset

    return False, serializer.errors


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
