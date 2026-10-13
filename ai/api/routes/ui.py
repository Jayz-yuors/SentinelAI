from __future__ import annotations

import base64
import hmac
import json
import os
import secrets
import threading
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote, urlencode

import httpx
from fastapi import APIRouter, BackgroundTasks, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import JSONResponse, RedirectResponse

router = APIRouter(prefix="/ui", tags=["SentinelAI Web UI"])

# These stores are process-local for the current single-instance development setup.
# Use a shared encrypted session store and durable job store for multiple workers.
_JOBS: dict[str, dict[str, Any]] = {}
_JOB_OWNERS: dict[str, str] = {}
_AUTH_SESSIONS: dict[str, dict[str, Any]] = {}
_OAUTH_STATES: dict[str, tuple[str, float]] = {}
_STATE_LOCK = threading.Lock()
_SESSION_TTL_SECONDS = 8 * 60 * 60
_OAUTH_STATE_TTL_SECONDS = 10 * 60


def _oauth_client_id() -> str:
    return os.getenv("GITHUB_OAUTH_CLIENT_ID", "").strip()


def _oauth_client_secret() -> str:
    return os.getenv("GITHUB_OAUTH_CLIENT_SECRET", "").strip()


def _oauth_redirect_uri(request: Request) -> str:
    return (
        os.getenv("GITHUB_OAUTH_REDIRECT_URI", "").strip()
        or str(request.url_for("github_oauth_callback"))
    )


def _cookie_secure(request: Request) -> bool:
    configured = os.getenv("SENTINELAI_COOKIE_SECURE")
    if configured is not None:
        return configured.strip().lower() == "true"
    return request.url.scheme == "https"


def _cookie_samesite() -> str:
    configured = os.getenv("SENTINELAI_COOKIE_SAMESITE", "lax").strip().lower()
    return configured if configured in {"lax", "strict", "none"} else "lax"


def _frontend_url() -> str:
    origins = [
        item.strip().rstrip("/")
        for item in os.getenv(
            "SENTINELAI_FRONTEND_ORIGINS",
            "http://localhost:5173",
        ).split(",")
        if item.strip()
    ]
    origin = origins[0] if origins else "http://localhost:5173"
    return f"{origin}/"


def _require_frontend_origin(request: Request) -> None:
    origin = request.headers.get("origin", "").rstrip("/")
    allowed = {
        item.strip().rstrip("/")
        for item in os.getenv(
            "SENTINELAI_FRONTEND_ORIGINS",
            "http://localhost:5173",
        ).split(",")
        if item.strip()
    }
    if not origin or origin not in allowed:
        raise HTTPException(status_code=403, detail="Request origin is not allowed.")


def _get_session(request: Request) -> tuple[str, dict[str, Any]]:
    session_id = request.cookies.get("sentinelai_session", "")
    if not session_id:
        raise HTTPException(
            status_code=401,
            detail="GitHub sign-in is required. Start at /ui/auth/login.",
        )

    with _STATE_LOCK:
        session = _AUTH_SESSIONS.get(session_id)
        if not session or session["expires_at"] <= time.time():
            _AUTH_SESSIONS.pop(session_id, None)
            raise HTTPException(
                status_code=401,
                detail="GitHub session expired. Sign in again.",
            )
        return session_id, dict(session)


def _github_headers(token: str) -> dict[str, str]:
    return {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "SentinelAI-Web",
    }


async def _github_get(
    token: str,
    path: str,
    params: dict[str, str] | None = None,
) -> Any:
    api = os.getenv("GITHUB_API_URL", "https://api.github.com").rstrip("/")
    try:
        async with httpx.AsyncClient(timeout=25) as client:
            response = await client.get(
                f"{api}/{path.lstrip('/')}",
                headers=_github_headers(token),
                params=params,
            )
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"GitHub API connection failed: {exc}",
        ) from exc
    if response.status_code >= 400:
        message = "GitHub API request failed"
        try:
            message = response.json().get("message", message)
        except Exception:
            pass
        raise HTTPException(status_code=response.status_code, detail=message)
    return response.json()


@router.get("/auth/status")
def auth_status(request: Request) -> dict[str, Any]:
    configured = bool(_oauth_client_id() and _oauth_client_secret())
    session_id = request.cookies.get("sentinelai_session", "")
    with _STATE_LOCK:
        session = _AUTH_SESSIONS.get(session_id)
        if session and session["expires_at"] <= time.time():
            _AUTH_SESSIONS.pop(session_id, None)
            session = None
    return {
        "configured": configured,
        "authenticated": bool(session),
        "login": (session or {}).get("user", {}).get("login"),
        "avatar_url": (session or {}).get("user", {}).get("avatar_url"),
        "name": (session or {}).get("user", {}).get("name"),
    }


@router.get("/auth/login")
def github_oauth_login(request: Request) -> RedirectResponse:
    client_id = _oauth_client_id()
    if not client_id or not _oauth_client_secret():
        raise HTTPException(
            status_code=503,
            detail=(
                "GitHub OAuth is not configured. Set "
                "GITHUB_OAUTH_CLIENT_ID and GITHUB_OAUTH_CLIENT_SECRET "
                "in the server environment."
            ),
        )

    state = secrets.token_urlsafe(32)
    browser_binding = secrets.token_urlsafe(32)
    with _STATE_LOCK:
        now = time.time()
        expired_states = [
            key for key, (_, expires_at) in _OAUTH_STATES.items()
            if expires_at <= now
        ]
        for key in expired_states:
            _OAUTH_STATES.pop(key, None)
        _OAUTH_STATES[state] = (
            browser_binding,
            now + _OAUTH_STATE_TTL_SECONDS,
        )

    authorization_url = "https://github.com/login/oauth/authorize?" + urlencode(
        {
            "client_id": client_id,
            "redirect_uri": _oauth_redirect_uri(request),
            "scope": "repo read:user",
            "state": state,
        }
    )
    response = RedirectResponse(authorization_url, status_code=302)
    response.set_cookie(
        "sentinelai_oauth_binding",
        browser_binding,
        max_age=_OAUTH_STATE_TTL_SECONDS,
        httponly=True,
        secure=_cookie_secure(request),
        samesite=_cookie_samesite(),
        path="/ui/auth",
    )
    return response


@router.get("/auth/callback", name="github_oauth_callback")
async def github_oauth_callback(
    request: Request,
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
) -> RedirectResponse:
    if error:
        response = RedirectResponse(
            f"{_frontend_url()}?github_auth=denied",
            status_code=302,
        )
        response.delete_cookie("sentinelai_oauth_binding", path="/ui/auth")
        return response

    if not code or not state:
        raise HTTPException(status_code=400, detail="GitHub authorization response is incomplete.")

    browser_binding = request.cookies.get("sentinelai_oauth_binding", "")
    with _STATE_LOCK:
        expected = _OAUTH_STATES.pop(state, None)
    if (
        not expected
        or expected[1] <= time.time()
        or not browser_binding
        or not hmac.compare_digest(expected[0], browser_binding)
    ):
        raise HTTPException(status_code=400, detail="GitHub authorization state is invalid or expired.")

    try:
        async with httpx.AsyncClient(timeout=25) as client:
            token_response = await client.post(
                "https://github.com/login/oauth/access_token",
                headers={"Accept": "application/json"},
                data={
                    "client_id": _oauth_client_id(),
                    "client_secret": _oauth_client_secret(),
                    "code": code,
                    "redirect_uri": _oauth_redirect_uri(request),
                },
            )
            token_response.raise_for_status()
            token_data = token_response.json()
    except (httpx.HTTPError, ValueError) as exc:
        raise HTTPException(status_code=502, detail="Could not complete GitHub token exchange.") from exc

    access_token = str(token_data.get("access_token") or "").strip()
    if not access_token:
        raise HTTPException(status_code=401, detail="GitHub did not issue an access token.")

    user = await _github_get(access_token, "user")
    session_id = secrets.token_urlsafe(32)
    with _STATE_LOCK:
        _AUTH_SESSIONS[session_id] = {
            "token": access_token,
            "user": {
                "id": user.get("id"),
                "login": user.get("login"),
                "name": user.get("name"),
                "email": user.get("email"),
                "avatar_url": user.get("avatar_url"),
            },
            "expires_at": time.time() + _SESSION_TTL_SECONDS,
        }

    response = RedirectResponse(
        f"{_frontend_url()}?github_auth=connected",
        status_code=302,
    )
    response.set_cookie(
        "sentinelai_session",
        session_id,
        max_age=_SESSION_TTL_SECONDS,
        httponly=True,
        secure=_cookie_secure(request),
        samesite=_cookie_samesite(),
        path="/",
    )
    response.delete_cookie("sentinelai_oauth_binding", path="/ui/auth")
    return response


@router.post("/auth/logout")
def github_oauth_logout(request: Request) -> JSONResponse:
    _require_frontend_origin(request)
    session_id = request.cookies.get("sentinelai_session", "")
    with _STATE_LOCK:
        _AUTH_SESSIONS.pop(session_id, None)
    response = JSONResponse({"logged_out": True})
    response.delete_cookie("sentinelai_session", path="/")
    return response


@router.get("/github/status")
async def github_status(request: Request) -> dict[str, Any]:
    _, session = _get_session(request)
    user = session["user"]
    return {
        "connected": True,
        "login": user.get("login"),
        "avatar_url": user.get("avatar_url"),
        "name": user.get("name"),
    }


@router.get("/github/repositories")
async def github_repositories(
    request: Request,
    page: int = 1,
    per_page: int = 50,
) -> dict[str, Any]:
    _, session = _get_session(request)
    per_page = max(1, min(per_page, 100))
    repos = await _github_get(
        session["token"],
        "user/repos",
        {
            "sort": "updated",
            "per_page": str(per_page),
            "page": str(max(1, page)),
            "affiliation": "owner,collaborator,organization_member",
        },
    )
    return {"items": [{
        "id": repo.get("id"),
        "name": repo.get("name"),
        "full_name": repo.get("full_name"),
        "private": repo.get("private", False),
        "description": repo.get("description"),
        "html_url": repo.get("html_url"),
        "default_branch": repo.get("default_branch", "main"),
        "updated_at": repo.get("updated_at"),
        "language": repo.get("language"),
        "owner": (repo.get("owner") or {}).get("login"),
    } for repo in repos]}


@router.get("/github/repositories/{owner}/{repo}/tree")
async def repository_tree(
    request: Request,
    owner: str,
    repo: str,
    branch: str = "main",
) -> dict[str, Any]:
    _, session = _get_session(request)
    safe_branch = quote(branch, safe="")
    data = await _github_get(
        session["token"],
        f"repos/{owner}/{repo}/git/trees/{safe_branch}",
        {"recursive": "1"},
    )
    return {
        "branch": branch,
        "truncated": data.get("truncated", False),
        "tree": [
            {
                "path": item.get("path"),
                "type": item.get("type"),
                "size": item.get("size"),
                "sha": item.get("sha"),
            }
            for item in data.get("tree", [])
            if item.get("type") in {"blob", "tree"}
        ],
    }


@router.get("/github/repositories/{owner}/{repo}/file")
async def repository_file(
    request: Request,
    owner: str,
    repo: str,
    path: str,
    branch: str = "main",
) -> dict[str, Any]:
    _, session = _get_session(request)
    if not path or path.startswith("/") or ".." in Path(path).parts:
        raise HTTPException(status_code=400, detail="Invalid repository-relative file path.")
    data = await _github_get(
        session["token"],
        f"repos/{owner}/{repo}/contents/{quote(path, safe='/')}",
        {"ref": branch},
    )
    if data.get("type") != "file":
        raise HTTPException(status_code=400, detail="The selected path is not a file.")
    try:
        content = base64.b64decode(data.get("content", "")).decode("utf-8")
    except (ValueError, UnicodeDecodeError) as exc:
        raise HTTPException(status_code=415, detail="This file is not readable as UTF-8 text in the editor.") from exc
    return {
        "path": data.get("path", path),
        "sha": data.get("sha"),
        "size": data.get("size"),
        "content": content,
    }


def _run_remediation(
    job_id: str,
    upload_path: Path,
    repository_url: str,
    target: str,
    branch: str,
    reason: str,
    push: bool,
    github_token: str,
) -> None:
    with _STATE_LOCK:
        _JOBS[job_id]["status"] = "running"
        _JOBS[job_id]["stage"] = "Starting SentinelAI remediation"
        _JOBS[job_id]["started_at"] = datetime.now(timezone.utc).isoformat()
    try:
        from ai.integrations.local_remediation.service import LocalRemediationService

        service = LocalRemediationService(github_token=github_token)
        result = service.execute({
            "repository_url": repository_url,
            "target": target,
            "base_branch": branch,
            "local_file": str(upload_path),
            "reason": reason,
            "push": push,
        })
        payload = result.to_dict() if hasattr(result, "to_dict") else vars(result)
        with _STATE_LOCK:
            _JOBS[job_id].update({
                "status": "completed" if payload.get("success") else "failed",
                "stage": "Workflow finished",
                "result": payload,
            })
    except Exception as exc:
        with _STATE_LOCK:
            _JOBS[job_id].update({
                "status": "failed",
                "stage": "Workflow failed",
                "error": f"{type(exc).__name__}: {exc}",
            })
    finally:
        with _STATE_LOCK:
            _JOBS[job_id]["finished_at"] = datetime.now(timezone.utc).isoformat()


@router.post("/analysis", status_code=202)
async def start_analysis(
    request: Request,
    background_tasks: BackgroundTasks,
    repository_url: str = Form(...),
    target: str = Form(...),
    branch: str = Form("main"),
    reason: str = Form(..., min_length=20),
    push: bool = Form(False),
    file: UploadFile = File(...),
) -> dict[str, Any]:
    _require_frontend_origin(request)
    session_id, session = _get_session(request)
    filename = Path(file.filename or "uploaded-code.txt").name
    if filename != Path(target.replace("\\", "/")).name:
        raise HTTPException(status_code=400, detail="Uploaded filename must match the selected repository target filename.")
    if not target or target.startswith(("/", "\\")) or ".." in Path(target.replace("\\", "/")).parts:
        raise HTTPException(status_code=400, detail="Target must be a safe repository-relative path.")
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    if len(content) > 2 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File exceeds the 2 MiB UI upload limit.")
    try:
        content.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise HTTPException(status_code=415, detail="Only UTF-8 text source files are supported.") from exc

    job_id = uuid.uuid4().hex
    upload_dir = Path("artifacts/ui-uploads").resolve() / job_id
    upload_dir.mkdir(parents=True, exist_ok=True)
    upload_path = upload_dir / filename
    upload_path.write_bytes(content)
    with _STATE_LOCK:
        _JOBS[job_id] = {
            "id": job_id,
            "status": "queued",
            "stage": "Queued",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "repository_url": repository_url,
            "target": target,
            "branch": branch,
        }
        _JOB_OWNERS[job_id] = session_id
    background_tasks.add_task(
        _run_remediation,
        job_id,
        upload_path,
        repository_url,
        target,
        branch,
        reason,
        push,
        session["token"],
    )
    return {"id": job_id, "status": "queued", "poll_url": f"/ui/analysis/{job_id}"}


@router.get("/analysis/{job_id}")
def get_analysis(request: Request, job_id: str) -> dict[str, Any]:
    session_id, _ = _get_session(request)
    with _STATE_LOCK:
        job = _JOBS.get(job_id)
        if job is None or _JOB_OWNERS.get(job_id) != session_id:
            raise HTTPException(status_code=404, detail="Analysis job not found.")
        return dict(job)


@router.get("/analysis/{job_id}/evidence")
async def get_analysis_evidence(request: Request, job_id: str) -> dict[str, Any]:
    """Read the evidence bundle from the pushed candidate branch for the UI."""
    session_id, session = _get_session(request)
    with _STATE_LOCK:
        job = _JOBS.get(job_id)
        if job is None or _JOB_OWNERS.get(job_id) != session_id:
            raise HTTPException(status_code=404, detail="Analysis job not found.")
        job = dict(job)

    result = job.get("result") or {}
    candidate_branch = result.get("candidate_branch")
    artifact_directory = result.get("artifact_directory")
    if job.get("status") != "completed" or not candidate_branch or not artifact_directory:
        raise HTTPException(
            status_code=404,
            detail="No pushed evidence bundle is available for this run.",
        )

    repository_url = str(job.get("repository_url") or "")
    try:
        owner, repo = repository_url.rstrip("/").removesuffix(".git").split("/")[-2:]
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="The job repository URL is invalid.") from exc

    run_id = Path(artifact_directory).name
    evidence_path = f".sentinelai/remediation/{run_id}"
    token = session["token"]
    try:
        entries = await _github_get(
            token,
            f"repos/{owner}/{repo}/contents/{quote(evidence_path, safe='/')}",
            {"ref": str(candidate_branch)},
        )
        if not isinstance(entries, list):
            raise HTTPException(status_code=404, detail="Evidence directory was not found on the candidate branch.")

        evidence: dict[str, Any] = {}
        patch = ""
        files: list[dict[str, Any]] = []
        readable_suffixes = {".json", ".md", ".patch", ".txt"}
        for entry in entries:
            name = str(entry.get("name") or "")
            files.append({
                "name": name,
                "size": entry.get("size"),
                "html_url": entry.get("html_url"),
            })
            if Path(name).suffix.lower() not in readable_suffixes or entry.get("type") != "file":
                continue
            content = await _github_get(
                token,
                f"repos/{owner}/{repo}/contents/{quote(evidence_path + '/' + name, safe='/')}",
                {"ref": str(candidate_branch)},
            )
            encoded = str(content.get("content") or "").replace("\n", "")
            try:
                decoded = base64.b64decode(encoded).decode("utf-8")
            except (ValueError, UnicodeDecodeError):
                continue
            if name == "evidence.json":
                try:
                    parsed = json.loads(decoded)
                    evidence = parsed if isinstance(parsed, dict) else {"value": parsed}
                except json.JSONDecodeError:
                    evidence = {"raw": decoded}
            elif name == "proposed_change.patch":
                patch = decoded
            elif name.endswith(".json"):
                try:
                    evidence[Path(name).stem] = json.loads(decoded)
                except json.JSONDecodeError:
                    evidence[Path(name).stem] = {"raw": decoded}
            elif name in {"README.md", "developer_reason.md"}:
                evidence[Path(name).stem] = decoded
        return {"run_id": run_id, "candidate_branch": candidate_branch, "evidence": evidence, "patch": patch, "files": files}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Could not load the GitHub evidence bundle: {exc}") from exc
