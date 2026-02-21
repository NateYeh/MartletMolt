.PHONY: install format lint test clean yaml-check yaml-fix

# 安裝依賴
install:
	pip install -e ".[dev]"
	pip install yamllint yamlfix

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

# 執行測試
test:
	pytest tests/ -v --cov=martlet_molt

# 清理
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# 完整檢查（CI/CD 用）
ci: lint test