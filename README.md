# Office Hours Optimizer (AI Final Project)

A Flask web app that helps professors schedule office hours by comparing their availability against student class schedules for a specific class code.

## Website

- https://ai-final-gamma.vercel.app/

## Core Workflow

1. Students use `/student` to submit their class-time blocks.
2. Professors sign in at `/professor-login`.
3. Professors use `/professor` to:
   - add availability windows,
   - filter by day (optional),
   - include/exclude weekends (optional),
   - generate ranked office-hour recommendations,
   - open recommended times.

## Features

- Class-code scoped scheduling data.
- Multi-day class-time entry (for example M/W/F in one submit).
- Recommendation engine for 60-minute windows using 30-minute increments.
- Weekend support toggle for professor optimization.
- Demo-data loader for class code `1234`.
- Basic professor session login/logout flow.

## Demo Professor Login

Current demo credentials:

- Username: `admin`
- Password: `password`

## Tech Stack

- Python
- Flask
- PostgreSQL in production via `DATABASE_URL`
- SQLite fallback for local development
- HTML templates + CSS
- Vercel deployment via `vercel.json`

## Local Development

1. Create and activate a virtual environment.
2. Install dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

3. Run the app:

   ```bash
   python app.py
   ```

4. Open:
   - `http://127.0.0.1:5000/student`
   - `http://127.0.0.1:5000/professor-login` (recommended entry for professor flow)

## Testing

```bash
python -m pip install -r requirements.txt
python -m pytest -q
```

## Deployment (Vercel)

1. Push this repo to GitHub.
2. Import it into Vercel as a Python project.
3. Configure `DATABASE_URL` (recommended for persistent production data).
4. Deploy; Vercel routes requests to `app.py` using `vercel.json`.

## Data Storage Notes

- If `DATABASE_URL` is configured, the app uses PostgreSQL.
- Otherwise it uses SQLite at `data/office_hours.db` locally.
- On Vercel without `DATABASE_URL`, fallback SQLite uses `/tmp/office_hours.db` (ephemeral).

## Known Limitations

- Professor authentication uses demo credentials and is not production-grade auth.
- Class-code based access is not a full authorization model (anyone with a code can submit student data).
- No dedicated admin/user management UI yet.
- Recommendation scoring focuses on schedule conflicts only (no preferences like location, capacity, or historical attendance).
- SQLite fallback on serverless deployments is ephemeral unless `DATABASE_URL` is configured.
