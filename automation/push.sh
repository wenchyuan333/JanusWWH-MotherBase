#!/data/data/com.termux/files/usr/bin/bash
set -e
cd "$(dirname "$0")/.."

# 執行母體核心 → 生成新哈希
python3 core-mother/mother_core.py

# 提交所有變動
git add .
git commit -m "Update: $(date +%F_%T)" --allow-empty

# 只推送主倉庫
git push origin main

echo "✅ 同步完成！"
