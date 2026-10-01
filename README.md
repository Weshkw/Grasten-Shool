# Grasten Academy

A school website and records system for Grasten Academy, built with Django. The
public site shares news and the fees structure; students sign in to see their
examination results, fee payments and a library matched to their grade; the
school office runs everything else from the Django admin.

## Features

- **Public site** – news, the fees structure as downloadable PDFs, and photo
  galleries of academics, co-curricular activities and ICT.
- **Student pages** – examination results and fee payments with the balance
  still owed for each term, visible only to that student.
- **Library** – past papers, e-books, pictures, videos and links. Students see
  what is recommended for their grade (plus resources for all students) and can
  browse everything; staff see the whole library.
- **Search** – one search box across what the visitor is allowed to see: public
  pages for everyone, the library for signed-in users, and their own results
  and fees for students.
- **School office administration** – students, staff, subjects, terms, fees,
  results, bills, statutory deductions and site content in the Django admin.

## Accounts

Students sign in with their admission number, teachers with their TSC number and
other staff with their national ID number (not case-sensitive). Accounts are
issued by the school office in the admin, which is also where forgotten
passwords are reset; there is no self-service sign-up or reset, so nobody can
claim an account just by knowing someone's admission number. Users change their
own password after signing in. Office staff can manage accounts, but only
superusers can grant privileges or edit other superusers.

## Project layout

| Path | What it holds |
| --- | --- |
| `schoolsystem/models.py` | Accounts, students, staff, terms and fees, results, library and site content |
| `schoolsystem/views.py` | Public pages, student pages, library and search |
| `schoolsystem/admin.py` | The school office's administration screens |
| `templates/` | Shared layout and the sign-in pages |
| `finalgrasten/settings.py` | Settings, all read from environment variables |

## Getting started

Requires Python 3.10 or newer.

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
python manage.py migrate
python manage.py createsuperuser   # asks for an ID number, names and phone number
python manage.py runserver
```

Open http://localhost:8000/admin/ to add students, staff accounts and content,
then visit http://localhost:8000/.

## Configuration

Settings are read from environment variables. With none set, the app runs in
local development mode on SQLite. See [`.env.example`](.env.example) for the
full list, including the `DB_*` variables for MySQL or another database. The app
refuses to start with debug off and no secret key.

## Development

```bash
ruff check .               # lint
ruff format .              # format
python manage.py test      # run the test suite
```

The same checks run on every push through GitHub Actions.
