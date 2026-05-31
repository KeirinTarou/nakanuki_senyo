def test_apply_nakanuki_updates_spinbox_max(
        tk_root, monkeypatch):
    from src.nakanuki_gui.main import NakanukiApp
    app = NakanukiApp(tk_root)

    class DummyImage:
        size = (100, 100)

    class DummyOutImage:
        size = (100, 70)

    class DummySpinbox:
        def __init__(self, value):
            self.value = value
            self.max_value = None

        def get(self):
            return self.value
        
        def config(self, **kwargs):
            self.max_value = kwargs.get("to")

    app.original_image = DummyImage()
    app.spin_from = DummySpinbox("10")
    app.spin_to = DummySpinbox("20")
    app.var_add_break_line = \
        type("", (), {"get": lambda self: False})()
    
    monkeypatch.setattr(
        app, 
        "_show_image_on_canvas", 
        lambda img: None
    )
    
    monkeypatch.setattr(
        app, 
        "_nakanuki_exec", 
        lambda: DummyOutImage()
    )

    monkeypatch.setattr(
        app, 
        "update_lines", 
        lambda: None
    )

    app.apply_nakanuki()

    assert app.spin_from.max_value == 70
    assert app.spin_to.max_value == 70