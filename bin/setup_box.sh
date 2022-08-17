#!/usr/bin/env bash

echo "=> Start config box..."
echo "=> Start config box..."
sudo apt-get update
sudo apt-get install -y git
# TODO Check ntpdate on stretch
# sudo apt-get install -y ntpdate
sudo apt-get install -y python3-pip
sudo python3 -m pip install -U pip
sudo python3 -m pip install -U pyOpenSSL
# Install PostgreSQL
echo "Installing postgresql"
sudo apt-get install -y libpq-dev postgresql postgresql-contrib libxml2-dev \
libxslt1-dev zlib1g-dev build-essential libssl-dev libffi-dev
# Create database if not exist
sudo -i -u postgres psql -c "CREATE DATABASE mydb"
sudo -i -u postgres psql -c "CREATE USER vagrant WITH PASSWORD 'vagrant';"
sudo -i -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE mydb TO vagrant;"
sudo -i -u postgres psql -c "ALTER USER vagrant CREATEDB;"

echo "=> Installing requirements..."
sudo python3 -m pip install -r /vagrant/requirements.txt

echo "=> Check flake8 for python lint..."
sudo python3 -m pip install -U flake8

echo "=> End config box..."
