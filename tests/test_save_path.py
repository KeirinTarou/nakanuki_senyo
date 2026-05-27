from pathlib import Path

def test_save_path_load_image_sets_src_path(
        tk_root, monkeypatch, patch_image_dependencies, mock_file_dialog):
    """ ファイルダイアログからファイルパスを受け取ることができる"""
    from src.nakanuki_gui.main import NakanukiApp
    app = NakanukiApp(tk_root)

    monkeypatch.setattr(app.canvas, "delete", lambda *a, **k: None)
    monkeypatch.setattr(app.canvas, "create_image", lambda *a, **k: None)

    app.load_image()
    # NakanukiAppのsrc_pathとテスト用ファイルのパスが一致するはず
    assert app.src_path == mock_file_dialog

def test_save_path_save_uses_src_directory(
        tk_root, monkeypatch, patch_image_dependencies, mock_file_dialog):
    from src.nakanuki_gui.main import NakanukiApp
    app = NakanukiApp(tk_root)

    monkeypatch.setattr(app.canvas, "delete", lambda *a, **k: None)
    monkeypatch.setattr(app.canvas, "create_image", lambda *a, **k: None)

    app.src_path = mock_file_dialog

    class DummyImage:
        def convert(self, mode):
            return self
        filename = str(mock_file_dialog)

    app.original_image = DummyImage()

    # 必要なUIパーツ群
    app.spin_from = type("", (), {"get": lambda self: "10"})()
    app.spin_to = type("", (), {"get": lambda self: "20"})()
    app.var_add_break_line = type("", (), {"get": lambda self: False})()

    # 保存パス取得
    saved_path = {}

    def fake_save(path):
        saved_path["path"] = path

    class DummyOut:
        def save(self, path):
            fake_save(path)

    monkeypatch.setattr(
        "src.nakanuki_gui.main.nakanuki_image", 
        lambda *a, **k: DummyOut())
    
    # 実行
    app.nakanuki_and_save()

    # 保存ファイルの親フォルダが元ファイルの親フォルダと一致するはず
    assert saved_path["path"].parent == mock_file_dialog.parent
    