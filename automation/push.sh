#!/data/data/com.termux/files/usr/bin/bash
set -e
cd "$(dirname "$0")/.."
python3 core-mother/mother_core.py
git add .
git commit -m "Update: $(date +%F_%T)" --allow-empty
git push
echo "Synced ✅"
