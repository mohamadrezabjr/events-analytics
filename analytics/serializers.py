from rest_framework import serializers
from analytics.models import Event

VALID_SORT_FIELDS = {
    'sum': lambda f: [f"sum_{f}", "date"],
    'avg': lambda f: [f"avg_{f}", "date"],
    'min': lambda f: [f"min_{f}", "date" ],
    'max': lambda f: [f"max_{f}", "date"],
    'count': lambda f: ["count", "date"],
    None: lambda f: ["date"],
}

class EventSerializer(serializers.ModelSerializer):
    timestamp = serializers.DateTimeField(source='client_timestamp')
    server_timestamp = serializers.DateTimeField(read_only=True)
    class Meta:
        model = Event
        fields = [
            'pk',
            'event_name',
            'user_id',
            'session_id',
            'timestamp',
            'server_timestamp',
            'metadata',

        ]
class AnalyticsSerializer(serializers.Serializer):
    metric = serializers.CharField(required=False, max_length=256)
    user_id = serializers.CharField(required=False, max_length=256)
    session_id = serializers.CharField(required=False, max_length=256)
    from_date = serializers.DateTimeField(required=False)
    to_date = serializers.DateTimeField(required=False)

    #Metadata fields
    device = serializers.CharField(required=False, max_length=256)
    browser = serializers.CharField(required=False, max_length=256)
    page = serializers.CharField(required=False, max_length=256)
    referrer = serializers.CharField(required=False, max_length=256)
    product_id = serializers.CharField(required=False, max_length=256)
    product = serializers.CharField(required=False, max_length=256)
    price = serializers.DecimalField(required=False, decimal_places=2, max_digits=10)


    #Group by :
    group_by_choices = ['day', 'week', 'month', 'year', 'device', 'referrer', 'metric', 'user_id', 'session_id',
                        'browser', 'product', 'product_id']
    group_by = serializers.ChoiceField(choices= group_by_choices,required=False)
    #Agreggate
    aggregate =serializers.ChoiceField(choices = ['sum', 'count', 'avg', 'min', 'max'], required=False)
    field = serializers.ChoiceField(choices=['price','duration', 'quantity'], required=False)

    sort_by = serializers.CharField(required=False)
    order = serializers.ChoiceField(choices=['asc', 'desc'], required=False)

    def validate(self, data):
        if data.get('aggregate') in ['sum', 'avg', 'min', 'max']:
            if not data.get('field'):
                raise serializers.ValidationError(f'For this aggregation ({data.get("aggregate")}), \"Field\" is required')
        if data.get('field') and data.get('aggregate') and data.get('sort_by'):
            field = data.get('field')
            valid_fields = VALID_SORT_FIELDS[data.get('aggregate')](field)
            sort_by = data.get('sort_by')
            aggregate = data.get('aggregate')
            if sort_by not in valid_fields:
                raise serializers.ValidationError(f'Sort by {sort_by} is not valid for this aggregate {aggregate}.Allowed : {valid_fields}')
        return data