# 📊 EventsAnalytics API

## 🚀 Introduction

**EventsAnalytics** is a **Django REST Framework**-based API designed for tracking, managing, and analyzing user events.
It allows storing detailed event data and retrieving aggregated analytics reports efficiently, even under high request volumes.

---

## 🛠 Technologies

* [Python 3.x](https://www.python.org/)
* [Django REST Framework](https://www.django-rest-framework.org/)
* [PostgreSQL](https://www.postgresql.org/)
* [Docker & Docker Compose](https://www.docker.com/)
* [Celery](https://docs.celeryq.dev/) for asynchronous event processing
* Redis (used internally by Celery and caching layer)

---

## 📦 Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/mohamadrezabjr/events-analytics.git
cd events-analytics
```

### 2. Build and run Docker containers

```bash
docker-compose up --build
```

### 3. Apply migrations (inside the web container)

```bash
docker-compose exec web python manage.py migrate
```

### 4. Create a superuser (optional)

```bash
docker-compose exec web python manage.py createsuperuser
```

---

## ⚡ Background Processing with Celery

To handle high volumes of events efficiently, **EventsAnalytics** uses **Celery** for asynchronous event processing.

* Incoming event requests are queued and processed in the background.
* Reduces response time for API clients.
* Fully integrated into Docker Compose; no additional setup required.

> All `Create Event` requests are processed asynchronously, keeping endpoints fast and responsive.

---

## 🗄 Caching

**Request-level caching** improves performance and reduces backend load:

* All requests (GET or POST) are cached along with their request body.
* Responses are stored so repeated requests can be served immediately without reprocessing.
* **Maximum cache size** is defined in `analytics/tasks.py`.
* When exceeding this size, **least frequently used (LFU)** entries are automatically removed.
* Integrated with Docker Compose; no additional setup required.

> High-frequency requests are handled efficiently while keeping cache size under control.

---

## 📂 Data Model

### Event

| Field            | Data Type    | Description                         |
| ---------------- | ------------ | ----------------------------------- |
| id               | Integer (PK) | Unique identifier                   |
| event_name       | String       | Name of the event                   |
| timestamp        | DateTime     | Time when the event occurred        |
| server_timestamp | DateTime     | Time when server received the event |
| user_id          | String       | Identifier of the user (optional)   |
| session_id       | String       | Session identifier (optional)       |
| metadata         | JSONField    | Additional event details            |

---

## 🔗 API Endpoints

| Method | Endpoint            | Description                               |
| ------ |---------------------| ----------------------------------------- |
| GET    | `/api/events/`      | Retrieve all events                       |
| POST   | `/api/events/`      | Create a new event                        |
| GET    | `/api/events/{id}/` | Retrieve a specific event                 |
| DELETE | `/api/events/{id}/` | Delete an event                           |
| GET    | `/api/analytics/`   | Retrieve aggregated analytics             |
| POST   | `/api/analytics/`   | Retrieve aggregated analytics (JSON body) |

---

## 🆕 Create Event Endpoint

Endpoint:

```http
POST /api/events/
```

### Fields

| Field              | Data Type | Required | Description                        |
| ------------------ | --------- | -------- | ---------------------------------- |
| `event_name`       | String    | Yes      | Name of the event                  |
| `user_id`          | String    | No       | User identifier                    |
| `session_id`       | String    | No       | Session identifier                 |
| `timestamp`        | DateTime  | Yes      | Event timestamp on client          |
| `server_timestamp` | DateTime  | Yes      | Event received timestamp on server |
| `metadata`         | JSON      | No       | Additional event data              |

### Example Request

```json
POST /api/events/
{
  "event_name": "user_signup",
  "user_id": "123",
  "session_id": "abc-456",
  "timestamp": "2025-10-01T10:30:00Z",
  "server_timestamp": "2025-10-01T10:30:05Z",
  "metadata": {
    "device": "mobile",
    "browser": "Chrome",
    "page": "/signup",
    "referrer": "google"
  }
}
```

### Example Response

```json
{
  "id": 1,
  "event_name": "user_signup",
  "user_id": "123",
  "session_id": "abc-456",
  "timestamp": "2025-10-01T10:30:00Z",
  "server_timestamp": "2025-10-01T10:30:05Z",
  "metadata": {
    "device": "mobile",
    "browser": "Chrome",
    "page": "/signup",
    "referrer": "google"
  }
}
```

---

## 📊 Analytics Endpoint

Endpoint:

```http
GET /api/analytics/
POST /api/analytics/
```

### Parameters (GET)

| Field        | Data Type | Description          |
| ------------ | --------- | -------------------- |
| `metric`     | String    | Metric to analyze    |
| `user_id`    | String    | Filter by user ID    |
| `session_id` | String    | Filter by session ID |
| `from_date`  | DateTime  | Start date of range  |
| `to_date`    | DateTime  | End date of range    |

#### Metadata Fields

| Field        | Data Type | Description      |
| ------------ | --------- | ---------------- |
| `device`     | String    | Device type      |
| `browser`    | String    | Browser used     |
| `page`       | String    | Page URL         |
| `referrer`   | String    | Referring source |
| `product_id` | String    | Product ID       |
| `product`    | String    | Product name     |
| `price`      | Decimal   | Associated price |

#### Group By Options

| Option     | Description                 |
| ---------- | --------------------------- |
| day        | Group by day of the event   |
| week       | Group by week of the event  |
| month      | Group by month of the event |
| year       | Group by year of the event  |
| device     | Group by device used        |
| referrer   | Group by referral source    |
| metric     | Group by metric field       |
| user_id    | Group by user ID            |
| session_id | Group by session ID         |
| browser    | Group by browser            |
| product    | Group by product name       |
| product_id | Group by product ID         |

#### Aggregate Options

```python
['sum', 'count', 'avg', 'min', 'max']
```

#### Field for Aggregate

```python
['price','screen_width','screen_height','step']
```

#### Sorting

| Field     | Allowed Values        |
| --------- | --------------------- |
| `sort_by` | Field name to sort by |
| `order`   | `asc` or `desc`       |

### Analytics POST Method

* Supports JSON body for all query parameters (GET equivalent).

#### Example POST Request

```http
POST /api/analytics/
Content-Type: application/json

{
  "from_date": "2025-01-01T00:00:00Z",
  "to_date": "2025-02-01T00:00:00Z",
  "group_by": "day",
  "aggregate": "count",
  "metric": "purchase"
}
```

#### Example Response

```json
[
  {
    "day": "2025-01-01",
    "count": 42
  },
  {
    "day": "2025-01-02",
    "count": 38
  }
]
```

---

## 🛠 Generating Random Events (For Testing)

* Script: `random_events`
* Generates 50 random events.
* Run using django-extensions `runscript`:

```bash
docker-compose exec web python manage.py runscript random_events
```

> Populates the database with random events for testing API endpoints and analytics.

---

