# Courses Lab - API Endpoints

## Base URL
```
http://127.0.0.1:8000/api/
```

---

## 📚 CATEGORIES

### List Categories
```http
GET /categories/
```

### Create Category (Teacher only)
```http
POST /categories/
Authorization: Bearer <token>

{
  "name": "Programming",
  "description": "Learn to code",
  "slug": "programming"
}
```

### Get Category Courses
```http
GET /categories/{slug}/courses/
```

---

## 📖 COURSES

### List All Courses
```http
GET /courses/
```

**Query Parameters:**
- `?category=programming` - Filter by category slug
- `?difficulty=beginner` - Filter by difficulty (beginner/intermediate/advanced)
- `?free=true` - Show only free courses
- `?my_courses=true` - Teacher's own courses (requires auth)
- `?search=python` - Search in title/description
- `?ordering=-created_at` - Sort by field

### Get Course Details
```http
GET /courses/{slug}/
```

### Create Course (Teacher only)
```http
POST /courses/
Authorization: Bearer <token>

{
  "title": "Python for Beginners",
  "slug": "python-for-beginners",
  "description": "Learn Python from scratch",
  "category": 1,
  "difficulty": "beginner",
  "price": 29.99,
  "duration": 20,
  "is_published": true
}
```

### Update Course (Teacher only)
```http
PUT /courses/{slug}/
Authorization: Bearer <token>

{
  "title": "Updated Title",
  "price": 39.99,
  "is_published": true
}
```

### Delete Course (Teacher only)
```http
DELETE /courses/{slug}/
Authorization: Bearer <token>
```

### Get Course Lessons
```http
GET /courses/{slug}/lessons/
Authorization: Bearer <token> (optional)
```

### Enroll in Course (Student only)
```http
POST /courses/{slug}/enroll/
Authorization: Bearer <token>
```

### Check Enrollment Status
```http
GET /courses/{slug}/enrollment_status/
Authorization: Bearer <token>
```

---

## 📝 LESSONS

### List Lessons
```http
GET /lessons/?course={course_slug}
Authorization: Bearer <token>
```

### Create Lesson (Teacher only)
```http
POST /lessons/
Authorization: Bearer <token>

{
  "course": 1,
  "title": "Introduction to Python",
  "description": "First lesson",
  "content_type": "video",
  "video_url": "https://youtube.com/watch?v=xyz",
  "content": "Lesson content here",
  "order": 1,
  "duration": 30
}
```

### Update Lesson (Teacher only)
```http
PUT /lessons/{id}/
Authorization: Bearer <token>

{
  "title": "Updated Lesson Title",
  "duration": 45
}
```

### Delete Lesson (Teacher only)
```http
DELETE /lessons/{id}/
Authorization: Bearer <token>
```

---

## 🎓 ENROLLMENTS

### My Enrollments (Student)
```http
GET /enrollments/
Authorization: Bearer <token>
```

### Get Enrollment Details
```http
GET /enrollments/{id}/
Authorization: Bearer <token>
```

### Get Enrollment Progress
```http
GET /enrollments/{id}/progress/
Authorization: Bearer <token>
```

### Mark Lesson Complete
```http
POST /enrollments/{id}/complete_lesson/
Authorization: Bearer <token>

{
  "lesson_id": 5
}
```

---

## 👨‍🎓 STUDENT ENDPOINTS

### My Courses
```http
GET /my-courses/
Authorization: Bearer <token>
```

---

## 👨‍🏫 TEACHER ENDPOINTS

### Teacher Courses
```http
GET /teacher-courses/
Authorization: Bearer <token>
```

### Teacher Statistics
```http
GET /teacher-stats/
Authorization: Bearer <token>
```

**Response:**
```json
{
  "total_courses": 5,
  "published_courses": 3,
  "total_students": 120,
  "total_enrollments": 250
}
```

---

## ✅ Success Responses

### Course Created
```json
{
  "id": 1,
  "title": "Python for Beginners",
  "slug": "python-for-beginners",
  "teacher": {...},
  "category": {...},
  "lessons_count": 0,
  "enrolled_students_count": 0,
  "is_enrolled": false
}
```

### Enrolled Successfully
```json
{
  "message": "Enrolled successfully",
  "enrollment": {
    "id": 1,
    "student": {...},
    "course": {...},
    "progress_percentage": 0,
    "enrolled_at": "2024-12-20T10:00:00Z"
  }
}
```

### Lesson Completed
```json
{
  "message": "Lesson marked as complete",
  "progress": {
    "id": 1,
    "lesson": {...},
    "completed": true,
    "completed_at": "2024-12-20T10:30:00Z"
  },
  "enrollment_progress": 20
}
```

---

## ❌ Error Responses

### 400 Bad Request
```json
{
  "error": "You are already enrolled in this course"
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
  "detail": "Only teachers can create courses."
}
```

### 404 Not Found
```json
{
  "detail": "Not found."
}
```