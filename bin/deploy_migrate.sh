#!/bin/sh
# Use this when promoting requires a migrations
# Deploy script when promoting needs migrations ==== Only works in production

heroku maintenance:on --app rexchain
heroku scale worker=0 --app rexchain
heroku run python ./rexchain/manage.py migrate --app rexchain
heroku scale worker=1 --app rexchain
heroku maintenance:off --app rexchain
