## EPX Virtual Terminal quick setup

1. Copy the example env file:
   - `cp .env.epx.example .env.epx`
2. Update `.env.epx` values (endpoint and optional API key).
3. Run a dry-run sale request:
   - `python3 epx_virtual_terminal.py sale --amount 10.00 --currency USD --reference ORDER-1 --card-number 4111111111111111 --exp-month 12 --exp-year 2030 --cvv 123 --name "Test User" --zip-code 10001`
4. Send a real request:
   - `python3 epx_virtual_terminal.py --execute sale --amount 10.00 --currency USD --reference ORDER-1 --card-number 4111111111111111 --exp-month 12 --exp-year 2030 --cvv 123 --name "Test User" --zip-code 10001`

`epx_virtual_terminal.py` reads `.env.epx` automatically by default. You can also pass another env file with `--env-file`.
# devasa
