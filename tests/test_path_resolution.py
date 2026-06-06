import sys

import config

# 実行時のパス解決保証テスト

# TODO: 
#   ✅- コマンドライン実行時に`resources`フォルダのパス解決ができる
#   ✅- EXE実行時に`resources`フォルダのパス解決ができる

def test_path_resolution_resource_path_normal(monkeypatch):
    """ コマンドライン実行時に`resources`フォルダのパス解決ができる"""
    monkeypatch.delattr(sys, "_MEIPASS", raising=False)
    assert config.resource_path("a/b.txt") == config.RESOURCES_DIR / "a/b.txt"

def test_path_resolution_resource_path_meipass(monkeypatch, tmp_path):
    """ EXE実行時に`resources`フォルダのパス解決ができる"""
    meipass = tmp_path / "bundle"
    meipass.mkdir()
    monkeypatch.setattr(sys, "_MEIPASS", str(meipass), raising=False)
    assert config.resource_path("x/y.txt") == meipass / "x/y.txt"