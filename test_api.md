# API Testing Guide

## 🧪 Testing Workflow

### 1. Start Server
```bash
python manage.py runserver
```

### 2. Register Users

**Register Teacher:**
```http
POST http://127.0.0.1:8000/api/users/register/

{
  "username": "john_teacher",
  "email": "john@teacher.com",
  "password": "Teacher@123!",
  "password2": "Teacher@123!",
  "first_name": "John",
  "last_name": "Doe",
  "user_type": "teacher",
  "recovery_question": "What is your favorite color?",
  "recovery_answer": "Blue"
}
```

**Register Student:**
```http
POST http://127.0.0.1:8000/api/users/register/

{
  "username": "alice_student",
  "email": "alice@student.com",
  "password": "Student@123!",
  "password2": "Student@123!",
  "first_name": "Alice",
  "last_name": "Johnson",
  "user_type": "student",
  "recovery_question": "What is your pet's name?",
  "recovery_answer": "Fluffy"
}
```

### 3. Login as Teacher
```http
POST http://127.0.0.1:8000/api/users/login/

{
  "username": "john_teacher",
  "password": "Teacher@123!"
}
```

**Save the access token!**

### 4. Create Category (as Teacher)
```http
POST http://127.0.0.1:8000/api/categories/
Authorization: Bearer <teacher_token>

{
  "name": "Programming",
  "description": "Learn to code",
  "slug": "programming"
}
```

### 5. Create Course (as Teacher)
```http
POST http://127.0.0.1:8000/api/courses/
Authorization: Bearer <teacher_token>

{
  "title": "Python Fundamentals",
  "slug": "python-fundamentals",
  "description": "Complete Python course for beginners",
  "category": 1,
  "difficulty": "beginner",
  "price": 29.99,
  "duration": 20,
  "is_published": true
}
```

### 6. Add Lessons (as Teacher)
```http
POST http://127.0.0.1:8000/api/lessons/
Authorization: Bearer <teacher_token>

{
  "course": 1,
  "title": "Introduction to Python",
  "description": "First lesson",
  "content_type": "video",
  "video_url": "https://youtube.com/watch?v=example",
  "order": 1,
  "duration": 30
}
```

### 7. Login as Student
```http
POST http://127.0.0.1:8000/api/users/login/

{
  "username": "alice_student",
  "password": "Student@123!"
}
```

### 8. Browse Courses (as Student)
```http
GET http://127.0.0.1:8000/api/courses/
```

### 9. Enroll in Course (as Student)
```http
POST http://127.0.0.1:8000/api/courses/python-fundamentals/enroll/
Authorization: Bearer <student_token>
```

### 10. View My Courses (as Student)
```http
GET http://127.0.0.1:8000/api/my-courses/
Authorization: Bearer <student_token>
```

### 11. Complete Lesson (as Student)
```http
POST http://127.0.0.1:8000/api/enrollments/1/complete_lesson/
Authorization: Bearer <student_token>

{
  "lesson_id": 1
}
```

### 12. Check Progress
```http
GET http://127.0.0.1:8000/api/enrollments/1/progress/
Authorization: Bearer <student_token>
```

### 13. Teacher Dashboard (as Teacher)
```http
GET http://127.0.0.1:8000/api/teacher-stats/
Authorization: Bearer <teacher_token>
```

---

## ✅ Expected Results

- ✅ Teachers can create courses and lessons
- ✅ Students can browse and enroll
- ✅ Progress tracking works
- ✅ Permissions are enforced
- ✅ Only course owners can modify