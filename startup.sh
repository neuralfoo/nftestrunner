export MACHINE_ID=alpha
export PUBLIC_URL=http://neuralfoo.com
gunicorn --bind 0.0.0.0:50001  --timeout 10000 --reload --workers 2  app:app
