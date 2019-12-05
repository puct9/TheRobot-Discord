import asyncio
import os

import discord

from routing.mapper import Endpoint


MC_ADDR = os.environ.get('mc_addr')


@Endpoint
async def is_server_up(client: discord.Client,
                       message: discord.Message):
    """
    Is my Minecraft server up??
    """
    reader, _ = await asyncio.open_connection(host=MC_ADDR, port=6969)
    recv = await reader.read()
    recv = recv.decode()
    if recv == 'Yes\n':
        msg = f'The server `{MC_ADDR}` is UP'
    else:
        msg = f'The server `{MC_ADDR}` is DOWN'
    await client.send_message(message.channel, msg)
