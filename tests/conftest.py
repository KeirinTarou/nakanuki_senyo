import tkinter as tk
import pytest
from unittest.mock import patch

@pytest.fixture
def tk_root(monkeypatch):
    # iconbitmap無効化
    monkeypatch.setattr(
        tk.Tk, "iconbitmap", lambda self, *a, **k: None)
    root = tk.Tk()
    root.withdraw()
    yield root
    root.destroy()

# ImageProcessorを偽装
class DummyImage:
    size = (100, 200)

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
    size = (100, 70)

@pytest.fixture
def dummy_image():
    return DummyImage

@pytest.fixture
def dummy_out_image():
    return DummyOutImage

@pytest.fixture
def dummy_proc():
    return DummyProc

@pytest.fixture
def patch_image_dependencies(monkeypatch, dummy_proc):
    monkeypatch.setattr(
        "src.nakanuki_gui.main.ImageProcessor", dummy_proc)
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
