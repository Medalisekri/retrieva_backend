# 🔍 Retrieva — Backend

> The REST API powering Retrieva, a lost-and-found platform. Built with Django 5.2 and Django REST Framework, backed by PostgreSQL, and secured through Firebase Authentication — with fuzzy item matching and push notifications built in.

![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)
![DRF](https://img.shields.io/badge/Django_REST_Framework-red?style=for-the-badge&logo=django&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![Firebase](https://img.shields.io/badge/Firebase-FFCA28?style=for-the-badge&logo=firebase&logoColor=black)

---

## Architecture

Firebase handles all authentication — registration, login, Google Sign-In, email verification, and password reset. Django handles everything else: items, search, permissions, chat, notifications, and business logic.

The Flutter client sends a Firebase ID token in the `Authorization` header with every request. Django's custom `FirebaseAuthentication` class verifies the token, then gets or creates a Django `User` using the Firebase UID as the username and attaches it to the request.

```
Flutter app
    │
    │  Authorization: Bearer <Firebase ID token>
    ▼
Django REST API
    ├── FirebaseAuthentication  →  verifies token, resolves User
    ├── items/                  →  CRUD, filtering, fuzzy matching, rate limiting
    ├── chats/                  →  conversations, messages, block/unblock
    └── accounts/               →  profiles, contact email
```

---

## Folder Structure

```
project/
├── accounts/
│   ├── models.py           # Profile model (OneToOneField → User, is_verified field)
│   ├── authentication.py   # FirebaseAuthentication class
│   ├── signals.py          # Auto-creates Profile on User creation
│   └── apps.py             # Loads signals and initializes Firebase Admin
├── items/
│   ├── models.py           # Item model
│   ├── serializers.py      # ItemListSerializer, ItemDetailSerializer
│   ├── views.py            # item_list, item_detail, report_item, my_items
│   ├── urls.py             # Item routes
│   ├── matching.py         # Fuzzy name matching logic
│   └── notifications.py    # OneSignal push notification logic
├── chats/
│   ├── models.py           # Conversation and Message models
│   ├── serializers.py      # ConversationSerializer, MessageSerializer
│   └── views.py            # chat_conv, chat_conv_detail, chat_msg, delete_msg, block_unblock
└── manage.py
```

---

## API Endpoints

### Items — public GET, protected POST / PATCH / DELETE

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/items/item/` | List all active, non-expired items. Supports `?type=`, `?category=`, `?status=` filters |
| `POST` | `/items/item/` | Create an item. Auth required. Max 5 posts per user per day |
| `GET` | `/items/item/<pk>/` | Get a single item. Returns 404 if expired |
| `PATCH` | `/items/item/<pk>/` | Update item. Owner only |
| `DELETE` | `/items/item/<pk>/` | Delete item. Owner only |
| `POST` | `/items/item/<pk>/report/` | Report an item. Auth required |
| `GET` | `/items/my-items/` | List the current user's items. Auth required |

### Chats — all require auth

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/chats/conversations/` | List the user's conversations |
| `POST` | `/chats/conversations/` | Create or retrieve an existing conversation for an item |
| `GET` | `/chats/conversations/<pk>/` | Get conversation detail |
| `GET` | `/chats/conversations/<pk>/messages/` | Get messages in a conversation |
| `POST` | `/chats/conversations/<pk>/messages/` | Send a message, triggers push notification |
| `DELETE` | `/chats/messages/<pk>/` | Soft-delete a message |
| `POST` | `/chats/conversations/<pk>/block/` | Toggle block / unblock for a conversation |

### Accounts

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/accounts/profile/` | Get the current user's profile. Auth required |
| `PATCH` | `/accounts/profile/` | Update profile. Auth required |
| `POST` | `/accounts/contact/` | Send a contact email via EmailJS. Auth required |

---

## Key Logic

| Feature | How it works |
|---|---|
| **Firebase Auth** | Flutter sends an ID token; Django verifies it with the Admin SDK and maps the UID to a Django `User` |
| **Owner check** | `PATCH` / `DELETE` return `403` if `item.user != request.user` |
| **Rate limiting** | Max 5 item posts per user per 24 hours — returns `429` if exceeded |
| **Auto-expiry** | Items expire 60 days after creation and are hidden from listings and direct lookups |
| **Fuzzy matching** | On new post, `SequenceMatcher` (threshold 0.6) searches opposite-type items from the last 30 days and notifies both owners on a match |
| **Push notifications** | OneSignal with Firebase UIDs as external IDs — no device token management needed |
| **Bidirectional chat** | Conversation lookup uses Django `Q` objects so existing chats are found regardless of participant order |

---

## Environment Variables

| Variable | Description |
|---|---|
| `SECRET_KEY` | Django secret key |
| `DATABASE_URL` | PostgreSQL connection string (production) |
| `FIREBASE_CREDENTIALS` | Full Firebase service account JSON as a string |
| `ONESIGNAL_APP_ID` | OneSignal application ID |
| `ONESIGNAL_REST_API_KEY` | OneSignal REST API key |
| `EMAILJS_SERVICE_ID` | EmailJS service ID |
| `EMAILJS_TEMPLATE_ID` | EmailJS template ID |
| `EMAILJS_PUBLIC_KEY` | EmailJS public key |

---

## Getting Started

**Prerequisites:** Python 3.11+, PostgreSQL, a Firebase project

**1. Clone the repo**
```bash
git clone https://github.com/yourusername/retrieva-backend.git
cd retrieva-backend
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Set environment variables**

Create a `.env` file at the project root and fill in the variables listed above.

**4. Run migrations**
```bash
python manage.py migrate
```

**5. (Optional) Seed sample items**
```bash
python manage.py seed_items
```

**6. Start the development server**
```bash
python manage.py runserver
```

---

## Tests

Tests use Django's `APITestCase` and `force_authenticate` to bypass Firebase token verification.

```bash
python manage.py test
```

| Test | What it covers |
|---|---|
| Active items appear in list | Basic item visibility |
| Expired items are hidden | Auto-expiry filter |
| Resolved items are hidden | Status filter |
| Filter by type works | Query param filtering |
| Owner can update their item | PATCH — authorized |
| Stranger cannot update item | PATCH — 403 expected |
| Stranger cannot delete item | DELETE — 403 expected |
| Owner can delete their item | DELETE — authorized |

---

## Deployment

The backend is deployed on **Render** (free tier) with a **Neon** PostgreSQL database.

| Step | Command |
|---|---|
| Build | `pip install -r requirements.txt && python manage.py collectstatic --noinput` |
| Start | `python manage.py migrate && gunicorn project.wsgi` |

> **Note:** The free tier on Render sleeps after inactivity. The first request after an idle period may take ~30 seconds to respond.

---

## What I Learned

- Firebase + Django hybrid auth — verifying ID tokens server-side with the Admin SDK and mapping Firebase UIDs to Django users
- Custom DRF authentication class — plugging into `DEFAULT_AUTHENTICATION_CLASSES` cleanly
- Fuzzy text matching — `SequenceMatcher` for name similarity across lost/found pairs
- OneSignal push notifications — using Firebase UIDs as external IDs to avoid managing device tokens
- Django Q objects — OR queries for bidirectional relationship lookups
- Production hardening — WhiteNoise for static files, `dj_database_url` for Neon SSL connections, environment-based settings