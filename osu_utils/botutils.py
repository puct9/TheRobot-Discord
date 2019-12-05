import io
import re

import discord

from routing.mapper import Endpoint
from .utils import osu_drawuserinfo, osu_getuserinfo


@Endpoint
async def osu_userinfo(client: discord.Client,
                       message: discord.Message):
    """
    Get user info for an osu player through osu API
    """
    re_match = re.match(r'^\$osu user (.+)', message.content)
    user_name = re_match.group(1)
    info = await osu_getuserinfo(user_name)
    if not info:
        await client.send_message(message.channel, 'User not found!')
        return
    image = await osu_drawuserinfo(info[0])
    image_bytes = io.BytesIO()
    image.save(image_bytes, format='png')
    await client.send_file(message.channel, io.BytesIO(image_bytes.getvalue()),
                           filename='stats.png')
