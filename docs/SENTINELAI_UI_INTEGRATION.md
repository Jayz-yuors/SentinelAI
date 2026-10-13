# SentinelAI UI integration

This document records the UI patch integrated into the existing SentinelAI tree. Existing folders and API modules remain in place; the React UI is under `frontend/` and its FastAPI endpoints are under `ai/api/routes/`.

## Updated and added files

- Added the React/Vite application files under `frontend/` from the supplied integration archive.
- Added `ai/api/routes/ui.py` and updated `ai/api/main.py` to register the UI router while retaining the analysis, health, and DevSecOps routers.
- Added `python-multipart` for upload form handling and `python-dotenv` for local `.env` loading in `ai/requirements.txt`.
- Added `reportlab` to `ai/requirements.txt`; remediation and Phase 7 workflows use it to generate PDF reports.
- Updated `docker-compose.yml` to pass OAuth app settings and cookie security settings to the AI container. The OAuth client secret and user access tokens remain server-side.
- Extended `.gitignore` for UI dependencies, build output, local UI environment settings, and uploaded source files.
- Added React/Vite TypeScript declarations so the included frontend build command can type-check the app.
- Pinned `@vitejs/plugin-react` to the Vite 6-compatible 4.x line; avoid `latest` because current plugin releases require newer Vite majors.
- Fixed the TypeScript type inference for combining folder and file entries in the repository tree.
- Restricted the AI gateway to Gemini with Groq fallback, removed eager OpenAI/OpenRouter imports, and passed those provider settings into the Compose AI container.
- Clarified that selecting a replacement file stages it in the UI; it is submitted to the API when the user starts the analysis.
- Configured candidate Git clones with the current user's OAuth token for HTTPS operations and set a repository-local commit identity from that authenticated GitHub profile (using its GitHub noreply address when no public email is available).
- Added per-user GitHub OAuth sign-in, state validation, HttpOnly session cookies, session logout/account switching, and per-session access to repositories and jobs.

## API routes

- `GET /ui/auth/status` — check OAuth configuration and current sign-in state.
- `GET /ui/auth/login` and `GET /ui/auth/callback` — start and finish the GitHub OAuth web flow.
- `POST /ui/auth/logout` — clear the current SentinelAI session.
- `GET /ui/github/status` — check the signed-in GitHub account.
- `GET /ui/github/repositories` — list accessible repositories.
- `GET /ui/github/repositories/{owner}/{repo}/tree` — list repository tree entries.
- `GET /ui/github/repositories/{owner}/{repo}/file` — load a UTF-8 text file.
- `POST /ui/analysis` — queue the existing local remediation workflow.
- `GET /ui/analysis/{job_id}` — poll the in-memory job status.

The UI calls FastAPI on port 8000 directly. It does not route these requests through Spring Boot. Sessions, OAuth state, and job state are process-local and are cleared when the AI service restarts; use a shared encrypted session store and durable job store before running multiple workers or production replicas. The UI uses each signed-in user's OAuth token. The legacy `GITHUB_TOKEN` is not used for browser UI repository requests.

## Configure GitHub sign-in

Register a GitHub OAuth App and set its callback URL to exactly `http://localhost:8000/ui/auth/callback` for local development. The UI requests `repo` and `read:user` so it can list private repositories, read source, create candidate branches/PRs when the user enables push, and identify the account. GitHub Apps are preferable for a production product that needs narrower repository permissions; this OAuth App flow is the current integration.

Add these settings to the root `.env` file. Keep the client secret server-side; do not put it in `frontend/.env` or a `VITE_*` setting.

```dotenv
GITHUB_OAUTH_CLIENT_ID=your-oauth-app-client-id
GITHUB_OAUTH_CLIENT_SECRET=your-oauth-app-client-secret
GITHUB_OAUTH_REDIRECT_URI=http://localhost:8000/ui/auth/callback
SENTINELAI_FRONTEND_ORIGINS=http://localhost:5173
SENTINELAI_COOKIE_SECURE=false
SENTINELAI_COOKIE_SAMESITE=lax
```

On startup, the browser UI checks for a session and redirects to GitHub sign-in when needed. Users can switch accounts from the sidebar. In HTTPS deployment, set `SENTINELAI_COOKIE_SECURE=true` and use the public callback URL registered with GitHub.

## Start with Docker Compose (recommended)

Run these commands in PowerShell from the SentinelAI project root after configuring the OAuth app. Docker Desktop must be running. Compose reads OAuth settings from the root `.env` file.

```powershell
Set-Location 'C:\Users\Shruti\jk\Python\Python_GUI\Project_series\11.SentiNelAI'
docker compose up -d --build postgres neo4j ai backend
docker compose ps
docker compose logs -f ai backend
```

Leave the service log command running. In a second PowerShell terminal, start the UI:

```powershell
Set-Location 'C:\Users\Shruti\jk\Python\Python_GUI\Project_series\11.SentiNelAI\frontend'
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
npm install
npm run dev
```

Open `http://localhost:5173`. The FastAPI docs are at `http://localhost:8000/docs`, and Spring Boot is at `http://localhost:8080` under Compose. Do not start a second local Uvicorn server on port 8000 while the Compose AI service is running.

## Run the AI API locally instead

Use this option instead of the Compose `ai` service. The commands create and activate a project virtual environment, install dependencies, then start Uvicorn from the project root. The application loads the root `.env` locally.

```powershell
Set-Location 'C:\Users\Shruti\jk\Python\Python_GUI\Project_series\11.SentiNelAI'
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r .\ai\requirements.txt
$env:SENTINELAI_FRONTEND_ORIGINS = 'http://localhost:5173'
python -m uvicorn ai.api.main:app --host 127.0.0.1 --port 8000 --reload
```

In another PowerShell terminal, run the same frontend commands from `frontend/` shown above. If PowerShell blocks virtual environment activation, allow it for that terminal only and activate again:

```powershell
Set-Location 'C:\Users\Shruti\jk\Python\Python_GUI\Project_series\11.SentiNelAI'
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## First manual smoke check

With the API and UI running, open `http://localhost:5173`. The browser should redirect to GitHub for sign-in, then return to SentinelAI. `/ui/github/status` requires a session cookie. Start with push disabled and inspect the returned workflow result. The UI workflow can push a candidate and create a pull request when enabled; do not enable that against a production repository until the existing verification and security gate behavior has been reviewed.
