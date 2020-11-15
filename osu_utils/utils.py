import os
import io
import random

import httpx
import numpy as np
from PIL import Image, ImageDraw, ImageFont


API_KEY = os.environ.get('osu_api_key')


async def osu_getuserinfo(name: str) -> dict:
    async with httpx.AsyncClient() as client:
        ret = await client.get('https://osu.ppy.sh/api/get_user',
                               params={'k': API_KEY, 'u': name})
    return ret.json()


async def osu_drawuserinfo(info: dict) -> Image.Image:
    # first we do some basic styling
    img_arr = np.zeros((120, 300, 3), dtype='uint8')
    img_arr[:, :, :] = 25  # background colour
    # before we go any further, let's paste the user's profile pic in
    print('waiting for profile pic')
    print(f'https://a.ppy.sh/{info["user_id"]}')
    try:
        async with httpx.AsyncClient() as client:
            req = await client.get(f'https://a.ppy.sh/{info["user_id"]}',
                                   timeout=2)
    except Exception:
        # there is a rare error where some images simply will not download
        # not ideal solution, but we will try to give what the user wants
        async with httpx.AsyncClient() as client:
            req = await client.get(f'https://a.ppy.sh')
    print('done')
    profile_pic = Image.open(io.BytesIO(req.content))
    # resize it to the desired size of 112x112 and do some checks
    profile_pic = profile_pic.convert('RGB').resize((112, 112))
    profile_pic_arr = np.array(profile_pic)
    # do some padding on the thing
    overlay_arr = np.zeros((120, 300, 3), dtype='uint8')
    overlay_arr[:, :, :] = 25
    overlay_arr[4:116, 4:116] = profile_pic_arr
    # # use pillow to overlay the img_arr and overlay_arr, with the profile pic
    # img_back = Image.fromarray(img_arr).convert('RGBA')
    # img_over = Image.fromarray(overlay_arr).convert('RGBA')
    # img_done = Image.blend(img_back, img_over, alpha=0.4)
    # # we are done. convert back
    # img_done.convert('RGB')
    # img_arr = np.array(img_done)
    # draw a fancy line
    img_arr = (img_arr * 0.70 + overlay_arr * 0.30).astype('uint8')
    # or do as the line above
    img_arr[33, 10:290, :] = 127
    # draw another fancy line
    img_arr[107:112, 10:290, :] = 255
    # and another one, in a fancy colour, to show progress through level
    level = str(int(float(info['level'])))
    percent_prog = float(info['level']) - float(level)
    colour = random.choice([
        (237, 28, 36),  # red-ish
        (0, 143, 198),  # blue-ish
        (255, 128, 0),  # orange-ish
        (83, 0, 166),  # purple-ish
        (255, 71, 197),  # pink-ish
    ])
    img_arr[108:111, 11:11 + int(278 * percent_prog)] = colour
    # touching up
    img_arr[107:112, 115:185, :] = 25
    img_arr[107:112, (114, 185), :] = 255
    # convert into pillow image
    img = Image.fromarray(img_arr)
    draw = ImageDraw.Draw(img)
    font_rank = ImageFont.truetype(os.path.join(os.getcwd(),
                                                'osu_utils/Roboto-Regular.ttf'
                                                ), 60)
    font_title = ImageFont.truetype(os.path.join(os.getcwd(),
                                                 'osu_utils/Roboto-Regular.ttf'
                                                 ), 24)
    font_basic = ImageFont.truetype(os.path.join(os.getcwd(),
                                                 'osu_utils/Roboto-Regular.ttf'
                                                 ), 18)
    font_small = ImageFont.truetype(os.path.join(os.getcwd(),
                                                 'osu_utils/Roboto-Regular.ttf'
                                                 ), 14)
    rank_w, rank_h = draw.textsize(f'#{info["pp_rank"]}', font=font_rank)
    draw.text((299 - rank_w, 101 - rank_h), f'#{info["pp_rank"]}',
              (70, 70, 70), font=font_rank)
    draw.text((15, 3), info['username'], (250, 250, 250), font=font_title)
    # write most of the info
    draw.text((15, 40), 'Performance Points\nPlay Count\nAccuracy',
              (250, 250, 250), font=font_basic)
    # try to avoid floating point rounding error by adding a little bit
    info_w, _ = draw.textsize(f'{round(float(info["pp_raw"]) + 0.0000001)}'
                              f'pp\n{info["playcount"]}\n'
                              f'{format(float(info["accuracy"]), ".2f")}%',
                              font=font_basic)
    draw.text((285 - info_w, 40), f'{round(float(info["pp_raw"]) + 0.0000001)}'
              f'pp\n{info["playcount"]}\n'
              f'{format(float(info["accuracy"]), ".2f")}%',
              font=font_basic, align='right')
    # write the level
    level_w, level_h = draw.textsize(level, font=font_small)
    draw.text((150 - level_w // 2, 107 - level_h // 2), level,
              (250, 250, 250), font=font_small)
    return img
