#!/bin/bash

# Stage the script file
git add info.sh

# Commit with backdated author and committer dates (June 10, 2026)
GIT_AUTHOR_DATE="2026-06-10T12:00:00" GIT_COMMITTER_DATE="2026-06-10T12:00:00" git commit -m "Add info.sh (Backdated to June 10, 2026)"

# Force push to the remote repository (assumes your primary branch is 'main')
git push -f origin main
