# LearnFlow Backend

A Django REST Framework-based goal tracking and progress management system with time tracking, analytics, and automated reminders.

## Features

### Core Functionality
- **Goal Management**: Create, track, and manage learning goals with categories (Primary, Secondary, Minor)
- **Progress Tracking**: Log progress with time tracking (logged hours vs. total hours)
- **User Authentication**: JWT-based authentication with custom user model
- **Tier-based Access**: Free and Premium user tiers with different API rate limits

### Advanced Features
- **Summary**: Weekly and monthly summary views with aggregated time tracking
- **Intelligent Caching**: Performance-optimized with Redis caching
- **Automated Reminders**: Celery-based scheduled tasks to remind users about inactive goals
- **Rate Limiting**: Tier-based API throttling (Free: 10/day, Premium: 1000/day)
- **Pagination**: Customizable pagination for list endpoints
- **Containerized**: Docker & Docker Compose for easy local development and deployment

## Tech Stack

- **Framework**: Django 5.2.6
- **API**: Django REST Framework
- **Authentication**: SimpleJWT (JWT tokens)
- **Database**: PostgreSQL
- **Task Queue**: Celery with Redis broker
- **Caching**: Redis
- **Scheduling**: Celery Beat
- **Web Server**: Gunicorn
- **Containerization**: Docker & Docker Compose

## Prerequisites

- Docker & Docker Compose (recommended for easy setup)
- OR Python 3.12+, PostgreSQL, and Redis (for manual setup)

## Quick Start with Docker (Recommended)

### 1. Clone the repository
```bash
git clone <repository-url>
cd learnflow_backend
```

### 2. Create environment file
```bash
cp .env.example .env
# Edit .env with your configuration
```

### 3. Start all services
```bash
docker-compose up -d
```

This will start:
- **Web**: Django API on `http://localhost:8000`
- **PostgreSQL**: Database (configure in .env)
- **Redis**: Cache & message broker
- **Celery Worker**: Background task processor
- **Celery Beat**: Scheduled task scheduler

### 4. Run migrations
```bash
docker-compose exec web python manage.py migrate
```

### 5. Create superuser (optional)
```bash
docker-compose exec web python manage.py createsuperuser
```

### 6. Access the API
```bash
curl http://localhost:8000/api/goals/
```

## Manual Setup (Without Docker)

### 1. Clone and setup environment
```bash
git clone <repository-url>
cd learnflow_backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration

Create a `.env` file in the project root:

```env
# Django
DJANGO_SECRET_KEY=your-secret-key-here
DEBUG=True

# PostgreSQL Database
DATABASE_URL=postgresql://user:password@localhost:5432/learnflow

# Redis
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Email (development)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

### 4. Database Setup

```bash
# Ensure PostgreSQL is running and create database
createdb learnflow

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### 5. Start Services

**Terminal 1: Django Server**
```bash
python manage.py runserver
```

**Terminal 2: Celery Worker**
```bash
celery -A learnflow_backend worker --loglevel=info
```

**Terminal 3: Celery Beat Scheduler**
```bash
celery -A learnflow_backend beat --loglevel=info
```

**Terminal 4: Redis (if not running as service)**
```bash
redis-server
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
# With Docker
docker-compose exec web python manage.py benchmark_cache --user_id=1

# Without Docker
python manage.py benchmark_cache --user_id=1
```

Runs 100 requests each for weekly and monthly summaries with and without caching, displaying performance metrics.

## Docker Compose Services

### Web Service
- Runs Gunicorn on port 8000
- Auto-reloads on code changes (mounted volume)
- Depends on Redis health check

### Redis Service
- Acts as cache and Celery message broker
- Data persisted to `redis_data` volume
- Health check ensures availability

### Celery Worker Service
- Processes background tasks
- Depends on Redis
- Logs to console at INFO level

### Celery Beat Service
- Runs scheduled tasks (e.g., reminder emails)
- Depends on Redis
- Single instance (don't scale without coordination)

### Database
Configure in `.env` using `DATABASE_URL`:
```
DATABASE_URL=postgresql://user:password@host:5432/dbname
```

## Development

### Project Structure
```
learnflow_backend/
├── core/                          # Main application
│   ├── management/commands/       # Custom Django commands
│   │   └── benchmark_cache.py     # Cache performance testing
│   ├── migrations/                # Database migrations
│   ├── admin.py                   # Admin interface config
│   ├── apps.py                    # App configuration
│   ├── models.py                  # Database models
│   ├── serializers.py             # DRF serializers
│   ├── views.py                   # API views
│   ├── urls.py                    # App URL routing
│   ├── tasks.py                   # Celery background tasks
│   ├── throttling.py              # Custom rate limiting
│   ├── pagination.py              # Custom pagination
│   └── tests.py                   # Unit tests
├── learnflow_backend/             # Project settings
│   ├── settings.py                # Django settings
│   ├── urls.py                    # Root URL config
│   ├── celery.py                  # Celery configuration
│   ├── asgi.py                    # ASGI config
│   └── wsgi.py                    # WSGI config
├── Dockerfile                     # Multi-stage Docker build
├── docker-compose.yml             # Docker Compose configuration
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment variables template
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
- Weekly and monthly summaries cached in Redis for 5 minutes
- Cache keys include user ID and goal number
- Automatic cache invalidation on timeout
- Benchmark command to measure cache effectiveness

### Database Optimization
- Indexed foreign keys
- Efficient querysets with `select_related()` and `prefetch_related()`
- Aggregation queries for summary views

## Docker Commands

### View logs
```bash
docker-compose logs -f web          # Django logs
docker-compose logs -f celery       # Celery worker logs
docker-compose logs -f celery-beat  # Celery Beat logs
docker-compose logs -f redis        # Redis logs
```

### Execute Django commands
```bash
docker-compose exec web python manage.py <command>
```

### Stop services
```bash
docker-compose down
```

### Rebuild images (if Dockerfile changes)
```bash
docker-compose build --no-cache
docker-compose up -d
```



## Security

- JWT-based authentication
- CSRF protection enabled
- Password validation enforced
- User-specific data isolation
- Rate limiting to prevent abuse
- Non-root user in Docker container
- Environment variables for all secrets

## Production Considerations

### Before Production Deployment
1. Set `DEBUG = False` in settings.py
2. Configure `ALLOWED_HOSTS` with your domain
3. Use strong `DJANGO_SECRET_KEY`
4. Configure proper email backend (SMTP)
5. Set up SSL/TLS certificates
6. Use managed database (AWS RDS, Heroku Postgres, etc.)
7. Use managed Redis or dedicated instance
8. Scale Celery workers based on load
9. Set up monitoring and alerting
10. Configure log aggregation

### Recommended Production Settings
```python
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
```

### Production Docker Deployment
```bash
# Use environment-specific docker-compose
docker-compose -f docker-compose.prod.yml up -d

# Scale Celery workers
docker-compose -f docker-compose.prod.yml up -d --scale celery=3
```

## Troubleshooting

### Common Issues

**Docker services failing to start:**
- Check Docker daemon is running
- Verify ports 8000, 6379 are available
- Review logs: `docker-compose logs -f`

**Celery tasks not running:**
- Ensure Redis container is healthy: `docker-compose ps`
- Check Celery worker logs: `docker-compose logs celery`
- Verify Celery Beat is running: `docker-compose logs celery-beat`

**Database connection errors:**
- Verify DATABASE_URL in .env
- Check PostgreSQL container/service is running
- Ensure database migrations completed

**Authentication fails:**
- Check JWT token is not expired
- Verify token format: `Bearer <token>`
- Confirm user exists in database

**Redis connection errors:**
- Verify Redis container is healthy
- Check CELERY_BROKER_URL in .env
- Run `docker-compose restart redis`

## Support

For issues and questions, please open an issue on the repository.