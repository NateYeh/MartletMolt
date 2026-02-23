#!/bin/bash

# MartletMolt 專案啟動服務
PROJECT_ROOT="/mnt/work/py_works/external_projects/MartletMolt"
LOG_DIR="$PROJECT_ROOT/shared/logs"

# 確保日誌目錄存在
mkdir -p "$LOG_DIR"

# 服務開關
START_ORCHESTRATOR=1
START_FRONTEND=1

# 封裝好的啟動函數 (參考 app.sh 優化版)
start_service() {
    _name="$1"
    _dir="$2"
    _cmd="$3"

    if screen -list | grep -q "${_name}"; then
        echo "✅ [$_name] 已經在運行中。"
    else
        echo "🚀 正在啟動 [$_name]..."
        (
            cd "$_dir" || exit 1
            # 啟動並記錄日誌
            screen -dmS "$_name" bash -c "$_cmd 2>&1 | tee -a $LOG_DIR/${_name}.log"
        )
        sleep 2
    fi
}

# --- 執行順序 ---

# 1. 啟動 Orchestrator (入口 8000 + A/B 切換器)
if [ "$START_ORCHESTRATOR" -eq 1 ]; then
    # 使用 orchestrator 模組啟動，並進入 daemon 模式監控
    start_service "martlet-orc" "$PROJECT_ROOT" "python -m orchestrator.main start --daemon"
fi

# 等待後端就位
echo "⌛ 等待守護者就位..."
sleep 3

# 2. 啟動 Web Lite V2 前端 (入口 8002)
if [ "$START_FRONTEND" -eq 1 ]; then
    start_service "martlet-web" "$PROJECT_ROOT/frontend/web-lite-v2" "python main.py"
fi

echo "✨ MartletMolt 啟動流程完成！"
echo "---------------------------------------"
echo "🌐 前端入口: http://你的服務器IP:8002"
echo "🛡️ 調度中心: http://你的服務器IP:8000"
echo "📂 日誌目錄: $LOG_DIR"
echo "---------------------------------------"
echo "提示: 使用 'screen -r martlet-orc' 查看後端日誌"
