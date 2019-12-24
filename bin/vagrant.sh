#!/bin/sh
sudo apt-get update

# Install Pip
echo "*******************************************"
echo "Installing pip"
echo "*******************************************"
sudo apt-get install python-pip

# Install PostgreSQL
# echo "Installing postgresql"
# sudo apt-get install -y libpq-dev postgresql postgresql-contrib libxml2-dev libxslt1-dev zlib1g-dev build-essential libssl-dev libffi-dev
# # Create database if not exist
# psql -U postgres -tc "SELECT 1 FROM pg_database WHERE datname = 'mydb'" | grep -q 1 || psql -U postgres -c "CREATE DATABASE mydb"

# # Create user
# echo "Creating user and granting privileges"
# sudo -i -u postgres psql -c "CREATE USER vagrant WITH PASSWORD 'vagrant';"
# sudo -i -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE mydb TO vagrant;"

# Install Requirements
echo "*******************************************"
echo "Installing from requirements.txt"
echo "*******************************************"
sudo pip install -r /vagrant/requirements.txt

echo "=> Check coverage install..."
sudo python3.6 -m pip install -U coverage
