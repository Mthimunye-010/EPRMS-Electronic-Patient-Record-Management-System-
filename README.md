# Electronic Patient Record Management System (EPRMS)

A Django + PostgreSQL web application for managing patient records at South
African public hospitals, built for the mini-project by **Mfundo Mthimunye**.

This implements the scope described in the project proposal:

- Patient registration and information management
- Patient record searching
- **Duplicate patient detection** (by SA ID number, and by name + date of
  birth as a fallback for mistyped ID numbers)
- Medical history management
- Recording of doctor/nurse consultations
- Medication tracking
- Appointment scheduling and status tracking
- Staff login with **role-based access control** (Administrator, Doctor,
  Nurse, Receptionist)
- **Audit logging** of logins, logouts, record creation/updates, searches,
  and duplicate-detection events
- A PostgreSQL-backed database with a backup script

## Project layout

```
epr_system/
├── config/          # Django project settings, root URLs
├── accounts/        # Custom staff User model, roles, login, staff management
├── core/             # Dashboard/home page
├── patients/         # Patient model, registration, search, duplicate detection
├── records/           # Medical history, consultations, medications, appointments
├── audit/             # Audit log model, middleware, and viewer (admin only)
├── templates/         # HTML templates (Bootstrap 5 styling)
├── static/             # CSS
├── scripts/backup_db.sh # PostgreSQL backup helper
└── requirements.txt
```

## 1. Prerequisites

- Python 3.11+
- PostgreSQL 14+ (running locally or accessible remotely)

## 2. Setup

```bash
# From the epr_system/ folder
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create the PostgreSQL database and user (run in `psql` or a GUI like
pgAdmin):

```sql
CREATE DATABASE eprms_db;
CREATE USER eprms_user WITH PASSWORD 'eprms_password';
GRANT ALL PRIVILEGES ON DATABASE eprms_db TO eprms_user;
```

Copy `.env.example` to `.env` and adjust values as needed, then export them
(or use a tool like `django-environ`/`python-decouple` to load `.env`
automatically):

```bash
cp .env.example .env
export $(cat .env | xargs)      # quick way to load the vars in bash
```

> **Quick start without PostgreSQL:** set `DJANGO_DB_ENGINE=sqlite` to run
> against a local SQLite file instead — handy for a first look at the app
> before setting up Postgres.

## 3. Run migrations and create an admin account

```bash
python3 manage.py migrate
python3 manage.py createsuperuser
```

Or, to quickly populate the database with realistic **synthetic test data**
(staff accounts + patients + records) for demoing or testing:

```bash
python3 manage.py seed_demo_data --patients 20
```

This creates four demo logins (password `DemoPass123!` for all):

| Username        | Role          |
|-----------------|---------------|
| `admin_demo`    | Administrator |
| `dr_ndlovu`     | Doctor        |
| `nurse_maseko`  | Nurse         |
| `reception_v`   | Receptionist  |

## 4. Run the development server

```bash
python3 manage.py runserver
```

Visit `http://127.0.0.1:8000/` and log in.

## 5. Running the automated tests

```bash
python3 manage.py test
```

The test suite (14 tests) covers: duplicate-detection logic, role-based
access control on key views, and audit-log creation on login and patient
registration.

## 6. Database backups

```bash
./scripts/backup_db.sh
```

Dumps the PostgreSQL database to `backups/eprms_backup_<timestamp>.sql`
using `pg_dump`, keeping the 14 most recent backups. Restore with:

```bash
pg_restore -h localhost -U eprms_user -d eprms_db backups/eprms_backup_YYYYMMDD_HHMMSS.sql
```

Consider scheduling this script via `cron` for automatic daily backups in a
real deployment.

## Roles and permissions

| Action                          | Receptionist | Nurse | Doctor | Administrator |
|----------------------------------|:---:|:---:|:---:|:---:|
| Register / edit patient          | ✅  |     |     | ✅  |
| Search / view patient records    | ✅  | ✅  | ✅  | ✅  |
| Add medical history / consultation / medication | | ✅ | ✅ | ✅ |
| Schedule appointments            | ✅  | ✅  | ✅  | ✅  |
| Manage staff accounts            |     |     |     | ✅  |
| View audit log                   |     |     |     | ✅  |

## Notes on the duplicate-detection feature

When registering a new patient, `Patient.find_potential_duplicates()` checks:

1. **Exact SA ID number match** — blocked outright by the database's unique
   constraint (two patients cannot share an ID number).
2. **Matching first name + last name + date of birth, with a different ID**
   — flagged as a *possible* duplicate (e.g. a mistyped ID number). The
   receptionist is shown the matching record(s) and can either open the
   existing record or confirm that this is genuinely a new, distinct
   patient before proceeding.

Every duplicate flag and every patient registration is written to the audit
log for traceability.

## Next steps / what to extend

This is a working first implementation of the scope. Natural follow-ups
before a production rollout: password-reset flow, HTTPS/session hardening
for deployment, pagination on the patient list for large hospitals, and
exporting patient summaries to PDF.

## Security and privacy controls

This version applies privacy-by-design principles for a healthcare student project:

- Least-privilege role checks are enforced server-side; Administrator no longer bypasses every role restriction.
- Receptionists do not receive clinical notes, diagnoses, medication records or full SA ID numbers.
- SA ID numbers are not shown in patient lists or used as general patient-directory search terms.
- Patient administrative editing is limited to contact/next-of-kin information.
- Doctors create consultations and medication records; nurses can add medical history but cannot create diagnoses or prescriptions.
- Clinical records use protected relationships so a patient cannot be casually deleted together with their history.
- Audit logs do not store patient names in their target representation and cannot be changed or deleted through Django admin.
- Login is blocked for disabled staff accounts.
- Sessions use a 15-minute timeout and an inactivity timeout for unattended workstations.
- Production settings support secure cookies, HTTPS redirect and HSTS when DEBUG=False.
- A Privacy & Security page explains confidentiality and acceptable use.

These controls are intended for the university project and are not a claim of legal POPIA compliance or production clinical certification.
