# Cendres Vapeur Backend

Backend API for Cendres Vapeur application built with FastAPI and Django ORM.

## Tech Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **Django ORM**: Database models and migrations
- **MySQL**: Database
- **JWT**: Authentication
- **WebSocket**: Real-time communication
- **ReportLab**: PDF invoice generation

## Prerequisites

- Python 3.10+
- MySQL Server
- pip (Python package manager)

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd cendres-vapeur-backend
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure database**
   
   Edit `shared/database.py` with your MySQL credentials:
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.mysql',
           'NAME': 'cendres_vapeur',
           'USER': 'your_mysql_user',
           'PASSWORD': 'your_mysql_password',
           'HOST': 'localhost',
           'PORT': '3306',
       }
   }
   ```

5. **Create database**
   ```sql
   CREATE DATABASE cendres_vapeur CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

6. **Run migrations**
   ```bash
   python manage.py migrate
   ```

## Running the Application

Start the development server:

```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API Base URL**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc

## API Endpoints

### Authentication
- `POST /auth/login` - User login with 2FA
- `POST /auth/verify-2fa` - Verify 2FA code
- `POST /auth/register` - User registration

### Users
- `GET /users` - List all users
- `GET /users/{user_id}` - Get user details
- `PUT /users/{user_id}` - Update user
- `DELETE /users/{user_id}` - Delete user

### Orders
- `GET /orders` - List all orders
- `GET /orders/{order_id}` - Get order details
- `POST /orders` - Create new order
- `PUT /orders/{order_id}` - Update order
- `DELETE /orders/{order_id}` - Delete order

### Products
- `GET /products` - List all products
- `GET /products/{product_id}` - Get product details
- `POST /products` - Create product
- `PUT /products/{product_id}` - Update product
- `DELETE /products/{product_id}` - Delete product

### Categories
- `GET /categories` - List categories
- `POST /categories` - Create category
- `PUT /categories/{category_id}` - Update category
- `DELETE /categories/{category_id}` - Delete category

### Shift Notes
- `GET /shift-notes` - List shift notes
- `GET /shift-notes/{shift_note_id}` - Get shift note
- `POST /shift-notes` - Create shift note
- `PUT /shift-notes/{shift_note_id}` - Update shift note
- `DELETE /shift-notes/{shift_note_id}` - Delete shift note

### Other Endpoints
- `/order-items` - Order items management
- `/colony-events` - Colony events
- `/votes` - Product voting system
- `/logs` - Activity logs
- `/mail` - Email notifications
- `/chat` - WebSocket chat

## Project Structure

```
cendres-vapeur-backend/
├── api/                    # FastAPI routes and business logic
│   ├── crud/              # CRUD operations
│   ├── router/            # API endpoints
│   └── schemas/           # Pydantic models
├── apps/                  # Django application
│   ├── models/            # Database models
│   ├── migrations/        # Database migrations
│   └── classes/           # Utility classes
├── core/                  # Django settings
├── shared/                # Shared utilities
│   ├── database.py        # Database configuration
│   ├── security.py        # JWT authentication
│   ├── mailer.py          # Email service
│   ├── pdf_generator.py   # Invoice PDF generation
│   └── websocket.py       # WebSocket manager
├── invoices/              # Generated invoice PDFs
├── uploads/               # Uploaded files
└── manage.py              # Django management

```

## Authentication

The API uses JWT tokens with 2FA (Two-Factor Authentication):

1. Login with email/password → Receive 2FA code via email (will appear on the back-end console)
2. Verify 2FA code → Receive JWT token
3. Include token in requests: `Authorization: Bearer <token>`

### User Roles

- `ADMIN` - Full access
- `EDITOR` - Can create/edit content
- `USER` - Read-only access

## Database Migrations

Create new migration:
```bash
python manage.py makemigrations
```

Apply migrations:
```bash
python manage.py migrate
```

## Development

### WebSocket Usage

Connect to WebSocket for real-time updates:
```javascript
const ws = new WebSocket('ws://localhost:8000/chat/ws/{user_id}?token={jwt_token}');
```

## Production Deployment

1. Set `DEBUG = False` in `core/settings.py`
2. Change `SECRET_KEY` in `core/settings.py`
3. Use a production-grade server (Gunicorn + Nginx)
4. Set up SSL certificates
5. Configure CORS origins properly

