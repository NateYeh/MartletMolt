.PHONY: install format lint clean yaml-check yaml-fix dev dev-backend dev-frontend docs check-all

# 安裝依賴
install:
	pip install -e ".[dev]"
	pip install yamllint yamlfix
	pip install httpx

# 格式化程式碼
format:
	ruff format .
	yamlfix **/*.yaml **/*.yml

# 程式碼檢查
lint:
	ruff check .
	ruff format --check .
	pyright
	yamllint -c .yamllint .

# YAML 檢查
yaml-check:
	yamllint -c .yamllint .

# YAML 自動修正
yaml-fix:
	yamlfix **/*.yaml **/*.yml

# 清理
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# 完整檢查（CI/CD 用）
ci: lint

# 文檔生成
docs:
	@echo "📝 Generating API documentation..."
	python tools/generate_api_docs.py

# 完整檢查 + 文檔生成
check-all: lint docs
	@echo "✅ All checks passed and docs generated!"

# ─────────────────────────────────────────────────────────
# 開發服務啟動命令
# ─────────────────────────────────────────────────────────

# 開發模式：同時啟動後端 API 和前端服務
dev:
	@echo "🚀 Starting MartletMolt Development Environment..."
	@echo "Backend API: http://0.0.0.0:8001"
	@echo "Frontend:    http://0.0.0.0:8002"
	@echo ""
	@echo "Press Ctrl+C to stop all services"
	@echo ""
	@trap 'kill 0' INT; \
	python -m martlet_molt.main & \
	cd frontend/web-lite && python main.py & \
	wait

# 只啟動後端 API（Port 8001）
dev-backend:
	@echo "🚀 Starting Backend API Server..."
	@echo "Backend API: http://0.0.0.0:8001"
	python -m martlet_molt.main

# 只啟動前端服務（Port 8002）
dev-frontend:
	@echo "🚀 Starting Frontend Server..."
	@echo "Frontend: http://0.0.0.0:8002"
	@echo "Ensure Backend API is running at http://0.0.0.0:8001"
	cd frontend/web-lite && python main.py
