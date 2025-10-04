from analytics.tasks import *
from analytics.models import Event
from django.db.models.expressions import RawSQL

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
def get_analytics_queryset(data):
    serializer = AnalyticsSerializer(data=data)

    if serializer.is_valid():
        filters = {}
        # Serializer fields filter
        serializer_fields = ['device', 'browser', 'page', 'referrer', 'product_id', 'product', 'price', 'metric',
                             'event_name', 'session_id', 'user_id']
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
                price_numeric=RawSQL(
                    "COALESCE((metadata->>%s)::double precision, 0)",
                    ("price",),
                    output_field=FloatField()
                )
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

