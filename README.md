# Courses Lab - Online Learning Platform

Backend learning platform built with Django REST Framework.

## 🚀 Features

- User Authentication (JWT)
- Role-based Access (Teacher/Student)
- Course Management
- Lesson Management
- Enrollment System
- Progress Tracking
- Password Recovery

## 🛠️ Tech Stack

- Django 5.0
- Django REST Framework
- PostgreSQL
- Docker
- JWT Authentication

## 📦 Installation

### Option 1: Local Development (SQLite)
```bash
# Clone repository
git clone https://github.com/EleneBeridze/Learning-Platform.git
cd Courses_Lab

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run server
python manage.py runserver
```

### Option 2: Docker (PostgreSQL)
```bash
# Build and run
docker-compose up --build

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Access at http://localhost:8000
```

## 📚 API Documentation

See [API_ENDPOINTS.md](API_ENDPOINTS.md) for complete API documentation.

## 🐳 Docker

See [DOCKER_INSTRUCTIONS.md](DOCKER_INSTRUCTIONS.md) for Docker setup guide.

## 🧪 Testing

See [test_api.md](test_api.md) for API testing guide.

## 📁 Project Structure
```
Courses_Lab/
├── config/              # Settings
├── users/               # User app
├── courses/             # Courses app
├── media/               # Uploads
├── staticfiles/         # Static files
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## 👨‍💻 Author

Elene Beridze - [GitHub](https://github.com/EleneBeridze)

## 📄 License

MIT License