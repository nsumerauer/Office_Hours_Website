# Office Hours Optimizer (AI Final Project)

A Python web app for collecting student class times and helping a professor choose office-hour times that maximize student attendance by avoiding those class blocks.

## Link To Website
- https://ai-final-gamma.vercel.app/ 

## Features

- Two-page workflow:
  - Student page to submit class times by class code.
  - Professor page to add availability and optimize office-hour windows.
- Multi-day schedule entry (for example M/W/F in one submit).
- Professor weekend toggle (enable/disable Saturday and Sunday office hours).
- Class-code isolation so each class has its own scheduling data.
- Stores:
  - student schedule intervals
  - professor availability intervals
  - opened office-hour times
- Optimization engine ranks 60-minute windows (in 30-minute increments) by expected students free from class.
- Ability to open recommended times and manage them.
- One-click website demo loader for class code `1234`.

## Tech Stack

- Python
- Flask
- PostgreSQL (production) with SQLite fallback for local dev
- HTML/CSS templates
- Vercel deployment config (`vercel.json`)

## Local Run

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
   - `http://127.0.0.1:5000/professor`

## Run Tests

From the project directory:

```bash
python -m pip install -r requirements.txt
python -m pytest -q
```

Expected result:
- all tests pass (for example: `7 passed`)

## Vercel Deploy

1. Push this project to a Git provider (GitHub recommended).
2. Import the repository in Vercel.
3. Add environment variable `DATABASE_URL` in Vercel (use Vercel Postgres, Neon, Supabase, etc.).
4. Keep framework settings default for a Python project.
5. Vercel will use `vercel.json` to route requests to `app.py`.
6. Deploy and open the generated public URL.

## Normal Use on Vercel Website

After deployment, open your public Vercel URL and use:

1. `/student`
   - Enter class code and student name
   - Add one or more day/time class blocks
2. `/professor`
   - Enter the same class code
   - Add professor availability
   - (Optional) set weekend on/off
   - Click **Find Best Times** and optionally **Open This Time**

## Testing Mode (Demo Data from Website)

Use this when you want to quickly verify optimization without manual data entry.

1. Open `/professor` on your local or deployed app.
2. Click **Load Demo Data (Class 1234)**.
3. Click **Find Best Times**.
4. Confirm you see ranked recommendations for class code `1234`.

This demo dataset includes:
- multiple students with overlapping M/W/F schedules
- additional Tuesday/Thursday schedules
- weekend data to test weekend-toggle behavior

## Data Notes

- If `DATABASE_URL` is set to a Postgres connection string, the app uses PostgreSQL.
- Without `DATABASE_URL`, local development uses SQLite at `data/office_hours.db`.
- On Vercel without `DATABASE_URL`, fallback SQLite uses `/tmp/office_hours.db` (ephemeral).
- Data model supports:
  - multiple students per class code
  - one professor (or more, if needed) adding availability to the same class code

## Project Deliverables

- Standalone deployed web app with public URL
- `README.md`
- `ROBOTS.md`
