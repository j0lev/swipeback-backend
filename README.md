# Swipeback

This is a FastAPI-powered backend for Swipeback App.
---

## Table of Contents
- [About](#about)
- [Getting started](#start)
- [Installation](#installation)
- [Authentication](#authentication)
- [Core Endpoints](#ndpointsion)
- [API Documentation](#apidocu)
- [Contact](#contact)

---

## About

Swipeback designed to enable real-time interactions between professors (Users) and students. It supports the creation of modules, management of active lecture sessions via join codes, and various feedback mechanisms (Swiper, Sliders and Text Feedback). Students give anonymous feedback, so that they don't have to be logged in. 
It helps professors to get feedback for their lectures, in order to evaluate the students satisfaction level and their understanding of course content.

---

## Getting Started
#Prerequisites:
- Python 3.10+
- FastAPI (Web Framework, Pydantic for data validation)
- SQLModel (data bank)
- JWT for Authentication


---

## Installation

- Clone the repository
git clone https://github.com/j0lev/swipeback-backend.git

- Navigate into the project folder
cd app

- Project structure

```text

app/
├── auth.py         # Authentication & Dependencies
├── _init_.py
├── db.py           # DB‑Session
├── models/         # SQLModel models
│   ├── hero.py
│   ├── module.py
│   ├── session.py
│   ├── metric.py
│   ├── metric_value.py
│   ├── question.py
│   ├── question_response.py
│   ├── slider.py
│   └── text_feedback.py
├── routers/           # API Router
│   ├── hero.py
│   ├── module.py
│   ├── session.py
│   ├── metric.py
│   ├── metric_value.py
│   ├── question.py
│   ├── question_response.py
│   ├── slider.py
│   └── text_feedback.py
└── main.py            # FastAPI App
```

---


## Authentication

- **Professor endpoints**
  - Require `CurrentActiveUserDI`
  - JWT-based authentication
  - Used for modules, sessions, and results

- **Student endpoints**
  - No login required
  - Access via active `join_code`
  - Anonymous feedback

---

## Core Endpoints

### Authentication & Users
- POST /token: Exchange credentials for a JWT.

- POST /users: Register a new professor.

- GET /users/me: Fetch current professor profile.

### Module & Session Management
- POST /modules/: Create a course module.

- GET /modules/: List all modules for the current professor.

- POST /modules/{id}/sessions/start: Start a lecture and generate a 6-char Join Code.

- POST /sessions/{id}/end: Close an active session.

### Feedback (Student Access via Join Code)
- GET /modules/sliders/by_join_code/{code}: Fetch active sliders.

- GET /sessions/questions/by_join_code/{code}: Fetch active binary questions.

- POST /feedback/metric/{code}: Submit a numeric rating (0-10).

- POST /feedback/question/{code}: Submit a Yes/No response.

- POST /feedback/text/{code}: Submit open-ended text feedback.

### Results (Professor Only)
- GET /sessions/{id}/metrics/results: Get calculated averages for metrics.

- GET /sessions/{id}/questions/results: Get Yes/No counts for polls.

- GET /sessions/{id}/text-feedback: List all text comments.

---

## API Documentation
Once running, you can explore and test the full API via:

Swagger UI: http://localhost:8000/docs

ReDoc: http://localhost:8000/redoc

---

## Contact
- Jonathan Evers jonathan.evers2@stud.uni-hannover.de
- Iryna Polishchuk iryna.polishchuk@stud.uni-hannover.de