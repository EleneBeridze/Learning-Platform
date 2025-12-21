# Docker Setup Instructions

## 🐳 Prerequisites

Install Docker Desktop:
- Windows: https://docs.docker.com/desktop/install/windows-install/
- Mac: https://docs.docker.com/desktop/install/mac-install/
- Linux: https://docs.docker.com/desktop/install/linux-install/

## 🚀 Quick Start

### 1. Build and Run
```bash
# Build images and start containers
docker-compose up --build

# Or run in detached mode (background)
docker-compose up -d --build
```

### 2. Access the Application
```
http://localhost:8000
```

### 3. Create Superuser
```bash
docker-compose exec web python manage.py createsuperuser
```

### 4. View Logs
```bash
# All services
docker-compose logs -f

# Only web service
docker-compose logs -f web

# Only database
docker-compose logs -f db
```

### 5. Stop Containers
```bash
# Stop
docker-compose stop

# Stop and remove
docker-compose down

# Stop and remove with volumes (⚠️ deletes database)
docker-compose down -v
```

## 🔧 Useful Commands

### Run Migrations
```bash
docker-compose exec web python manage.py migrate
```

### Collect Static Files
```bash
docker-compose exec web python manage.py collectstatic --noinput
```

### Create App
```bash
docker-compose exec web python manage.py startapp newapp
```

### Django Shell
```bash
docker-compose exec web python manage.py shell
```

### Database Shell
```bash
docker-compose exec db psql -U courses_user -d courses_lab_db
```

### View Running Containers
```bash
docker-compose ps
```

### Restart Services
```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart web
```

## 📦 Services

### Web (Django)
- Port: 8000
- Image: Built from Dockerfile
- Depends on: PostgreSQL

### Database (PostgreSQL)
- Port: 5432
- Image: postgres:15-alpine
- Database: courses_lab_db
- User: courses_user
- Password: courses_password_2024

## 🗄️ Volumes

- `postgres_data`: PostgreSQL database data
- `static_volume`: Django static files
- `media_volume`: User uploaded files

## 🔐 Environment Variables

Create `.env` file:
```env
DEBUG=False
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://courses_user:courses_password_2024@db:5432/courses_lab_db
ALLOWED_HOSTS=localhost,127.0.0.1
```

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Check what's using port 8000
netstat -ano | findstr :8000

# Kill process (Windows)
taskkill /PID <PID> /F
```

### Database Connection Error
```bash
# Wait for database to be ready
docker-compose up db
# Then start web
docker-compose up web
```

### Reset Everything
```bash
docker-compose down -v
docker-compose up --build
```

### View Container Details
```bash
docker-compose exec web env
```

## 📊 Production Deployment

For production, update:
1. Change SECRET_KEY
2. Set DEBUG=False
3. Update ALLOWED_HOSTS
4. Use environment variables
5. Enable SSL/HTTPS
6. Use production database credentials
7. Configure proper backup strategy

## 🔄 Development vs Production

### Development (SQLite)
```bash
python manage.py runserver
```

### Production (PostgreSQL + Docker)
```bash
docker-compose up --build
```