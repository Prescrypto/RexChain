#!/usr/bin/env bash

echo "=> Start config box..."
echo "=> Start config box..."
sudo apt-get update
sudo apt-get install -y git
# TODO Check ntpdate on stretch
# sudo apt-get install -y ntpdate
sudo apt-get install -y python3-pip
sudo python3 -m pip install --break-system-packages -U pip
sudo python3 -m pip install --break-system-packages -U pyOpenSSL
# Install PostgreSQL
echo "Installing postgresql"
sudo apt-get install -y libpq-dev postgresql postgresql-contrib libxml2-dev \
libxslt1-dev zlib1g-dev build-essential libssl-dev libffi-dev
# Create database if not exist
sudo -i -u postgres psql -c "CREATE DATABASE mydb"
sudo -i -u postgres psql -c "CREATE USER vagrant WITH PASSWORD 'vagrant';"
sudo -i -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE mydb TO vagrant;"
sudo -i -u postgres psql -c "ALTER USER vagrant CREATEDB;"

# Fix Git security issue for shared directories
echo "=> Configuring Git safe directories..."
git config --global --add safe.directory /vagrant
git config --global --add safe.directory /vagrant/src/django-4-jet

echo "=> Installing requirements..."
sudo python3 -m pip install --break-system-packages -r /vagrant/requirements.txt

echo "=> Check flake8 for python lint..."
sudo python3 -m pip install --break-system-packages -U flake8

echo "=> End config box..."
