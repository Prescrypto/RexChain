web: sh -c 'cd rexchain && gunicorn rexchain.wsgi:application --timeout 120'
worker: python ./rexchain/manage.py rqworker high default low
