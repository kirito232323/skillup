# SkillUp Django Conversion

This workspace now includes a Django version of the existing SkillUp PHP app.

## Setup

1. Create and activate a virtual environment:

```bash
python -m venv venv
venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run migrations:

```bash
python manage.py migrate
```

4. Create a superuser:

```bash
python manage.py createsuperuser
```

5. Start the development server:

```bash
python manage.py runserver
```

## URLs

- `/` — login and dashboard page
- `/login.php` — login API
- `/logout.php` — logout redirect
- `/session.php` — session status API
- `/api/get_dashboard_stats.php` — dashboard stats API
- `/api/get_recommendations.php` — recommendations API
- `/api/get_skill_gaps.php` — skill gap API
- `/api/get_trainees.php` — trainee list API
- `/api/get_user_skills.php` — user skills API

## Notes

- The original page structure and API routes are preserved so the frontend HTML and JavaScript can remain unchanged.
- The project uses SQLite by default; you can adjust `skillup/settings.py` to use MySQL if needed.
