#!/data/data/com.termux/files/usr/bin/bash
set -e
cd "$(dirname "$0")/.."

# 1️⃣ 執行母體核心 → 生成新哈希
python3 core-mother/mother_core.py

# 2️⃣ 提交所有變動
git add .
git commit -m "Update: $(date +%F_%T)" --allow-empty

# 3️⃣ 同步到雙倉庫 ⚡
echo "➡️  推送主倉庫..."
git push origin main
echo "➡️  推送鏡像倉庫..."
git push mirror main

echo "✅ 雙重同步完成！Cloudflare 自動部署中..."
