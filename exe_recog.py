import log_helper
import sys
import os
from PIL import Image
import numpy as np
from screenshot import open_screenimage
from recog import Recognition as recog

if __name__ == '__main__':
    
    if len(sys.argv) < 2:
        print('Usage: python exe_recog.py <image_file>')
    else:
        filename = sys.argv[1]
        screen = open_screenimage(filename)
        img = Image.open(filename)
        result = recog.get_result(screen)

        np_value = np.array(img.crop((48, 135, 1188, 952)))
        musicname = recog.MusicSelect.get_musicname(np_value)
        print('musicname:', musicname)

        print(result.informations.music)
        print(result.informations.play_mode, result.informations.difficulty, result.informations.level, result.informations.notes)
        print(f"opt arrange:{result.details.options.arrange}, flip:{result.details.options.flip}, battle:{result.details.options.battle}, assist:{result.details.options.assist}, special:{result.details.options.special}")
        print(f'sc:{result.details.score.current}, lamp:{result.details.clear_type.current}')

