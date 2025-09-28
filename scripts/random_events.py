import random
from datetime import datetime, timedelta
from analytics.models import Event

pages = ['/home', '/about', '/products', '/cart', '/checkout']
browsers = ['Chrome', 'Firefox', 'Safari', 'Edge']
devices = ['desktop', 'mobile', 'tablet']
referrers = ['google.com', 'facebook.com', 'twitter.com', None]
products = ['Shoes', 'Bag', 'Watch', 'Shirt', 'Hat']

events = []

for i in range(50):
    k = random.random()

    event_name = 'page_view' if k < 0.6 else 'purchase' if k < 0.8 else 'button'
    event = {
        "event_name": event_name,
        "user_id": random.randint(1, 20),
        "session_id": f"session_{random.randint(1, 10)}",
        "client_timestamp": (datetime.now() - timedelta(days=random.randint(0, 10),
                                                        hours=random.randint(0, 23),
                                                        minutes=random.randint(0, 59))).isoformat(),
        "metadata": {
            "page": random.choice(pages),
            "browser": random.choice(browsers),
            "device": random.choice(devices),
            "referrer": random.choice(referrers),
            "product_id": random.randint(1, 10),
            "product": random.choice(products),
        }
    }
    if event_name == 'purchase':
        event['metadata']['price'] = round(random.uniform(10, 500), 2)
        event['metadata']['page'] = random.choice(f'products/{event["metadata"]["product_id"]}')
    Event.objects.create(**event)
