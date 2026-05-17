from src.nakanuki_gui.main import NakanukiApp

def test__calc_horizontal_line_coods_normal():
    line1, line2 = \
        NakanukiApp._calc_horizontal_line_coords(
            img_display_size=(600, 400), 
            img_pixel_size=(900, 600), 
            display_scale=2 / 3, 
            y_from=180, 
            y_to = 360)
    
    assert line1 == (0, 120, 600, 120)
    assert line2 == (0, 240, 600, 240)
