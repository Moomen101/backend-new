# Missing Person Detection System

## Overview

This project is an AI-powered backend system for detecting missing persons using live camera feeds. It leverages FastAPI for the backend, SQLAlchemy for ORM, and integrates with AI face recognition (DeepFace) to match faces from camera streams against a database of missing persons. The system supports user authentication, missing person reporting, AI-based detection, and SOS alerts.

## Features

- **User Authentication:** Register and login endpoints for users.
- **Missing Person Reporting:** Users can report missing persons with details and images.
- **AI Detection:** Real-time face recognition from camera feeds, matching against reported missing persons.
- **SOS Alerts:** Users can send emergency SOS requests with location data.
- **Notifications:** Users receive notifications when a match is detected for a missing person they reported.
- **Image Uploads:** Handles and stores images for missing persons and detections.

## Project Structure

```
ai_watcher.py                # AI face recognition and camera stream handler
backend/
  requirements.txt           # Python dependencies
  app/
    main.py                  # FastAPI app entry point
    database.py              # Database setup (SQLite)
    models/                  # SQLAlchemy models (User, MissingPerson, Detection, Camera, SOSRequest)
    routers/                 # FastAPI routers for API endpoints
    services/
      ai_service.py          # (Placeholder for AI logic)
uploads/
  detections/                # Detected face images
  missing_persons/           # Uploaded missing person images
  verifications/             # (For user verification images)
```

## Setup Instructions

1. **Clone the repository**

2. **Install dependencies**
   ```
   pip install -r backend/requirements.txt
   ```

3. **Run the FastAPI backend**
   ```
   uvicorn backend.app.main:app --reload
   ```

4. **Run the AI watcher (face recognition)**
   ```
   python ai_watcher.py
   ```

5. **Access the API docs**
   - Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) in your browser.

## API Endpoints

- **User**
  - `POST /users/register` — Register a new user
  - `POST /users/login` — User login

- **Missing Persons**
  - `POST /missing-persons/report` — Report a missing person (with image)
  - `GET /missing-persons/all` — List all missing persons

- **AI Detections**
  - `POST /detections/match` — Register an AI detection (used by ai_watcher.py)
  - `GET /detections/notifications/{user_id}` — Get detection notifications for a user

- **SOS**
  - `POST /sos/send` — Send an SOS alert

## Database

- Uses SQLite by default (`missing_people.db`).
- Models: User, MissingPerson, Detection, Camera, SoSRequest.

## Notes

- The AI watcher requires a working RTSP camera stream and DeepFace installed.
- Uploaded images are stored in the `uploads/` directory.
- Static files are served at `/static`.
