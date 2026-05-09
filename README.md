# Tic-Tac-Toe REST API

Django REST API backend for a fully playable Tic-Tac-Toe (Tres en Raya) game.  

---

## Features

- Game state is persisted in database. 
- Player authentication is token-based with JWT.
- API endpoints for game creation, making moves, and retrieving game state.
- Comprehensive unit tests for game logic and API endpoints.

---

## Requirements

- Python 3.12+
- Dependencies listed in `requirements.txt`

```bash
pip install -r requirements.txt
```

---

## Configuration

You can set environment variables and copy `env.template` template file to `.env` final file for local development.
**Attention**: You must set `SECRET_KEY` in `.env` before running the server, with a random string of at least 50 characters between double quotes.

```bash
cp env.template .env
```

---

## Running locally

```bash
cd tictactoe
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

The API is available at `http://localhost:8000/`.

---

## Running with Docker

```bash
docker-compose up --build
```

---

## Running tests

```bash
cd tictactoe
python manage.py test users --verbosity=2
```

---

## Users app

### Password policy

All passwords must meet the following requirements:

| Rule | Detail |
|---|---|
| Minimum length | 10 characters |
| Uppercase | At least one letter A–Z |
| Lowercase | At least one letter a–z |
| Digit | At least one digit 0–9 |
| Special character | At least one of: `@ # % ( ) _ + - .` |
| Forbidden characters | Any character outside letters, digits and the allowed specials is rejected |

Example of a valid password: `Tictactoe1@`

---

### Endpoints

Base URL: `http://localhost:8000/api/v1`

#### Register

```
POST /register/
```

Body:
```json
{ "username": "alice", "password": "Tictactoe1@" }
```

Responses:
- `201 Created` — user created, returns `{ "username": "alice", "token": "<access_token>" }`
- `400 Bad Request` — missing field, password does not meet policy, or username already exists

```bash
curl -X POST http://localhost:8000/api/v1/register/ \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "Tictactoe1@"}'
```

---

#### Login

```
POST /login/
```

Body:
```json
{ "username": "david", "password": "SecurePassword1@" }
```

Responses:
- `200 OK` — returns `{ "access": "<jwt>", "refresh": "<jwt>" }`
- `401 Unauthorized` — invalid credentials

```bash
curl -X POST http://localhost:8000/api/v1/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "david", "password": "SecurePassword1@"}'
```

---

#### Refresh token

```
POST /token/refresh/
```

Body:
```json
{ "refresh": "<refresh_token>" }
```

Responses:
- `200 OK` — returns `{ "access": "<new_jwt>" }`
- `401 Unauthorized` — token invalid or expired

```bash
curl -X POST http://localhost:8000/api/v1/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "<refresh_token>"}'
```

---

#### List users

Requires authentication.

```
GET /users/
```

```bash
curl http://localhost:8000/api/v1/users/ \
  -H "Authorization: Bearer <access_token>"
```

Response `200 OK`:
```json
[
  { "username": "david", "email": "", "roles": ["user"], "is_active": true }
]
```

---

#### User detail

Requires authentication.

```
GET /users/<username>/
```

```bash
curl http://localhost:8000/api/v1/users/david/ \
  -H "Authorization: Bearer <access_token>"
```

Responses:
- `200 OK` — returns user object
- `404 Not Found` — user does not exist

---

### Management commands

These commands are run inside the Django container or dev environment:

```bash
cd tictactoe
```

#### create_roles

Creates the `admin` and `user` groups. Must be run once after the initial migration.

```bash
python manage.py create_roles
```

#### create_user

Creates a user and assigns it a role.

```bash
python manage.py create_user <username> <password> <role>
```

- `role` must be `admin` or `user`
- Raises an error if the username already exists

```bash
python manage.py create_user david SecurePassword1@ admin
python manage.py create_user steve   SecurePassword2# user
```

#### create_admin

Creates the default admin user from environment variables. Intended for automated deployments.

```bash
ADMIN_USERNAME=admin 
ADMIN_PASSWORD=SecurePassword1@ 

python manage.py create_admin
```

If `ADMIN_PASSWORD` is not set the command exits silently without creating any user.

#### change_password

Changes the password of an existing user.

```bash
python manage.py change_password <username> <new_password>
```

```bash
python manage.py change_password david NewSecurePassword1@
```

---

## License

[Apache License 2.0](./LICENSE)
