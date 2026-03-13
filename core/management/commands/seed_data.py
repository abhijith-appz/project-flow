"""
python manage.py seed_data

Creates demo users, a team, tasks, and notifications so you can explore
the app immediately after setting it up.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta


class Command(BaseCommand):
    help = 'Seed the database with demo data for development.'

    def handle(self, *args, **options):
        from accounts.models import User
        from teams.models import Team, TeamMembership, Feedback
        from tasks.models import Task
        from notifications.utils import notify

        self.stdout.write('🌱 Seeding database...')

        # ── Teacher ──────────────────────────────────────────
        teacher, _ = User.objects.get_or_create(
            username='teacher1',
            defaults=dict(
                first_name='Dr. Ravi', last_name='Kumar',
                email='ravi@college.edu',
                role='teacher', department='cs', is_staff=False,
            )
        )
        teacher.set_password('teacher123')
        teacher.save()
        self.stdout.write('  ✅ Teacher: teacher1 / teacher123')

        # ── Students ─────────────────────────────────────────
        students_data = [
            ('arun',  'Arun',  'Kumar',  'arun@college.edu',  '20CS1045'),
            ('john',  'John',  'Stephen','john@college.edu',  '20CS1046'),
            ('ravi',  'Ravi',  'Anand',  'ravi2@college.edu', '20CS1047'),
            ('asha',  'Asha',  'Suresh', 'asha@college.edu',  '20CS1048'),
            ('meera', 'Meera', 'Nair',   'meera@college.edu', '20CS1049'),
        ]
        students = []
        for uname, fn, ln, email, sid in students_data:
            u, _ = User.objects.get_or_create(
                username=uname,
                defaults=dict(
                    first_name=fn, last_name=ln, email=email,
                    role='student', department='cs', student_id=sid,
                )
            )
            u.set_password('student123')
            u.save()
            students.append(u)
        self.stdout.write(f'  ✅ {len(students)} students (password: student123)')

        # ── Team ─────────────────────────────────────────────
        team, created = Team.objects.get_or_create(
            name='Team Alpha',
            defaults=dict(
                project_title='AI Chatbot — NLP Final Year Project',
                description='Building a conversational AI chatbot using NLP techniques.',
                department='cs',
                teacher=teacher,
                leader=students[0],
                status='active',
                github_url='https://github.com/team-alpha/ai-chatbot',
            )
        )
        if created:
            for s in students:
                TeamMembership.objects.get_or_create(team=team, student=s)
        self.stdout.write(f'  ✅ Team: {team.name}')

        # ── Tasks ─────────────────────────────────────────────
        today = date.today()
        tasks_data = [
            ('Design login page wireframe',       students[0], 'high',   'completed', today - timedelta(days=10)),
            ('Integrate OpenAI API',              students[2], 'high',   'completed', today - timedelta(days=5)),
            ('Write unit tests for auth module',  students[0], 'medium', 'overdue',   today - timedelta(days=1)),
            ('Update README documentation',       students[1], 'low',    'in_progress',today + timedelta(days=5)),
            ('Build conversation history feature',students[3], 'medium', 'pending',   today + timedelta(days=7)),
            ('Prepare demo video walkthrough',    students[4], 'low',    'pending',   today + timedelta(days=14)),
            ('Deploy to staging server',          students[0], 'high',   'pending',   today + timedelta(days=10)),
        ]
        for title, assignee, priority, status, deadline in tasks_data:
            Task.objects.get_or_create(
                team=team, title=title,
                defaults=dict(
                    assigned_to=assignee,
                    created_by=students[0],
                    priority=priority,
                    status=status,
                    deadline=deadline,
                    completed_at=timezone.now() if status == 'completed' else None,
                )
            )
        self.stdout.write(f'  ✅ {len(tasks_data)} tasks created')

        # ── Feedback ─────────────────────────────────────────
        Feedback.objects.get_or_create(
            team=team, teacher=teacher,
            defaults=dict(
                feedback_type='general',
                message='Good progress on the frontend. Please improve the API documentation '
                        'and add proper error handling in the backend module before the final submission.',
                rating=4,
            )
        )
        self.stdout.write('  ✅ Feedback added')

        # ── Notifications ─────────────────────────────────────
        for student in students:
            notify(
                recipient=student,
                verb='welcome',
                description=f'Welcome to ProjectFlow, {student.first_name}! You have been added to {team.name}.',
                icon='fa-rocket',
                color='blue',
            )
            notify(
                recipient=student,
                verb='feedback',
                description=f'New feedback from {teacher.get_full_name()} on your project.',
                icon='fa-comment',
                color='blue',
            )
        self.stdout.write('  ✅ Notifications sent')

        self.stdout.write(self.style.SUCCESS('\n🎉 Seed complete! Login credentials:'))
        self.stdout.write('   Teacher  → username: teacher1  / password: teacher123')
        self.stdout.write('   Student  → username: arun      / password: student123')
        self.stdout.write('   (or john, ravi, asha, meera — all use student123)')
