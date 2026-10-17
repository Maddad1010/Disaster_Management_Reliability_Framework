
#!/bin/bash
set -e

apt-get update
apt-get install -y docker.io awscli

systemctl enable docker
systemctl start docker
