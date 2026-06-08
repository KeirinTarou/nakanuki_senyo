from datetime import datetime
from src.nakanuki_gui.main import NakanukiApp

# 「中抜き！」ボタンクリック時の動作保証テスト

# TODO: 
#   ✅- 「中抜き！」ボタンクリック -> タイムスタンプ付きファイル名が生成される

class FixedDatetime:
    @classmethod
    def now(cls):
        return datetime(2026, 6, 9, 12, 34, 56)

def test_nakanuki_and_save_generates_timestamped_filename(
        tk_root, monkeypatch, tmp_path, 
        dummy_image, dummy_out_image, dummy_spinbox, dummy_boolean_var):
    """ 中抜き！」ボタンクリック -> タイムスタンプ付きファイル名生成"""
    # NakanukiAppインスタンス取得
    app = NakanukiApp(tk_root)
    # 画像を読み込んだ状態を再現
    app.src_path = tmp_path / "sample.png"
    app.original_image = dummy_image
    app.spin_from = dummy_spinbox("10")
    app.spin_to = dummy_spinbox("40")
    app.var_add_break_line = dummy_boolean_var
    # nakanuki_image()の差し替え
    #   -> DummyOutImageを返すよう差し替える
    monkeypatch.setattr(
        "src.nakanuki_gui.main.nakanuki_image", 
        lambda *a, **k:dummy_out_image
    )
    # datetime.now()の差し替え
    monkeypatch.setattr(
        "src.nakanuki_gui.main.datetime", 
        FixedDatetime
    )

    # nakanuki_and_save()実行
    app.nakanuki_and_save()

    # 検証
    # ファイル名は"sample_20260609_123456.png"のはず
    assert dummy_out_image.saved_path.name == "sample_20260609_123456.png"
    # 保存先フォルダは元画像と同じフォルダのはず
    assert dummy_out_image.saved_path.parent == tmp_path
    