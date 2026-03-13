# ProjectFlow — Student Project Management System

Django backend for a student project management system where 5–6 students form teams and teachers monitor progress.

---

## Project Structure

```
projectflow/
├── manage.py
├── requirements.txt
├── projectflow/          # Django project config
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── accounts/             # Custom user model, auth (login/register/profile)
├── teams/                # Team creation, membership, teacher feedback
├── tasks/                # Task CRUD, assignment, status, comments
├── submissions/          # File uploads, phase management, teacher review
├── notifications/        # In-app notification system
├── core/                 # Home page, dashboards, seed data command
├── templates/            # All Django HTML templates
└── static/               # CSS + JS
    ├── css/main.css
    └── js/main.js
```

---

## Quick Start

### 1. Create and activate a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run migrations

```bash
python manage.py migrate
```

### 4. Create a superuser (for /admin)

```bash
python manage.py createsuperuser
```

### 5. Seed demo data (optional but recommended)

```bash
python manage.py seed_data
```

This creates:
- **Teacher** → `teacher1` / `teacher123`
- **Students** → `arun`, `john`, `ravi`, `asha`, `meera` / `student123`
- A complete team "Team Alpha" with tasks, feedback, and notifications

### 6. Run the development server

```bash
python manage.py runserver
```

Visit **http://127.0.0.1:8000**

---

## User Roles

| Role    | Capabilities |
|---------|-------------|
| Student | Register, create/join teams, manage tasks, submit files, view feedback |
| Teacher | Monitor all teams, review submissions (approve/reject), give feedback |
| Admin   | Full access via `/admin/` Django admin panel |

---

## Key URLs

| URL | Description |
|-----|-------------|
| `/` | Public home page |
| `/accounts/login/` | Login |
| `/accounts/register/` | Student registration |
| `/accounts/register/teacher/` | Teacher registration |
| `/dashboard/` | Auto-redirects to role dashboard |
| `/dashboard/student/` | Student dashboard |
| `/dashboard/teacher/` | Teacher dashboard |
| `/teams/` | Team list / management |
| `/tasks/` | Task list / management |
| `/submissions/` | File submissions |
| `/notifications/` | In-app notifications |
| `/profile/` | User profile |
| `/admin/` | Django admin |

---

## App Overview

### `accounts`
- Custom `User` model extending `AbstractUser`
- Fields: `role`, `student_id`, `department`, `avatar`, `bio`, `github_url`
- Views: login, logout, register (student + teacher), profile view/edit, password change

### `teams`
- `Team` model: name, project title, leader, teacher, status, progress (computed from tasks)
- `TeamMembership`: links students to teams, max 6 per team
- `Feedback`: teacher feedback with rating (1–5) and type
- Views: list, detail, create, join, leave, give feedback

### `tasks`
- `Task` model: title, assigned_to, priority (low/medium/high), status, deadline
- Auto-marks tasks as overdue when deadline passes
- `TaskComment`: threaded comments per task
- Views: list (with status filter), create, detail, update, mark complete, delete

### `submissions`
- `Submission` model: file upload, phase (1/2/3), status (pending/approved/rejected/reviewed), version auto-increment
- File validation: PDF, ZIP, DOCX, PPTX, DOC, TXT (max 50 MB)
- Views: list, create (with drag-and-drop upload UI), review (teacher), download

### `notifications`
- `Notification` model: verb, description, icon, color, is_read
- Context processor injects `unread_notifications` and `unread_count` globally
- Auto-created on: task assignment, team join, submission upload, feedback given, submission reviewed

---

## Production Checklist

- [ ] Set `SECRET_KEY` via environment variable
- [ ] Set `DEBUG = False`
- [ ] Configure PostgreSQL database
- [ ] Configure SMTP email backend
- [ ] Run `python manage.py collectstatic`
- [ ] Serve with Gunicorn behind Nginx
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Set up media file storage (S3 or similar)
