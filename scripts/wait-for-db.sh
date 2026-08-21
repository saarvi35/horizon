#!/bin/sh
set -e

host="$1"
shift

until mysqladmin ping -h"$host" -u"$DB_USER" -p"$DB_PASSWORD" --silent; do
  echo "MySQL ($host) is unavailable - sleeping..."
  sleep 2
done

echo "MySQL ($host) is up and running!"
exec "$@"