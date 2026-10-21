# FinLit Pro (website)

This repository is the FinLit Pro website and nothing else: a React and Vite
site in JavaScript, with serverless API functions in `api/`.

## The desktop app is a separate project

FinLit Pro Desktop lives in its own repository, KrishModi6/finlit-pro-desktop.
Keep the two apart:

- Website changes, branches and pull requests go in this repository only.
  Desktop changes go in finlit-pro-desktop only.
- Never add the desktop app's code to this repository, and never open a pull
  request for one project in the other's repository.
- When a fix applies to both, make it separately in each repository, each
  with its own tests.
- The old branch `claude/pensive-goldberg-s5cto4` here holds a copy of the
  desktop app from before the split. Do not build on it; finlit-pro-desktop
  is where the desktop app lives.

## Checks

Run both before pushing:

- `npm test`
- `npm run lint`
