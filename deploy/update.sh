#!/bin/bash
# Pull the latest code from GitHub and apply it on PythonAnywhere.
# Run in a PythonAnywhere Bash console:   bash ~/load-impact/deploy/update.sh
# Then press "Reload" on the Web tab.
set -e
cd ~/load-impact
git pull
source ~/.virtualenvs/loadimpact-env/bin/activate
pip install -q -r requirements.txt
python manage.py makemigrations accounts gym appearance
python manage.py migrate
python manage.py collectstatic --noinput
echo ""
echo "Done. Now open the Web tab on PythonAnywhere and click the green Reload button."
