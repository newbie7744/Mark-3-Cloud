# Mark-3-Cloud

Mark-3-Cloud is a self-hosted personal cloud app built with Flask. It supports user accounts, file management, profile updates, and lightweight image classification for uploaded images. The current implementation is designed to run offline in Docker and uses local fonts and local file processing only.

## Features

- User signup and login with password hashing
- Password policy enforcement:
	- at least 9 characters
	- at least one letter
	- at least one uppercase letter
	- at least one number
	- at least one symbol
- Profile update and profile picture upload
- File upload, batch upload, folder upload, download, preview, rename, and delete
- Image classification for uploaded image files
- Human and non-human classification labels shown on image cards
- Per-user file storage under the app upload folder
- Offline-friendly UI with no external font dependency

## Current Database Setup

The app currently uses PostgreSQL in Docker.

- `docker-compose.yml` starts a `postgres:15` service
- The Flask app reads `DATABASE_URL` from the environment
- Existing databases are repaired at startup so the `classification` column is added automatically if missing

SQLite is not the default runtime database in the current model. If you want SQLite for local-only development, you would need to set `DATABASE_URL` manually to a SQLite URI.

## Project Structure

```text
Mark-3-Cloud/
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── routes.py
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css
│   │   ├── images/
│   │   │   └── bg.jpg
│   │   ├── js/
│   │   │   ├── dashboard.js
│   │   │   └── password.js
│   │   └── uploads/
│   │       ├── .gitkeep
│   │       ├── 1/
│   │       ├── 3/
│   │       └── 6.jpg
│   └── templates/
│       ├── dashboard.html
│       ├── login.html
│       └── signup.html
├── instance/
├── static/
│   └── uploads/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── run.py
└── README.md
```

Notes:

- `app/static/uploads/` is the active upload location used by the app.
- `static/uploads/` exists as a repository-level runtime folder and may be used for mounted or local storage setups.
- User uploads are created under user-specific subfolders when needed.

## Running With Docker

1. Create a `.env` file in the project root.
2. Set at least:

```env
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql+psycopg2://postgres:password@db:5432/cloud_db
```

3. Start the stack:

```bash
docker compose up --build
```

4. Open the app at `http://localhost:5000`.

## Local Development

If you want to run the app outside Docker, make sure `DATABASE_URL` points to a reachable PostgreSQL database. The app still expects that environment variable to exist.

Install dependencies with:

```bash
pip install -r requirements.txt
```

Then run:

```bash
python run.py
```

## Notes

- Uploads are stored under `app/static/uploads/<user_id>/`.
- Folder uploads preserve relative paths when the browser supports them.
- The app creates missing upload directories automatically.
- Image classification is local and does not require internet access.
- External font loading has been removed so the UI works fully offline.
