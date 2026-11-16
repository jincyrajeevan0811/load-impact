import os
import sys
import traceback

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "loadimpact.settings")


def _auto_setup():
    """
    On Render, make sure the database tables, static files and starting content
    exist before the site starts serving. This makes the site work even if the
    Render "Build Command" was not changed to `bash build.sh`.
    Runs once per container; set AUTO_SETUP=0 to switch it off.
    """
    if "RENDER" not in os.environ or os.environ.get("AUTO_SETUP", "1") == "0":
        return

    import fcntl

    import django
    from django.core.management import call_command

    django.setup()
    done_marker = "/tmp/loadimpact-setup.done"
    with open("/tmp/loadimpact-setup.lock", "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)  # only one worker runs the setup
        if os.path.exists(done_marker):
            return
        try:
            print("LoadImpact: preparing database and static files...", flush=True)
            call_command("makemigrations", "accounts", "gym", "appearance", interactive=False, verbosity=1)
            call_command("migrate", interactive=False, verbosity=1)
            call_command("collectstatic", interactive=False, verbosity=0)
            call_command("seed_demo")
            open(done_marker, "w").close()
            print("LoadImpact: setup complete.", flush=True)
        except Exception:
            print("LoadImpact: automatic setup FAILED:", file=sys.stderr, flush=True)
            traceback.print_exc()
            raise


_auto_setup()
application = get_wsgi_application()
