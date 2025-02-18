#!/bin/bash
set -e

# Add custom host entries
echo "127.0.0.1  localhost" >> /etc/hosts
echo "172.17.0.1 host.docker.internal" >> /etc/hosts

# Start the application
exec "$@"
