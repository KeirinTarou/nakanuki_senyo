def test_apply_nakanuki_updates_spinbox_max(
        tk_root, monkeypatch, 
        dummy_image, dummy_out_image, dummy_spinbox, dummy_boolean_var):
    """ 「中抜き適用」ボタンクリック -> スピンボックスの最大値更新"""
    from src.nakanuki_gui.main import NakanukiApp
    app = NakanukiApp(tk_root)
    # 元画像をダミーに差し替え
    app.original_image = dummy_image
    # スピンボックスをダミーに差し替え
    #   -> From: 10, To: 40にセットしてあることにする
    app.spin_from = dummy_spinbox("10")
    app.spin_to = dummy_spinbox("40")
    # ｢省略線追加」チェックボックスがオフの状態を偽装
    app.var_add_break_line = dummy_boolean_var
    
    # NakanukiApp.load_image()内で呼ばれる_show_image_on_canvas()を差し替え
    monkeypatch.setattr(
        app, 
        "_show_image_on_canvas", 
        lambda img: None
    )
    # 「中抜適用」、「中抜き！」時に呼ばれる_exec_nakanuki()を差し替え
    #   -> 何もせずにダミー中抜後画像を返すだけにする
    monkeypatch.setattr(
        app, 
        "_nakanuki_exec", 
        lambda: dummy_out_image()
    )
    # 水平線を更新するupdate_lines()を差し替え
    monkeypatch.setattr(
        app, 
        "update_lines", 
        lambda: None
    )
    # 中抜き実行
    #   -> `NakanukiApp.apply_nakanuki()`メソッドのうち、スピンボックスの
    #       最大値更新処理だけが実際に行われる
    app.apply_nakanuki()
    # ダミー中抜後画像の高さは70 -> スピンボックス最大値は70になるはず
    assert app.spin_from.max_value == 70
    assert app.spin_to.max_value == 70

def test_apply_nakanuki_updates_current_height(
        tk_root, monkeypatch, dummy_image, dummy_out_image, dummy_spinbox):
    """ ｢中抜適用｣ボタンクリック -> 画像の高さ更新"""
    from src.nakanuki_gui.main import NakanukiApp
    app = NakanukiApp(tk_root)

    app.original_image = dummy_image
    app.spin_from = dummy_spinbox("10")
    app.spin_to = dummy_spinbox("20")
    app.var_add_break_line = \
        type("", (), {"get": lambda self: False})()
    
    # _show_image_on_canvas()乗っ取り
    monkeypatch.setattr(
        app, 
        "_show_image_on_canvas", 
        lambda img: None
    )
    # _nakanuki_exec()乗っ取り
    monkeypatch.setattr(
        app, 
        "_nakanuki_exec", 
        lambda: dummy_out_image()
    )
    # update_lines()乗っ取り
    monkeypatch.setattr(
        app, 
        "update_lines", 
        lambda: None
    )
    # apply_nakanuki()実行
    app.apply_nakanuki()

    # ラベルに表示される画像高さは中抜き後の70のはず
    assert app.var_height.get() == "Height: 70 px"