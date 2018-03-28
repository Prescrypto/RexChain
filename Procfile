web: sh -c 'cd prescryptchain && gunicorn prescryptchain.wsgi:application'
worker: python ./prescryptchain/manage.py rqworker high default low
