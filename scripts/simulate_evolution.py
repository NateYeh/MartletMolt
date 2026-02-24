import requests
import time
import json

BASE_URL = "http://localhost:8000"

def log_test(step, message):
    print(f"\n\033[94m[{step}]\033[0m {message}")

def get_status():
    resp = requests.get(f"{BASE_URL}/status")
    return resp.json()

def chat(message):
    # 這裡假設後端有個簡單的 /chat 或者我們直接測根路徑
    # 根據我們啟動 logs, 後端跑在 8001
    try:
        resp = requests.get(BASE_URL + "/")
        source = resp.headers.get("X-Martlet-Source", "Unknown")
        return resp.text, source
    except Exception as e:
        return str(e), "Error"

def run_simulation():
    print("🚀 \033[1mMartletMolt 進化循環演示開始\033[0m")
    
    # 1. 初始狀態
    status = get_status()
    log_test("初始狀態", f"當前活躍系統: {status['active_system']}")
    
    # 2. 第一輪對話
    content, source = chat("你好，你是誰？")
    log_test("第一輪對話", f"回應來自: \033[92m{source}\033[0m")
    
    # 3. 模擬進化 - 由 MCP 修改 System B 代碼 (這裡我直接在測試時手動改個小地方)
    log_test("進化中", "正在為 System B 進行『大腦改造』...")
    
    # 4. 觸發切換
    log_test("指令", "正在切換流量至 System B...")
    requests.post(f"{BASE_URL}/switch/system_b")
    
    # 等待一小會讓快取或連線穩定
    time.sleep(1)
    
    # 5. 第二輪對話
    content, source = chat("再問你一次，你是誰？")
    log_test("第二輪對話", f"回應來自: \033[93m{source}\033[0m")
    
    new_status = get_status()
    print(f"\n✨ \033[1m演示結束。系統已成功從 {status['active_system']} 進化至 {new_status['active_system']}\033[0m")

if __name__ == "__main__":
    run_simulation()
