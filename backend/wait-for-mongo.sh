#!/bin/bash
# wait-for-mongo.sh - Wait for MongoDB to be ready

set -e

host="$1"
shift
cmd="$@"

# Extract host and port
IFS=':' read -ra ADDR <<< "$host"
mongo_host="${ADDR[0]}"
mongo_port="${ADDR[1]:-27017}"

until nc -z "$mongo_host" "$mongo_port"; do
  >&2 echo "MongoDB is unavailable - sleeping"
  sleep 2
done

>&2 echo "MongoDB is up - executing command"
exec $cmd
