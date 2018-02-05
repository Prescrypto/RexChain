#!/bin/sh
# Use this when promoting requires a migrations
# Deploy script when promoting needs migrations ==== Only works in production

heroku maintenance:on --app rxchain
heroku run python ./prescryptchain/manage.py migrate --app rxchain
heroku maintenance:off --app rxchain
