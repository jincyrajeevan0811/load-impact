# ---------------------------------------------------------------------------
# PythonAnywhere WSGI file for LoadImpact
#
# Copy everything below into the WSGI configuration file linked on the
# PythonAnywhere "Web" tab (replace its whole contents), then:
#   1. replace YOUR_USERNAME with your PythonAnywhere username (2 places)
#   2. replace the SECRET_KEY value with a long random string
#      (generate one in a Bash console:
#       python -c "import secrets; print(secrets.token_urlsafe(50))")
# ---------------------------------------------------------------------------
import os
import sys

PROJECT_DIR = "/home/YOUR_USERNAME/load-impact"
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

os.environ["DJANGO_SETTINGS_MODULE"] = "loadimpact.settings"
os.environ["DJANGO_DEBUG"] = "False"
os.environ["DJANGO_SECRET_KEY"] = "PASTE-A-LONG-RANDOM-SECRET-KEY-HERE"
os.environ["DJANGO_ALLOWED_HOSTS"] = "YOUR_USERNAME.pythonanywhere.com"

from django.core.wsgi import get_wsgi_application  # noqa: E402

application = get_wsgi_application()
