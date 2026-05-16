# TODO:
#   ✅- import構造が壊れていない
#   ✅- nakanukiモジュールのnakanuki_image()が呼べる
#   ✅- mainモジュールのNakanukiAppクラスが読める

def test_import_structure():
    """ import構造が壊れていない"""
    import src
    import src.nakanuki_core
    import src.nakanuki_gui

def test_import_module_src_nakanuki_core_nakanuki_image():
    """ nakanukiモジュールのnakanuki_image()が呼べる"""
    from src.nakanuki_core.nakanuki import nakanuki_image
    assert callable(nakanuki_image)

def test_import_module_src_nakanuki_gui_main_NakanukiApp():
    """ mainモジュールのNakanukiAppクラスが読める"""
    from src.nakanuki_gui.main import NakanukiApp