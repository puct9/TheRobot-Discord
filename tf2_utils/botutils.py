import asyncio
import os
import subprocess

import discord

from routing.mapper import Endpoint
from .utils import parse_game_info
from .utils import get_player_info as raw_get_player_info


TF2_ADDR = os.environ.get('tf2_addr')

# allow arbitrary ports
SUBPROC_PORTS = {port: True for port in range(30000, 30050)}


@Endpoint
async def get_player_info(client: discord.Client,
                          message: discord.Message):
    """
    How many players are on my server?
    """
    # which port do we want to use?
    if not any(SUBPROC_PORTS.values()):
        await client.send_message(message.channel, 'The server is busy. '
                                                   'Please try again later.')
        return

    for port, available in SUBPROC_PORTS.items():
        if available:
            SUBPROC_PORTS[port] = False
            break
    # this process is clever and will manage itself
    # we don't have to shut it down manually
    subprocess.Popen(['python', './tf2_utils/tf2gamequery.py', str(port)])

    try:
        reader, writer = await asyncio.open_connection(host='127.0.0.1',
                                                       port=port)
        writer.write(TF2_ADDR.encode())
        await writer.drain()
        info = await reader.read()
        SUBPROC_PORTS[port] = True  # released the port by now
    except Exception:
        SUBPROC_PORTS[port] = True
        # fallback to non-async method
        addr = TF2_ADDR.split(':')
        addr[1] = int(addr[1])
        info = raw_get_player_info(tuple(addr))

    player_info = parse_game_info(info)
    msg = 'Players currently on the server\n```\n'
    if player_info:
        msg += '\n'.join(f'{player[0]} - {player[1]}' for player in player_info)
    else:
        msg += 'There are currently no players.'
    msg += '\n```'

    await client.send_message(message.channel, msg)
