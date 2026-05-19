#!/bin/bash
set -e

# =============================================================================
# EC2 User Data Script - Allsome Orders Analytics
#
# This script runs on first boot to provision the EC2 instance:
# 1. Updates system packages
# 2. Installs Docker and Docker Compose plugin
# 3. Installs Nginx as a reverse proxy
# 4. Creates application directory and environment file
# =============================================================================

# Update system packages
apt-get update
apt-get upgrade -y

# Detect system architecture for Docker repo
ARCH=$(dpkg --print-architecture)

# Install Docker
apt-get install -y apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=$ARCH signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Start and enable Docker service
systemctl enable docker
systemctl start docker

# Add ubuntu user to docker group for non-root access
usermod -aG docker ubuntu

# Install Nginx as reverse proxy (routes port 80 -> app containers)
apt-get install -y nginx

# Get public IP using IMDSv2 (token-based metadata access)
TOKEN=$(curl -s -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")
PUBLIC_IP=$(curl -s -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/public-ipv4)

# Configure Nginx reverse proxy
cat > /etc/nginx/sites-available/allsome <<EOF
server {
    listen 80;
    server_name _;

    # Frontend (React)
    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }

    # Backend API (Django)
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }

    # Django Admin
    location /admin/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
EOF

ln -sf /etc/nginx/sites-available/allsome /etc/nginx/sites-enabled/default
systemctl restart nginx

# Create app directory
mkdir -p /opt/allsome-orders
cd /opt/allsome-orders

# Create environment file with secure values
cat > .env <<EOF
DB_NAME=allsome_orders
DB_USER=allsome
DB_PASSWORD=${db_password}
DB_HOST=db
DB_PORT=3306
DJANGO_SECRET_KEY=$(openssl rand -base64 48)
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=$PUBLIC_IP,localhost
CORS_ALLOWED_ORIGINS=http://$PUBLIC_IP
REACT_APP_API_URL=http://$PUBLIC_IP/api
EOF

echo "Server provisioning complete. Deploy application with GitHub Actions."
