#!/bin/bash
set -e

CONFIG="/shared/extenddb.toml"
mkdir -p /etc/extenddb

ADMIN_USER="${EXTENDDB_ADMIN_USER:-admin}"
ADMIN_PASS="${EXTENDDB_ADMIN_PASSWORD:-admin123secret}"

# If already initialized (config exists and DB is reachable), just start
if [ -f "$CONFIG" ] && [ -f "/shared/credentials.env" ]; then
  echo "Already initialized, starting server..."
  extenddb serve --config "$CONFIG"
  exec tail -f /dev/null
fi

# Fresh initialization
INIT_OUTPUT=$(extenddb init \
  --pg-host postgres \
  --pg-port 5432 \
  --pg-user postgres \
  --pg-pass "${PG_PASSWORD:-extenddb-local-dev}" \
  --bind-addr 0.0.0.0 \
  --config "$CONFIG" \
  --overwrite 2>&1)

echo "$INIT_OUTPUT"

# Extract account ID from init output
ACCOUNT_ID=$(echo "$INIT_OUTPUT" | grep "Account ID:" | awk '{print $NF}')
echo "Detected Account ID: $ACCOUNT_ID"

# Start server (daemonizes)
extenddb serve --config "$CONFIG"

# Wait for server to be ready
echo "Waiting for ExtendDB to be ready..."
for i in $(seq 1 30); do
  if curl -sk https://localhost:8000/health > /dev/null 2>&1; then
    echo "ExtendDB is ready."
    break
  fi
  sleep 2
done

# Create IAM user and access key using the CLI
echo "Creating IAM user and access key..."
MANAGE_OUTPUT=$(extenddb manage --config "$CONFIG" --user "$ADMIN_USER" --password "$ADMIN_PASS" \
  create-user --account-id "$ACCOUNT_ID" --user-name "$ADMIN_USER" 2>&1 || true)
echo "$MANAGE_OUTPUT"

# Attach full DynamoDB access policy
POLICY='{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Action":"dynamodb:*","Resource":"*"}]}'
extenddb manage --config "$CONFIG" --user "$ADMIN_USER" --password "$ADMIN_PASS" \
  put-user-policy --account-id "$ACCOUNT_ID" --user-name "$ADMIN_USER" \
  --policy-name DynamoDBFullAccess --policy-document "$POLICY" 2>&1 || true
echo "Policy attached."

KEY_OUTPUT=$(extenddb manage --config "$CONFIG" --user "$ADMIN_USER" --password "$ADMIN_PASS" \
  create-access-key --account-id "$ACCOUNT_ID" --user-name "$ADMIN_USER" 2>&1)
echo "$KEY_OUTPUT"

ACCESS_KEY_ID=$(echo "$KEY_OUTPUT" | jq -r '.access_key_id // empty' 2>/dev/null || true)
SECRET_ACCESS_KEY=$(echo "$KEY_OUTPUT" | jq -r '.secret_access_key // empty' 2>/dev/null || true)

if [ -n "$ACCESS_KEY_ID" ] && [ -n "$SECRET_ACCESS_KEY" ]; then
  echo "Access key created: $ACCESS_KEY_ID"
  cat > /shared/credentials.env <<EOF
AWS_ACCESS_KEY_ID=${ACCESS_KEY_ID}
AWS_SECRET_ACCESS_KEY=${SECRET_ACCESS_KEY}
EOF
  echo "Credentials written to /shared/credentials.env"
else
  echo "WARNING: Could not create access key."
  echo "AWS_ACCESS_KEY_ID=test" > /shared/credentials.env
  echo "AWS_SECRET_ACCESS_KEY=test" >> /shared/credentials.env
fi

# Keep container alive
exec tail -f /dev/null
