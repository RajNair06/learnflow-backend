# LearnFlow Backend

A Django REST Framework-based goal tracking and progress management system with time tracking, analytics, and automated reminders.

## Features

### Core Functionality
- **Goal Management**: Create, track, and manage learning goals with categories (Primary, Secondary, Minor)
- **Progress Tracking**: Log progress with time tracking (logged hours vs. total hours)
- **User Authentication**: JWT-based authentication with custom user model
- **Tier-based Access**: Free and Premium user tiers with different API rate limits

### Advanced Features
- **Analytics Dashboard**: Weekly and monthly summary views with aggregated time tracking
- **Intelligent Caching**: Performance-optimized with Django's caching framework
- **Automated Reminders**: Celery-based scheduled tasks to remind users about inactive goals
- **Rate Limiting**: Tier-based API throttling (Free: 10/day, Premium: 1000/day)
- **Pagination**: Customizable pagination for list endpoints

## Tech Stack

- **Framework**: Django 5.2.6
- **API**: Django REST Framework
- **Authentication**: SimpleJWT (JWT tokens)
- **Database**: PostgreSQL
- **Task Queue**: Celery with Redis broker
- **Caching**: Django Local Memory Cache
- **Scheduling**: Celery Beat

## Prerequisites

- Python 3.12+
- PostgreSQL
- Redis Server

## Installation

### 1. Clone the repository
```bash
git clone <repository-url>
cd learnflow_backend
```

### 2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install django djangorestframework djangorestframework-simplejwt
pip install psycopg2-binary python-dotenv celery redis django-celery-beat
pip install tabulate  # For benchmark command
```

### 4. Environment Configuration

Create a `.env` file in the project root:

```env
# Django
DJANGO_SECRET_KEY=your-secret-key-here

# PostgreSQL Database
PGDATABASE=your_database_name
PGUSER=your_database_user
PGPASSWORD=your_database_password
PGHOST=localhost
PGPORT=5432
```

### 5. Database Setup

```bash
# Create PostgreSQL database
createdb your_database_name

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### 6. Start Services

#### Terminal 1: Django Server
```bash
python manage.py runserver
```

#### Terminal 2: Celery Worker
```bash
celery -A learnflow_backend worker --loglevel=info
```

#### Terminal 3: Celery Beat Scheduler
```bash
celery -A learnflow_backend beat --loglevel=info
```

## API Endpoints

### Authentication
```
POST   /api/token/              # Obtain JWT token pair
POST   /api/token/refresh/      # Refresh access token
POST   /api/user/               # Register new user
```

### Users
```
GET    /api/users/              # List all usernames
```

### Goals
```
GET    /api/goals/              # List all goals (paginated, filterable)
POST   /api/goals/              # Create new goal
GET    /api/goals/<goalNum>     # Get specific goal (1-indexed)
```

**Query Parameters for GET /api/goals/**
- `category`: Filter by Primary/Secondary/Minor
- `is_complete`: Filter by completion status
- `page`: Page number
- `page_size`: Items per page (max 10)

### Progress
```
GET    /api/goals/<goalNum>/progress/                    # List all progress for a goal
POST   /api/goals/<goalNum>/progress/                    # Create progress entry
GET    /api/goals/<goalNum>/progress/<progressNum>       # Get specific progress
PATCH  /api/goals/<goalNum>/progress/<progressNum>       # Update progress
GET    /api/progress/                                    # List all progress entries
```

### Analytics
```
GET    /api/summary/weekly/              # Weekly summary for all goals
GET    /api/summary/weekly/<goalNum>/    # Weekly summary for specific goal
GET    /api/summary/monthly/             # Monthly summary for all goals
GET    /api/summary/monthly/<goalNum>/   # Monthly summary for specific goal
```

## Models

### CustomUser
- Extends Django's AbstractUser
- Fields: `username`, `email`, `tier` (free/premium)

### Goal
- `goal_name`: Text description
- `user`: Foreign key to CustomUser
- `category`: Primary/Secondary/Minor
- `is_complete`: Boolean status
- `deadline`: Optional date
- `completion_percentage`: Calculated property based on progress

### Progress
- `progress`: Text description
- `goal`: Foreign key to Goal
- `logged_hours`: Duration field
- `total_hours`: Duration field
- `is_complete`: Auto-calculated based on hours
- `percentage_complete`: Calculated property

## Configuration

### Cache Settings
Located in `settings.py`:
```python
MONTHLY_SUMMARY_CACHE_TIMEOUT = 300  # 5 minutes
WEEKLY_SUMMARY_CACHE_TIMEOUT = 300   # 5 minutes
```

### Rate Limiting
- **Free Tier**: 10 requests/day
- **Premium Tier**: 1000 requests/day
- Applied to Progress endpoints

### Pagination
- Default page size: 5
- Max page size: 10
- Configurable via `page_size` query parameter

### Automated Tasks
- **Reminder Emails**: Runs daily at midnight (Asia/Kolkata timezone)
- Sends reminders for goals inactive for 7+ days
- Email backend: Console (development)

## Management Commands

### Benchmark Cache Performance
```bash
python manage.py benchmark_cache --user_id=1
```

Runs 100 requests each for weekly and monthly summaries with and without caching, displaying performance metrics.

## Development

### Project Structure
```
learnflow_backend/
├── core/                          # Main application
│   ├── management/commands/       # Custom Django commands
│   ├── migrations/                # Database migrations
│   ├── admin.py                   # Admin interface config
│   ├── models.py                  # Database models
│   ├── serializers.py             # DRF serializers
│   ├── views.py                   # API views
│   ├── urls.py                    # App URL routing
│   ├── tasks.py                   # Celery tasks
│   ├── throttling.py              # Custom throttling
│   └── pagination.py              # Custom pagination
├── learnflow_backend/             # Project settings
│   ├── settings.py                # Django settings
│   ├── urls.py                    # Root URL config
│   ├── celery.py                  # Celery configuration
│   └── wsgi.py                    # WSGI config
└── manage.py                      # Django management script
```

### Logging
- Cache hits/misses logged to `caches.log`
- Console logging for cache misses only
- Celery task logging to console and file

## API Usage Examples

### Register User
```bash
curl -X POST http://localhost:8000/api/user/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "secure_password",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "tier": "free"
  }'
```

### Obtain JWT Token
```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "secure_password"
  }'
```

### Create Goal
```bash
curl -X POST http://localhost:8000/api/goals/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_access_token>" \
  -d '{
    "goal_name": "Learn Django REST Framework",
    "category": "Primary",
    "deadline": "2025-12-31"
  }'
```

### Log Progress
```bash
curl -X POST http://localhost:8000/api/goals/1/progress/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_access_token>" \
  -d '{
    "progress": "Completed authentication module",
    "logged_hours": "02:30:00",
    "total_hours": "05:00:00"
  }'
```

### Get Weekly Summary
```bash
curl -X GET http://localhost:8000/api/summary/weekly/ \
  -H "Authorization: Bearer <your_access_token>"
```

## Performance Features

### Caching Strategy
- Weekly and monthly summaries are cached for 5 minutes
- Cache keys include user ID and goal number
- Automatic cache invalidation on timeout
- Benchmark command to measure cache effectiveness

### Database Optimization
- Indexed foreign keys
- Efficient querysets with `select_related()` and `prefetch_related()`
- Aggregation queries for summary views

## Security

- JWT-based authentication
- CSRF protection enabled
- Password validation enforced
- User-specific data isolation
- Rate limiting to prevent abuse

## Production Considerations

### Before Deployment
1. Set `DEBUG = False` in settings.py
2. Configure `ALLOWED_HOSTS` properly
3. Use environment variables for all secrets
4. Switch from SQLite to PostgreSQL (already configured)
5. Configure proper email backend (currently console)
6. Set up Redis for production
7. Use proper WSGI server (Gunicorn/uWSGI)
8. Configure static file serving
9. Set up SSL/TLS certificates
10. Implement proper logging and monitoring

### Recommended Production Settings
```python
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com']
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

## Troubleshooting

### Common Issues

**Celery tasks not running:**
- Ensure Redis is running: `redis-cli ping`
- Check Celery worker is active
- Verify Celery Beat is running

**Database connection errors:**
- Verify PostgreSQL is running
- Check .env credentials
- Ensure database exists

**Authentication fails:**
- Check JWT token is not expired
- Verify token is in Authorization header as `Bearer <token>`



## Support

For issues and questions, please open an issue on the repository.