# Gunicorn settings (loaded automatically by `gunicorn loadimpact.wsgi`).
# The first start on Render runs migrations/collectstatic, so allow more time.
timeout = 120
accesslog = "-"
errorlog = "-"
