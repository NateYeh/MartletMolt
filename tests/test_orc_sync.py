import os

import pytest

from orchestrator.sync import Syncer


@pytest.fixture
def sync_env(tmp_path):
    # 模擬 System A 和 System B 的目錄
    src = tmp_path / "sys_a"
    dst = tmp_path / "sys_b"
    src.mkdir()
    dst.mkdir()

    # 在 A 建立一些檔案
    (src / "app.py").write_text("print('hello')", encoding="utf-8")
    (src / "data").mkdir()
    (src / "data" / "config.json").write_text("{}", encoding="utf-8")

    # 在 B 建立一些應該被保留的檔案 (排除清單中的)
    (dst / ".git").mkdir()
    (dst / ".git" / "HEAD").write_text("ref: refs/heads/main", encoding="utf-8")
    (dst / ".env").write_text("SECRET=123", encoding="utf-8")

    return src, dst


def test_smart_sync_excludes_and_keeps_target_files(sync_env, monkeypatch):
    src, dst = sync_env

    # 模擬 settings 中的路徑
    class MockConfig:
        path = src

    class MockSettings:
        system_a = MockConfig()
        system_b = MockConfig()
        sync = type("obj", (object,), {"exclude_patterns": ["__pycache__", ".git", ".env"]})

    # 我們需要讓 getattr(settings, "system_a").path 回傳我們的測試路徑
    monkeypatch.setattr("orchestrator.sync.settings.system_a", type("obj", (object,), {"path": src}))
    monkeypatch.setattr("orchestrator.sync.settings.system_b", type("obj", (object,), {"path": dst}))
    monkeypatch.setattr("orchestrator.sync.settings.sync", type("obj", (object,), {"exclude_patterns": [".git", ".env"]}))

    syncer = Syncer()
    success = syncer.sync("a", "b")

    assert success is True

    # 檢查檔案是否同步
    assert (dst / "app.py").exists()
    assert (dst / "data" / "config.json").exists()

    # 檢查排除檔案是否被保留且未被刪除
    assert (dst / ".git" / "HEAD").exists()
    assert (dst / ".env").exists()
    assert (dst / ".env").read_text() == "SECRET=123"


def test_incremental_sync(sync_env, monkeypatch):
    src, dst = sync_env
    monkeypatch.setattr("orchestrator.sync.settings.system_a", type("obj", (object,), {"path": src}))
    monkeypatch.setattr("orchestrator.sync.settings.system_b", type("obj", (object,), {"path": dst}))
    monkeypatch.setattr("orchestrator.sync.settings.sync", type("obj", (object,), {"exclude_patterns": []}))

    syncer = Syncer()

    # 第一次同步
    syncer.sync("a", "b")
    mtime_before = os.path.getmtime(dst / "app.py")

    # 修改 A 的內容
    import time

    time.sleep(0.1)  # 確保 mtime 不同
    (src / "app.py").write_text("print('hello v2')", encoding="utf-8")

    # 第二次同步
    syncer.sync("a", "b")
    mtime_after = os.path.getmtime(dst / "app.py")

    assert mtime_after > mtime_before
    assert (dst / "app.py").read_text() == "print('hello v2')"
