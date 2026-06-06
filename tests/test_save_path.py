from pathlib import Path

from src.nakanuki_gui.main import NakanukiApp

# ファイルダイアログから正しくパスを受け取ることができることを保証するテスト

# TODO: 
#   ✅- ファイルダイアログからファイルパスを受け取ることができる
#   ✅- エクスポート先フォルダは元ファイルのフォルダと同じ

def test_save_path_load_image_sets_src_path(
        tk_root, monkeypatch, patch_load_image_dependencies, mock_file_dialog):
    """ ファイルダイアログからファイルパスを受け取ることができる"""
    # ダミーtkinter.Tkインスタンスを使ってNakanukiAppインスタンスを作る
    app = NakanukiApp(tk_root)
    # self.canvasのdelete()、create_image()を差し替え
    monkeypatch.setattr(app.canvas, "delete", lambda *a, **k: None)
    monkeypatch.setattr(app.canvas, "create_image", lambda *a, **k: None)
    # load_image()呼び出し
    #   - mock_file_dialogによってテスト用のダミーファイルのパスを取得する
    app.load_image()
    # NakanukiAppのsrc_pathとテスト用ファイルのパスが一致するはず
    assert app.src_path == mock_file_dialog

def test_save_path_save_uses_src_directory(
        tk_root, monkeypatch, 
        patch_load_image_dependencies, mock_file_dialog, 
        dummy_image, dummy_out_image, dummy_spinbox, dummy_boolean_var):
    """ エクスポート先フォルダは元ファイルのフォルダと同じ"""
    # ダミーtkinter.Tkインスタンスを使ってNakanukiAppインスタンスを作る
    app = NakanukiApp(tk_root)
    # self.canvasのdelete()、create_image()を差し替え
    monkeypatch.setattr(app.canvas, "delete", lambda *a, **k: None)
    monkeypatch.setattr(app.canvas, "create_image", lambda *a, **k: None)
    # ファイルダイアログでファイルが選択された状態を再現
    app.src_path = mock_file_dialog

    app.original_image = dummy_image
    app.original_image.filename = str(mock_file_dialog)

    # 必要なUIパーツ群
    app.spin_from = dummy_spinbox("10")
    app.spin_to = dummy_spinbox("40")
    app.var_add_break_line = dummy_boolean_var

    # nakanuki_image()が常にDummyOutImageインスタンスを返すように差し替える
    monkeypatch.setattr(
        "src.nakanuki_gui.main.nakanuki_image", 
        lambda *a, **k: dummy_out_image)

    # 実行
    app.nakanuki_and_save()

    # 保存ファイルの親フォルダが元ファイルの親フォルダと一致するはず
    assert dummy_out_image.saved_path.parent == mock_file_dialog.parent
    