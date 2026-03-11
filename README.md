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

## MARK-3 Cloud – Project Structure

```
Mark-3-Cloud
│
├── Frontend
│   ├── index.html              # Login page
│   ├── style.css               # Main stylesheet
│   │
│   ├── js
│   │   └── login.js            # Password toggle JS
│   │
│   └── images
│       └── login.jpg           # Background image
│
├── Backend
│   ├── app.py                  # Flask server
│   ├── routes.py               # Login / upload routes
│   └── requirements.txt        # Python dependencies
│
├── Database
│   ├── schema.sql              # Tables
│   └── db_connect.py           # PostgreSQL connection
│
├── AI-Module
│   ├── object_detection.py
│   └── model_loader.py
│
├── Storage
│   └── uploads
│
├── Docs
│   ├── architecture.png
│   ├── flowchart.png
│   └── report
│
├── README.md
├── .gitignore
└── LICENSE
```