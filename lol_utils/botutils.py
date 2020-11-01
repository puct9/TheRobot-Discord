import io
import re

import discord

from routing.mapper import Endpoint
from .utils import getcms


@Endpoint
async def lol_masteries(client: discord.Client,
                        message: discord.Message):
    """
    Get LoL champion masteries of a player
    """
    re_match = re.match(r'^\$lol mastery ([a-zA-Z]{2,4}) (.{1,16})',
                        message.content)
    region = re_match.group(1)
    user_name = re_match.group(2)
    print('Going in')
    success, image_bytes = await getcms(user_name, region)
    print(success)
    if not success:
        await message.channel.send(image_bytes)
        return
    await message.channel.send(
        file=discord.File(io.BytesIO(image_bytes.getvalue()),
                          filename='masteries.png')
    )
