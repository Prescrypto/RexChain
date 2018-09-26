web: sh -c 'cd rxchain && gunicorn rxchain.wsgi:application'
worker: python ./rxchain/manage.py rqworker high default low
