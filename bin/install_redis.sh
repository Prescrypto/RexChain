# Execute sudo ./install_redis.sh
# Add repository for Redis

# Uncomment this for debian 11
if command -v redis-server --version &>/dev/null; then
    echo "Redis is already installed!"
    sudo systemctl enable redis-server.service
else
    sudo apt-get update
    sudo apt-get install -y redis-server
    echo "Instalation complete"
fi
echo "run redis-cli for test."
