#!/usr/bin/env bash
# =============================================================================
# Django Auth database initialisation — executed once by the MariaDB entrypoint
# on the first start (when the data directory is empty).
# =============================================================================
set -euo pipefail

: "${MYSQL_DATABASE:?MYSQL_DATABASE is not set}"
: "${MYSQL_USER:?MYSQL_USER is not set}"

mariadb -u root -p"${MYSQL_ROOT_PASSWORD}" <<-EOSQL
    ALTER DATABASE \`${MYSQL_DATABASE}\` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
    GRANT ALL PRIVILEGES ON \`${MYSQL_DATABASE}\`.* TO '${MYSQL_USER}'@'%';
    CREATE DATABASE IF NOT EXISTS \`test_${MYSQL_DATABASE}\` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
    GRANT ALL PRIVILEGES ON \`test_${MYSQL_DATABASE}\`.* TO '${MYSQL_USER}'@'%';
    FLUSH PRIVILEGES;
EOSQL

echo "[init] Database '${MYSQL_DATABASE}' configured (utf8mb4)."
