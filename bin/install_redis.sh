# Execute sudo ./install_redis.sh
# Add repository for Redis

# Uncomment this for debian 8
echo deb http://ftp.utexas.edu/dotdeb/ stable all > /etc/apt/sources.list.d/dotdeb.list
echo deb-src http://ftp.utexas.edu/dotdeb/ stable all >> /etc/apt/sources.list.d/dotdeb.list

# For debian 7
# echo deb http://packages.dotdeb.org jessie all > /etc/apt/sources.list.d/dotdeb.list
# echo deb-src http://packages.dotdeb.org jessie all >> /etc/apt/sources.list.d/dotdeb.list

cd /tmp/
wget https://www.dotdeb.org/dotdeb.gpg
sudo apt-key add dotdeb.gpg

sudo apt-get update
sudo apt-get install -y redis-server

cd /vagrant/prescryptchain

echo "Instalation complete"
echo "run redis-cli for test."
