#!/usr/bin/env bash

echo "=> Start config box..."
sudo apt-get update
sudo apt-get install -y build-essential libssl-dev wget python-pip python-dev libffi-dev
sudo pip install -U pip

echo "=> Installing requirements..."
sudo pip install -r /vagrant/requirements.txt

echo "=> End config box..."
