import json
import random
from datetime import datetime, timedelta
from analytics.models import Event

def run():
    pages = ['/home', '/about', '/products', '/cart', '/checkout']
    browsers = ['Chrome', 'Firefox', 'Safari', 'Edge']
    devices = ['desktop', 'mobile', 'tablet']
    referrers = ['google.com', 'facebook.com', 'twitter.com', None]
    products = ['Shoes', 'Bag', 'Watch', 'Shirt', 'Hat']


    events = []

    for i in range(100):
        event = {
            "event_name": "page_view" if random.random() > 0.2 else "purchase",
            "user_id": random.randint(1, 20),
            "session_id": f"session_{random.randint(1,10)}",
            "client_timestamp": (datetime.now() - timedelta(days=random.randint(0,500),
                                                           hours=random.randint(0,23),
                                                           minutes=random.randint(0,59))).isoformat(),
            "metadata": {
                "page": random.choice(pages),
                "browser": random.choice(browsers),
                "device": random.choice(devices),
                "referrer": random.choice(referrers),
                "product_id": random.randint(1, 10),
                "product": random.choice(products),
                "price": round(random.uniform(10, 500), 2)
            }
        }
        Event.objects.create(**event)
