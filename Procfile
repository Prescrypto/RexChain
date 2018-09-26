web: sh -c 'cd rexchain && gunicorn rexchain.wsgi:application'
worker: python ./rexchain/manage.py rqworker high default low
