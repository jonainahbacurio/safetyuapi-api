# SafetyU FastAPI

A FastAPI + SQL database backend compatible with the existing SafetyU frontend.

## API contract

- `POST /api/emergencies`
- `GET /api/emergencies`
- `GET /api/emergencies/{id}`
- `PATCH /api/emergencies/{id}`
- `DELETE /api/emergencies/{id}`
- `GET /health`
- Interactive documentation: `/docs`

Statuses are exactly:

- `waiting`
- `responding`
- `resolved`

The API also returns `queuePosition`, `reference`, `createdAt`, and `updatedAt` in the format expected by the current SafetyU JavaScript.

## 1. Run locally on Windows

Open Command Prompt or PowerShell inside this folder:

```bash
python -m venv venv
```

PowerShell:

```powershell
venv\Scripts\Activate.ps1
```

Command Prompt:

```cmd
venv\Scripts\activate.bat
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run:

```bash
uvicorn app.main:app --reload
```

Open:

- API: `http://127.0.0.1:8000`
- Swagger docs: `http://127.0.0.1:8000/docs`

If `DATABASE_URL` is not set, the API automatically creates `safetyu.db` using SQLite for local testing.

## 2. Test an emergency

POST body:

```json
{
  "category": "fire",
  "location": "Computer Laboratory 1",
  "description": "Smoke detected near a computer unit"
}
```

Update status:

```json
{
  "status": "responding",
  "responder": "Responder 1"
}
```

Then resolve:

```json
{
  "status": "resolved",
  "responder": "Responder 1"
}
```

## 3. Connect the existing SafetyU website

Your current `script.js` contains:

```js
const API_ENDPOINT = "/api/emergencies";
```

That works only when the frontend and API are hosted under the same origin/rewrite setup.

If the FastAPI API is deployed separately, change it to your real API URL, for example:

```js
const API_ENDPOINT = "https://safetyu-api.onrender.com/api/emergencies";
```

Do not include a trailing slash.

## 4. Deploy to Render

This repository includes `render.yaml`, which defines a Python web service and a PostgreSQL database.

Push the folder to GitHub, then create a Render Blueprint from the repository. Render can read `render.yaml` and connect the `DATABASE_URL` environment variable to the PostgreSQL database.

Manual web-service settings, if you prefer not to use a Blueprint:

- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

Set `DATABASE_URL` to your PostgreSQL connection string.

## ESP32 example request

Your ESP32 should POST JSON to:

```text
https://YOUR-API.onrender.com/api/emergencies
```

Body:

```json
{
  "category": "fire",
  "location": "Computer Laboratory 1",
  "description": "SOS button activated"
}
```

The returned `id` can later be used for status checks or updates.
