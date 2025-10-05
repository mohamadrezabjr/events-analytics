
import random
import time
import requests
import datetime
import uuid

events = []
def run(*args):

    n = 50

    if args:
        for arg in args:
            try :
                arg = int(arg)
            except :
                pass
            else:
                n= arg
                break
    API_URL = "http://localhost:8000/api/events/"

    EVENT_NAMES = ["page_view", "click", "purchase", "signup"]
    DEVICES = ["desktop", "mobile", "tablet"]
    BROWSERS = ["chrome", "firefox", "safari", "edge"]
    PAGES = ["/home", "/about", "/products", "/checkout", "/login", "/signup"]
    REFERRERS = ["google.com", "twitter.com", "facebook.com", "direct"]
    PRODUCTS = ["Laptop", "Phone", "Headphones", "Keyboard", "Mouse"]

    def random_event():
        event_name = random.choice(EVENT_NAMES)

        metadata = {
            "device": random.choice(DEVICES),
            "browser": random.choice(BROWSERS),
            "page": random.choice(PAGES),
            "referrer": random.choice(REFERRERS),
        }

        if event_name in ["purchase", "click"] and random.random() < 0.8:
            metadata["product_id"] = str(random.randint(100, 500))
            metadata["product"] = random.choice(PRODUCTS)
            metadata["price"] = round(random.uniform(10, 2000), 2) if random.random() < 0.9 else None
            metadata["page"] = f'products/{metadata["product_id"]}'
        if event_name == 'signup':
            metadata["page"] = "/signup"
        return {
            "event_name": event_name,
            "user_id": str(random.randint(1, 50)),
            "session_id": str(uuid.uuid4()),
            "timestamp": (datetime.datetime.now() - datetime.timedelta(
                hours=random.randint(0, 20000),


            )).isoformat(),
            "metadata": metadata
        }

    def generate_and_send_events(n):
        for i in range(n):
            event = random_event()
            s_time = time.time()
            response = requests.post(API_URL, json=event)
            e_time = time.time()
            if response.status_code == 201:
                print(f"*{i} - ✅ Event created:", f"Response time : {round((e_time - s_time)*1000, 2)} ms")
            else:
                print("❌ Failed:", response.status_code, response.text)

    start = time.time()
    generate_and_send_events(n)
    end = time.time()
    total_time = end - start
    print(f"Total Response time for {n} requests : {round((total_time)*1000, 2)} ms ({round(total_time,2)} seconds)")



