```
Mark-3-Cloud/
├── app/                          # Flask application code
│   ├── __init__.py
│   ├── routes.py
│   ├── models.py
│   ├── static/                   # Frontend assets
│   │   ├── css/
│   │   │   └── style.css
│   │   ├── js/
│   │   │   └── script.js
│   │   └── images/
│   │       └── logo.png
│   ├── templates/                # HTML templates
│   │   ├── index.html
│   │   └── dashboard.html
│   └── __pycache__/              # ignored by .gitignore
├── instance/                     # Flask instance folder (ignored)
│   ├── config.py
│   └── database.sqlite3
├── tests/                        # Unit / integration tests
│   ├── test_routes.py
│   └── test_models.py
├── venv/                         # Python virtual environment (ignored)
│   ├── bin/
│   ├── include/
│   ├── lib/
│   └── pyvenv.cfg
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .gitignore
├── README.md
├── .env                          # environment variables (ignored)
├── scripts/                      # utility scripts
│   └── setup.sh
├── docs/                         # optional project docs
│   └── _build/                   # ignored build folder
├── .vscode/                       # IDE settings (optional, ignored)
│   └── settings.json
└── __pycache__/                  # repo-level ignored Python cache
```
