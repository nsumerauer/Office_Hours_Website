# ROBOTS.md

This file documents how AI tools or automation should interact with this project.

## Purpose

The app helps faculty choose office-hour times that best fit student schedules using optimization over submitted availability windows.

## Project Rules for AI Contributors

- Preserve the two-page workflow:
  - Student submission page
  - Professor optimization page
- Keep class-code isolation in all new features.
- Maintain Python + Flask architecture unless explicitly requested otherwise.
- Keep deployment compatibility with Vercel Python routing.
- Keep production data persistence compatible with hosted PostgreSQL via `DATABASE_URL`.
- Avoid introducing breaking schema changes without migration guidance.
- Keep UI simple, readable, and classroom-appropriate.
- Preserve the professor demo-loader flow for class code `1234` unless explicitly replaced.

## Quality Expectations

- Validate all schedule inputs (day, start, end).
- Keep time logic consistent (minutes from midnight).
- Ensure optimization remains deterministic and easy to explain.
- Keep weekend enable/disable behavior enforced in both UI and backend logic.
- Add tests if a testing framework is introduced later.

## Security and Privacy

- Do not hardcode production secrets.
- Avoid collecting unnecessary personal data.
- Keep data scoped to class-code use cases only.

## Handoff Notes

When modifying this project, update:

- `README.md` if setup/deploy steps change
- `ROBOTS.md` if AI workflow expectations change
