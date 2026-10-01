---
description: Auto-Commit and Push Workflow Rule
---

# Git Workflow Rule

Going forward, whenever you complete ANY task, feature, bug fix, or code update for the user, you MUST:
1. Always commit and push immediately to GitHub.
2. The sequence should be:
   - `git add .`
   - `git commit -m "<descriptive message>"`
   - `git pull --rebase origin main` (Resolve conflicts if any)
   - `git push origin main`
3. Never leave changes uncommitted or unpushed, so the collaborator always has the latest code in real-time.
4. If `db.sqlite3` is locked during pull, handle it gracefully by merging in a scratch clone or informing the user to stop the server.
