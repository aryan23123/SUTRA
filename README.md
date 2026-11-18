# Information Management System

An independent Django project for collecting, organizing, managing, and
retrieving information. It uses the workspace-level `.myenv`; do not create a
separate environment inside this project.

## Current implementation status

The project now includes:

- built-in authentication with registration, login, logout, protected routes,
  and a profile page for editing display name and email
- category and tag management
- record creation, listing, search, filtering, update, detail view, and deletion
- dashboard statistics for record counts and recent updates
- document upload, listing, download, delete, and validation rules for PDF/DOCX/TXT files up to 10 MB
- PDF and Excel exports for filtered record lists
- shared templates and a simple project-level stylesheet

## Run the project

```bash
cd ~/Django/InformationManagementSystem
~/Django/.myenv/bin/python manage.py migrate
~/Django/.myenv/bin/python manage.py runserver
```

Then open the app in the browser at `http://127.0.0.1:8000/`.

For deployment, set `DJANGO_SECRET_KEY` to a stable, private value. Without it,
the app generates a temporary key on startup for local development.

## Load the student demo workspace

Create or log in to the account that should own the demonstration data, replace
`your_username` below with that account's username, and run:

```bash
~/Django/.myenv/bin/python manage.py seed_demo_data --username your_username
```

The command creates ten student-oriented categories, reusable study and career
tags, 21 original fictional records, and eight original TXT reference documents.
It does not create accounts, delete data, or overwrite an existing non-demo
record. Demo records are marked in their descriptions and with the `DEMO DATA`
tag; sample documents identify themselves as demonstration material. Running
the command again reuses its existing content rather than adding duplicates.

The generated files use the existing authenticated document-download flow and
are stored under `media/documents/`. The command does not create official LPU
materials, real resumes, or claims about applications, interviews, or offers.
The record detail page shows its creation and latest-update timestamps; the app
does not currently keep a full edit-by-edit audit log.

Run the project tests with:

```bash
~/Django/.myenv/bin/python manage.py test
```

## INT253 learning map

- **Unit I:** project and app structure, settings, and `manage.py` commands.
- **Unit II:** views, URL patterns, request methods, URL parameters, and errors.
- **Unit III:** templates, DTL, inheritance, debugging, and Django tests.
- **Unit IV:** Django Forms and ModelForms, validation, CSRF, and
  post/redirect/get.
- **Unit V:** SQLite models, relationships, migrations, ORM, Admin, groups, and
  permissions.
- **Unit VI:** built-in authentication, protected views, sessions, and cookies.
