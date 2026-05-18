from src.nakanuki_gui.main import NakanukiApp

# TODO:
#   ✅- 幅・高さともにキャンバスよりも大きい
#   ✅- 幅・高さともにキャンバスよりも小さい
#   ✅- 幅がキャンバスよりも大きい
#   ✅- 高さがキャンバスよりも大きい

def test__calc_horizontal_line_coords_larger_than_canvas():
    """ w, hともにキャンバスよりも大きい"""
    line1, line2 = \
        NakanukiApp._calc_horizontal_line_coords(
            canvas_size=(600, 400), 
            img_pixel_size=(900, 600), 
            display_scale=2 / 3, 
            y_from=180, 
            y_to=360)
    assert line1 == (0, 120, 600, 120)
    assert line2 == (0, 240, 600, 240)

def test__calc_horizontal_line_coords_smaller_than_canvas():
    """ w, hともにキャンバスよりも小さい"""
    line1, line2 = \
        NakanukiApp._calc_horizontal_line_coords(
            canvas_size=(600, 400), 
            img_pixel_size=(400, 300), 
            display_scale=1.0, 
            y_from=100, 
            y_to=200)
    assert line1 == (0, 150, 600, 150)
    assert line2 == (0, 250, 600, 250)

def test__calc_horizontal_line_coords_w_larger_than_canvas():
    """ wがキャンバスよりも大きい"""
    line1, line2 = \
        NakanukiApp._calc_horizontal_line_coords(
            canvas_size=(600, 400), 
            img_pixel_size=(800, 200), 
            # 幅を表示領域に収めようとする
            display_scale=3 / 4, 
            y_from=50, 
            y_to=100)
    assert line1 == (0, 137, 600, 137)
    assert line2 == (0, 175, 600, 175)

def test__calc_horizontal_line_coords_h_larger_than_canvas():
    """ hがキャンバスよりも大きい"""
    line1, line2 = \
        NakanukiApp._calc_horizontal_line_coords(
            canvas_size=(600, 400), 
            img_pixel_size=(400, 800), 
            # 高さを表示領域に収めようとする
            display_scale=1 / 2, 
            y_from=300, 
            y_to=500)
    assert line1 == (0, 150, 600, 150)
    assert line2 == (0, 250, 600, 250)
