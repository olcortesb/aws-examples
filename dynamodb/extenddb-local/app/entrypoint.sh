#!/bin/bash
echo "Waiting for credentials..."
while [ ! -f /shared/credentials.env ]; do sleep 2; done
echo "Credentials available."

# If a script is passed as argument, run it and exit
if [ -n "$1" ]; then
  echo "Running: $1"
  exec python "scripts/${1}.py" "${@:2}"
fi

# Otherwise stay alive for interactive use
echo "App container ready. Use: docker compose exec app python scripts/<script>.py"
exec tail -f /dev/null
