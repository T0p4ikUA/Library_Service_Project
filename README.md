# Library Service Project

## Project Description
Many local libraries still rely on outdated paper-based tracking systems, requiring cash payments and manual record-keeping. This lack of automation creates several challenges:
- Inability to check book inventory in real-time.
- Difficulty tracking borrowing periods and identifying overdue books.
- Limited payment options for users.

**Solution:**  
This project is an online management system for book borrowings designed to automate library operations, streamline tracking for administrators, and improve the user experience. The system provides a fully functional REST API via Django REST Framework to handle book inventory, user management, borrowings, automated fine calculations, Stripe payments, and Telegram notifications.

---

## Technologies & Stack
- **Language & Framework:** Python 3.12, Django, Django REST Framework (DRF)
- **Database:** PostgreSQL
- **Cache & Broker:** Redis
- **Background Tasks:** Django-Q
- **Payments:** Stripe API
- **Notifications:** Telegram Bot API
- **Code Quality & Style:** Black, Flake8
- **Containerization:** Docker & Docker Compose

---

## Core Features
- **Books Management:** Full CRUD operations for books with inventory tracking and price validation (restricted to admin users, read-only for guests).
- **User Authentication:** Custom user model based on `email`, with JWT-powered authentication (`SimpleJWT`).
- **Borrowings Service:** Create borrowings (automatically decreases book inventory by 1), filter by active status or user ID, and return books (increases inventory, calculates fines if overdue).
- **Payments Integration:** Automated Stripe Checkout session generation on borrowing creation, success/cancel handling, and fine payment processing.
- **Notifications & Background Tasks:** Telegram bot integration for instant alerts on new borrowings, and scheduled tasks via Django-Q to check and notify about overdue books daily.

---

## Setup & Running (via Docker)

### Prerequisites
Make sure you have **Docker** and **Docker Compose** installed on your machine.

### 1. Clone the repository
```bash
git clone [https://github.com/T0p4ikUA/Library_Service_Project.git](https://github.com/T0p4ikUA/Library_Service_Project.git)
cd Library_Service_Project
```
### 2. Configure environment variables
Create a .env file in the root directory based on the .env.sample template:

```bash
SECRET_KEY=your_django_secret_key
DEBUG=False
POSTGRES_DB=library_db
POSTGRES_USER=library_user
POSTGRES_PASSWORD=library_password
DB_HOST=db
DB_PORT=5432
REDIS_URL=redis://redis:6379/0
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
STRIPE_PUBLISHABLE_KEY=your_stripe_pub_key
STRIPE_SECRET_KEY=your_stripe_secret_key
FINE_MULTIPLIER=2
```
### 3. Run the project with Docker Compose
Build and start all containers in the background:

Bash
docker compose up --build -d
### 4. Run database migrations
Bash
docker compose exec app python manage.py migrate
### 5. Create a superuser (optional, for admin access)
Bash
docker compose exec app python manage.py createsuperuser
### 6. Start Django-Q background worker (for scheduled overdue checks)
Bash
docker compose exec app python manage.py qcluster
### 7. Running Tests
To execute the complete test suite using pytest:

Bash
docker compose exec app pytest
API Documentation
Once the server is running, you can access the interactive API documentation and explore all endpoints via:

Swagger UI: http://127.0.0.1:8000/api/docs/

ReDoc: http://127.0.0.1:8000/api/redoc/

Browsable API: http://127.0.0.1:8000/api/