# Tic-Tac-Toe REST API

Django REST API backend for a fully playable Tic-Tac-Toe (Tres en Raya) game with MySQL database persistence, JWT authentication, and player score tracking.

---

## Features

- Full Tic-Tac-Toe game logic: turn validation, win detection (rows, columns, diagonals), draw detection.
- Game state persisted in database (MySQL) — no state lost on server restart.
- JWT authentication with access + refresh tokens.
- Player score tracking: wins, losses, draws, total games.
- Brute-force protection on login via `django-axes`.
- Comprehensive unit tests for game logic and all API endpoints.
- Structured logging to stdout.

---

## Requirements

- Docker and Docker Compose

---

## Running with Docker Compose

```bash
cp .env.template .env   # fill in DB credentials and SECRET_KEY
docker compose build
docker compose up -d
docker compose logs -f
```

The API is available at `http://localhost:8000/api/v1/`.

---

## Running locally (devcontainer)

Open the project in VS Code and reopen in container. Then in the integrated terminal:

```bash
cd /app/tictactoe
python manage.py migrate
python manage.py create_roles
python manage.py runserver 0.0.0.0:8000
```

---

## Running tests

```bash
# Users app
python manage.py test users --verbosity=2

# Game app
python manage.py test game --verbosity=2

# All
python manage.py test users game --verbosity=2
```

---

## Password policy

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

## API Reference

Base URL: `http://localhost:8000/api/v1`

All endpoints that require authentication expect the header:
```
Authorization: Bearer <access_token>
```

---

### Auth

#### Register

```
POST /register/
```

```bash
curl -s -X POST http://localhost:8000/api/v1/register/ \
  -H "Content-Type: application/json" \
  -d '{"username": "david", "password": "Tictactoe1@"}'
```

Response `201 Created`:
```json
{ "access": "<jwt>", "refresh": "<jwt>" }
```

Errors:
- `400` — missing field, weak password, or username already taken

---

#### Login

```
POST /login/
```

```bash
curl -s -X POST http://localhost:8000/api/v1/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "david", "password": "Tictactoe1@"}'
```

Response `200 OK`:
```json
{ "access": "<jwt>", "refresh": "<jwt>" }
```

Errors:
- `401` — invalid credentials

---

#### Refresh token

When the `access` token expires (15 minutes), use the `refresh` token to get a new one without logging in again.

```
POST /token/refresh/
```

```bash
curl -s -X POST http://localhost:8000/api/v1/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "<refresh_token>"}'
```

Response `200 OK`:
```json
{ "access": "<new_jwt>" }
```

Errors:
- `401` — refresh token invalid or expired (requires new login)

---

### Users

#### List users

```
GET /users/
```

```bash
curl -s http://localhost:8000/api/v1/users/ \
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

```
GET /users/<username>/
```

```bash
curl -s http://localhost:8000/api/v1/users/david/ \
  -H "Authorization: Bearer <access_token>"
```

Errors:
- `404` — user not found

---

### Players (scores)

#### Ranking

```
GET /players/
```

Returns all players ordered by wins descending.

```bash
curl -s http://localhost:8000/api/v1/players/ \
  -H "Authorization: Bearer <access_token>"
```

Response `200 OK`:
```json
[
  { "id": 1, "username": "david", "wins": 3, "losses": 1, "draws": 0, "total_games": 4 }
]
```

---

#### Player detail

```
GET /players/<username>/
```

```bash
curl -s http://localhost:8000/api/v1/players/david/ \
  -H "Authorization: Bearer <access_token>"
```

Errors:
- `404` — player not found

---

### Game

The board positions are numbered 0–8:

```
 0 | 1 | 2
-----------
 3 | 4 | 5
-----------
 6 | 7 | 8
```

#### Create a game

```
POST /games/
```

```bash
curl -s -X POST http://localhost:8000/api/v1/games/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '{"opponent": "steve"}'
```

The requesting user is always player X and moves first.

Response `201 Created`:
```json
{
  "id": 1,
  "player_x": "david",
  "player_o": "steve",
  "current_turn": "david",
  "winner": null,
  "status": "active",
  "board": " - | - | - \n-----------\n - | - | - \n-----------\n - | - | - ",
  "moves": [],
  "created_at": "...",
  "updated_at": "..."
}
```

Errors:
- `400` — missing opponent, playing against yourself
- `404` — opponent not found

---

#### List my games

```
GET /games/
```

```bash
curl -s http://localhost:8000/api/v1/games/ \
  -H "Authorization: Bearer <access_token>"
```

Returns all games where the authenticated user is player X or O, ordered by most recent.

---

#### Game detail

```
GET /games/<id>/
```

```bash
curl -s http://localhost:8000/api/v1/games/1/ \
  -H "Authorization: Bearer <access_token>"
```

Errors:
- `404` — game not found

---

#### Make a move

```
POST /games/<id>/move/
```

```bash
curl -s -X POST http://localhost:8000/api/v1/games/1/move/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '{"position": 4}'
```

Response `200 OK` — returns updated game state including board and move history.

Errors:
- `400` — not your turn, position taken, position out of range (0–8), game already finished
- `404` — game not found

---

### Example: playing a full game

```bash

# david registers
TOKEN_david=$(curl -s -X POST http://localhost:8000/api/v1/register/ \
  -H "Content-Type: application/json" \
  -d '{"username": "david", "password": "Tictactoe1@"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['access'])")

# steve registers
TOKEN_steve=$(curl -s -X POST http://localhost:8000/api/v1/register/ \
  -H "Content-Type: application/json" \
  -d '{"username": "steve", "password": "Tictactoe1@"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['access'])")

# david logins and gets token
TOKEN_david=$(curl -s -X POST http://localhost:8000/api/v1/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "david", "password": "Tictactoe1@"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['access'])")

# steve logins and gets token
TOKEN_steve=$(curl -s -X POST http://localhost:8000/api/v1/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "steve", "password": "Tictactoe1@"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['access'])")

# david creates a game against steve
GAME_ID=$(curl -s -X POST http://localhost:8000/api/v1/games/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN_david" \
  -d '{"opponent": "steve"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")

# david plays position 0 (top-left)
curl -s -X POST http://localhost:8000/api/v1/games/$GAME_ID/move/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN_david" \
  -d '{"position": 0}'

# steve plays position 4 (center)
curl -s -X POST http://localhost:8000/api/v1/games/$GAME_ID/move/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN_steve" \
  -d '{"position": 4}'
```

---

## Management commands

Run from inside the Django container or devcontainer (`cd /app/tictactoe`):

#### create_roles

Creates the `admin` and `user` groups. Must be run once after the initial migration.

```bash
python manage.py create_roles
```

#### create_user

Creates a user (and its player profile) with the given role.

```bash
python manage.py create_user <username> <password> <role>
```

- `role` must be `admin` or `user`

```bash
python manage.py create_user david Tictactoe1@ user
python manage.py create_user steve Tictactoe1@ admin
```

#### create_admin - option 1
Creates admin user interactively:

```bash
python manage.py create_user david Tictactoe1@ admin
```

#### create_admin - option 2

Creates the default admin user from environment variables. Intended for automated deployments.

```bash
ADMIN_USERNAME=admin 
ADMIN_PASSWORD=Tictactoe1@ 

python manage.py create_admin
```

If `ADMIN_PASSWORD` is not set the command exits silently.

#### change_password

```bash
python manage.py change_password <username> <new_password>
```

---

## License

[Apache License 2.0](./LICENSE)
