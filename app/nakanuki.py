from PIL import Image

def nakanuki_image(
        img: Image.Image, 
        y_from: int, 
        y_to: int) -> Image.Image:
    """ 中抜き後のImage.Imageオブジェクトを返す
    
    :param img: 中抜き前のImage.Imageオブジェクト
    :type img: Image.Image
    :param y_from: 中抜き開始座標
    :type y_from: int
    :param y_to: 中抜き終了座標
    :type y_to: int
    :return: 中抜き後のImage.Imageオブジェクト
    :rtype: Image.Image
    """
    if y_from >= y_to:
        raise ValueError("y_from must be less than y_to.")
    
    w, h = img.size

    y_from = max(0, min(y_from, h))
    y_to = max(0, min(y_to, h))

    top = img.crop((0, 0, w, y_from))
    bottom = img.crop((0, y_to, w, h))

    new_h = top.height + bottom.height
    out = Image.new(img.mode, (w, new_h))

    out.paste(top, (0, 0))
    out.paste(bottom, (0, top.height))

    return out