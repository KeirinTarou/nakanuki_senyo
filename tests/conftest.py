import tkinter as tk
import pytest
from unittest.mock import patch

@pytest.fixture
def tk_root(monkeypatch):
    """ テスト用のダミーtkinter.Tkインスタンスを返す"""
    # iconbitmap無効化
    monkeypatch.setattr(
        tk.Tk, "iconbitmap", lambda self, *a, **k: None)
    root = tk.Tk()
    root.withdraw()
    yield root
    root.destroy()

# ImageProcessorを偽装
class DummyImage:
    def convert(self, mode):
        return self
    filename = None
    size = (100, 200)

@pytest.fixture
def dummy_image():
    return DummyImage()

class DummyProc:
    def __init__(self, path):
        self.image = DummyImage()
    def resize_for_display(self, img, w, h):
        return img
    @staticmethod
    def calc_display_size(width, height, max_w, max_h):
        return 50, 100, 0.5

class DummyPhotoImage:
    def width(self):
        return 50
    
    def height(self):
        return 100

class DummyOutImage:
    """ nakanuki_image()の返り値を偽装するダミーImageオブジェクト"""
    size = (100, 70)
    def __init__(self):
        self.saved_path = None
    
    def save(self, path):
        self.saved_path = path

@pytest.fixture
def dummy_out_image():
    """ nakanuki_image()の返り値を偽装するダミーImageオブジェクトを返す"""
    return DummyOutImage()

class DummyBooleanVar:
    """ get()メソッドを呼んだらFalseを返すだけのクラス
    
    .. note::
    - tk.BooleanVarクラスを偽装したダミークラス
    """
    def get(self):
        return False
    
@pytest.fixture
def dummy_boolean_var():
    """ tk.BooleanVarのダミーインスタンスを返す
    
    .. note::
    - get()は常にFalseを返す
    """
    return DummyBooleanVar()

@pytest.fixture
def patch_load_image_dependencies(monkeypatch):
    """ NakanukiApp.load_image()メソッドの依存クラスをテスト用ダミーに差し替える
    
    .. note::
    - 下記依存を解消するために使う
        - load_image(): ImageProcessorに依存
        - load_image() -> _show_image_on_canvas: ImageTk.PhotoImageに依存
    """
    # ImageProcessorクラスが呼ばれたらDummyProcクラスに差し替える
    monkeypatch.setattr(
        "src.nakanuki_gui.main.ImageProcessor", DummyProc)
    # ImageTk.PhotoImageクラスはDummyPhotoImageクラスに差し替える
    monkeypatch.setattr(
        "src.nakanuki_gui.main.ImageTk.PhotoImage", 
        lambda * _: DummyPhotoImage())

class DummySpinbox:
    def __init__(self, value):
        self.value = value
        self.max_value = None

    def get(self):
        return self.value
    
    def config(self, **kwargs):
        self.max_value = kwargs.get("to")

@pytest.fixture
def dummy_spinbox():
    return DummySpinbox

@pytest.fixture
def mock_file_dialog(tmp_path):
    test_img = tmp_path / "sample.png"
    test_img.touch()

    with patch(
        "src.nakanuki_gui.main.filedialog.askopenfilename", 
        return_value=str(test_img)):
        yield test_img
