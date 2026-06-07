from src.nakanuki_gui.main import NakanukiApp

# NakanukiApp.load_image()メソッドの機能を保証するテスト

# TODO: 
#   ✅- 画像読み込みとともにUIの各パラメータが適切にセットされる
#       ✅- 元画像が読み込まれる
#       ✅- 画像高さ表示ラベルが更新される
#       ✅- 「From」、「To」スピンボックスの最大値が更新される
#       ✅- 画像をキャンバスに表示する内部メソッド_show_image_on_canvas()が呼ばれる
#       ✅- 中抜き位置を表示する水平線を更新するupdate_lines()が呼ばれる
#   ✅- 空のファイル名が渡されたときにキャンセルされる

def test_load_image_updates_ui(
        tk_root, monkeypatch, 
        patch_load_image_dependencies, mock_file_dialog):
    # テスト用のtkinter.Tkインスタンスを用いてNakanukiAppインスタンス取得
    app = NakanukiApp(tk_root)
    # 内部メソッドが呼ばれたかどうかを記録するフラグ
    #   - show: _show_image_on_canvas()
    #   - update: update_lines()
    called = {"show": False, "update": False, }
    # _show_image_on_canvas()メソッドを偽装
    #   -> called["show"]をTrueにするメソッドに差し替える
    monkeypatch.setattr(
        app, 
        "_show_image_on_canvas", 
        lambda img: called.__setitem__("show", True)
    )
    # update_lines()メソッドを偽装
    #   -> called["update"]をTrueにするメソッドに差し替える
    monkeypatch.setattr(
        app, 
        "update_lines", 
        lambda: called.__setitem__("update", True)
    )
    # load_image()メソッドを呼ぶ
    #   - 次の2つのフィクスチャが働く
    #   - mock_file_dialog()
    #       - ユーザが`sample.png`を選択した状態を再現
    #   - patch_load_image_dependencies()
    #       - ImageProcessorをDummyProcに差し替え
    #       - DummyProcはDummyImageインスタンスを返す
    #  - 結果的にload_image()実行により、
    #       - app.src_pathにテスト用一時フォルダの`sample.png`のパスが入り、
    #       - app.original_imageにDummyImageインスタンスが入る
    app.load_image()

    # 検証
    # `original_image`属性に画像がセットされているはず（Noneでない）
    assert app.original_image is not None
    # 画像高さ表示ラベルに表示する文字列がセットされているはず
    #   - DummyImageインスタンスの画像高さは200px
    assert app.var_height.get() == "Height: 200 px"
    # スピンボックスの最大値が画像高さと一致するはず
    assert int(app.spin_from["to"]) == 200
    assert int(app.spin_to["to"]) == 200
    # calledフラグはともにTrueのはず
    assert called["show"] is True
    assert called["update"] is True

def test_load_image_cancelled(tk_root, monkeypatch):
    """ 空のファイル名が渡されたときにキャンセルされる"""
    # テスト用のtkinter.Tkインスタンスを用いてNakanukiAppインスタンス取得
    app = NakanukiApp(tk_root)
    # ファイルダイアログがキャンセルされた状態を再現
    #   - filedialog.askopenfilename()が""を返すよう差し替え
    monkeypatch.setattr(
        "src.nakanuki_gui.main.filedialog.askopenfilename", 
        lambda **_: ""
    )
    # load_image()メソッド実行
    #   - 入り口のところで`not path`がTrueになるのでreturnされるはず
    app.load_image()

    # 検証
    # app.original_imageはNoneのはず
    #   - original_image属性をセットするところまで進まないはず
    assert app.original_image is None
    #  app.src_pathもNoneのはず
    assert app.src_path is None
