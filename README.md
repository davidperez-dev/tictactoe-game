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
python manage.py runserver
```

The API is available at `http://localhost:8080/api/v1/`.

---

## Running with Docker

```bash
docker-compose up --build
```

---

## Running tests

```bash
cd tictactoe
python manage.py test game --verbosity=2
```

---

## License

[Apache License 2.0](./LICENSE)
