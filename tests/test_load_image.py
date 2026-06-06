# NakanukiApp.load_image()メソッドの機能を保証するテスト

# TODO: 
#   - 画像読み込みとともにUIの各パラメータが適切にセットされる
#   - 元画像が読み込まれる
#   - 画像高さ表示ラベルが更新される
#   - 「From」、「To」スピンボックスの最大値が更新される
#   - 画像をキャンバスに表示する内部メソッド_show_image_on_canvas()が呼ばれる
#   - 中抜き位置を表示する水平線を更新するupdate_lines()が呼ばれる
#   - 空のファイル名が渡されたときにキャンセルされる

def test_load_image_updates_ui(
        tk_root, monkeypatch, patch_load_image_dependencies):
    pass