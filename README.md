# Ehan International Ltd — Step 1

Working foundation: Django + DRF, PostgreSQL, Next.js, organization-scoped service catalog, reviewed recruitment opportunities, public inquiries, and Django admin.

## Requirements
- Windows 10/11 with Docker Desktop and WSL2 integration enabled
- Docker Compose v2
- Free local ports 3000 and 8000

## Windows PowerShell installation

```powershell
cd D:\EhanInternationalLtd
Copy-Item .env.example .env
# IMPORTANT: Edit .env and set long unique DJANGO_SECRET_KEY and POSTGRES_PASSWORD.
# If changing POSTGRES_PASSWORD, update DATABASE_URL as well.
docker compose up --build -d
docker compose ps
docker compose exec backend python manage.py createsuperuser
docker compose exec backend python manage.py seed_demo
```

- Website: http://localhost:3000
- Admin: http://localhost:8000/admin/
- API health: http://localhost:8000/api/v1/health/
- Public services: http://localhost:8000/api/v1/public/ehan-international/services/
- Public opportunities: http://localhost:8000/api/v1/public/ehan-international/opportunities/

## Tests
```powershell
docker compose exec backend python manage.py check
docker compose exec backend python manage.py test core
docker compose logs backend --tail=100
docker compose logs frontend --tail=100
```

## Add a service
Log in as superuser at /admin/, open Services, choose Add, select Ehan International Ltd, set category and Published, save. Reload website (server-rendered data may be cached for up to 60 seconds).

## Add an opportunity
Create an opportunity in Django admin, provide the documented authorization reference, assign a verifying staff user, and mark published only after independent verification. The current Step 1 admin is for a trusted superuser; the complete maker-checker approval workflow is reserved for Step 2.

## IMPORTANT security and scope notes
- Step 1 is a development foundation, **not production ready**. Django admin is restricted to trusted staff; do not expose to customers.
- Public inquiry form includes basic throttling and consent. Production must add spam protection, privacy policy, verified domains, HTTPS, full tenant permissions and retention controls.
- No online payments, real visa applications, or biometric device support are implemented in Step 1.
- Recruitment listings are demonstrations unless independently verified by an authorized agency employee.
- Do not use sample/demo data as an actual recruitment offer.
- Never publish the .env file or real credentials to GitHub.
- This build deliberately does not enable secure cookies because local HTTP development needs access; enforce HTTPS and secure cookies before production.
- Changing Postgres credentials after first initialization requires updating the existing database user password; editing .env alone is insufficient.

## Project structure
- backend/config: Django configuration
- backend/core: organization, memberships, services, opportunities, inquiries, API and tests
- frontend/app: public website and inquiry form
- docker-compose.yml: local application stack

## Steps 2 and 3
Step 2: full enterprise domain models, RBAC, CRM, manpower, travel, tourism, Hajj/Umrah, student, workflow, documents, invoices and contracts.
Step 3: double-entry accounting, HR/payroll, biometric adapters, client portal, advanced CMS, analytics, full hardening, production deployment and QA.

All later steps are delivered as complete file-by-file CREATE/REPLACE manuals, not ZIP-only updates.
