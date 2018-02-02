# !/usr/bin/env bash
# This loads fixtures automatically after deployment of review apps to Heroku

echo "=> Begin  postdeploy..."
# First, apply migrations to the schema
if [ $AUTO_MIGRATE == True ]; then
  echo "=> Loading fixtures..."
  python ./prescryptchain/manage.py migrate
  python ./prescryptchain/manage.py loaddata ./prescryptchain/fixtures/initial_data.json
else
  echo "=> Not apply automatically Migrations!"
fi
