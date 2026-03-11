# MARK-3 Cloud System

Self-hosted cloud storage platform built on Raspberry Pi.

## Features
- Secure file storage
- File sharing
- AI-based image recognition
- PostgreSQL metadata storage

## Tech Stack
Frontend: HTML, CSS, JavaScript
Backend: Flask (Python)
Database: PostgreSQL
Hardware: Raspberry Pi 4

Mark-3-Cloud Folder Structure
│
├── Frontend
│   │
│   ├── index.html              # Login page
│   ├── style.css               # Main stylesheet
│   │
│   ├── js
│   │   └── login.js            # Password toggle / login JS
│   │
│   └── images
│       └── login.jpg           # Background image
│
├── Backend
│   │
│   ├── app.py                  # Main server using Flask
│   ├── routes.py               # Login / upload routes
│   └── requirements.txt        # Python dependencies
│
├── Database
│   │
│   ├── schema.sql              # Tables for users/files
│   └── db_connect.py           # PostgreSQL connection
│
├── AI-Module
│   │
│   ├── object_detection.py     # Image recognition
│   └── model_loader.py         # Loads AI model
│
├── Storage
│   │
│   └── uploads                 # Uploaded user files
│
├── Docs
│   │
│   ├── architecture.png        # System architecture diagram
│   ├── flowchart.png           # Flowchart you made
│   └── report                  # Project report files
│
├── README.md                   # Project explanation
├── .gitignore                  # Ignore unnecessary files
└── LICENSE                     # Optional