"""
WSGI config for college_permission_system project.
Auto-runs migrations on cold start (safe for Vercel serverless).
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'college_permission_system.settings')

# ── Auto-migrate on cold start (Vercel serverless) ──
# This runs `manage.py migrate` the first time each serverless instance starts.
# It is a no-op if migrations are already applied (idempotent).
try:
    from django.core.management import call_command
    call_command('migrate', '--run-syncdb', verbosity=0)
except Exception as e:
    import sys
    print(f"[WSGI] Migration skipped: {e}", file=sys.stderr)

application = get_wsgi_application()
