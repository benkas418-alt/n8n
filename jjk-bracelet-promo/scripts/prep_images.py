"""Crop and rotate the source images that the composition uses."""
from PIL import Image

D = 'assets/img/'


def crop(src, dst, box):
    Image.open(D + src).convert('RGB').crop(box).save(D + dst, quality=92)


crop('gojo_sheet.png', 'gojo_strip.jpg', (40, 548, 1336, 684))
crop('spec_sheet.png', 'toji_strip_out.jpg', (143, 637, 1321, 709))
crop('spec_sheet.png', 'toji_strip_in.jpg', (143, 865, 1321, 936))
crop('toji_bracelet.png', 'toji_panel.jpg', (170, 30, 1510, 900))
crop('toji_manga_eyes.jpg', 'toji_eyes.jpg', (16, 196, 726, 376))
crop('toji_manga_eyes.jpg', 'toji_back.jpg', (60, 560, 700, 1308))
Image.open(D + 'gojo_anime_hand.jpg').rotate(90, expand=True).save(D + 'gojo_hand_up.jpg', quality=92)
Image.open(D + 'gojo_glasses.jpg').rotate(-90, expand=True).crop((380, 0, 1308, 600)).save(D + 'gojo_glasses_up.jpg', quality=92)
