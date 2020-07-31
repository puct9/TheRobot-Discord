import asyncio
import json
import os
import re

import aiohttp
import discord

from redisdb import REDISDB
from routing.mapper import Endpoint
from .c4game import C4Game

SERVER_ENDPOINT = os.environ['c4_endpoint']


async def aio_get(session: aiohttp.ClientSession, url):
    async with session.get(url) as resp:
        return await resp.text()


async def request_pos_info(position_string):
    url = SERVER_ENDPOINT + position_string
    async with aiohttp.ClientSession() as sess:
        resp = await aio_get(sess, url)
    return json.loads(resp)


def get_user_game_info(user_id):
    # user_id obtained from author.mention
    data = json.loads(REDISDB.get('con4').decode())
    game = data.get(user_id)
    if game is None:
        return
    return C4Game.deserialise(game)


@Endpoint
async def new_game(client: discord.Client,
                   message: discord.Message):
    """
    User wants to start a new game with the bot
    """
    game = C4Game()
    serialised = game.serialise()
    db_data = json.loads(REDISDB.get('con4').decode())
    db_data[message.author.mention] = serialised
    REDISDB.set('con4', json.dumps(db_data).encode())
    await message.channel.send('New game!\n' +
                               game.discord_message())


@Endpoint
async def load_game(client: discord.Client,
                    message: discord.Message):
    game = get_user_game_info(message.author.mention)
    if game is None:
        await message.channel.send('No active game found')
        return
    await message.channel.send('Loaded!\n' + game.discord_message())


@Endpoint
async def process_move(client: discord.Client,
                       message: discord.Message):
    # user made a move now we pwn them
    game = get_user_game_info(message.author.mention)
    if game is None:
        await message.channel.send('Game not found')
        return
    re_match = re.match(r'^\$c4 move ([A-Ga-g])$', message.content)
    move = re_match.group(1).lower()
    move = 'abcdefg'.index(move)
    legals = game.legal_moves()
    if not legals[move]:
        await message.channel.send('Bad move')
        return
    game.play_move(move)
    serialised = game.serialise()
    db_data = json.loads(REDISDB.get('con4').decode())
    db_data[message.author.mention] = serialised
    REDISDB.set('con4', json.dumps(db_data).encode())
    await message.channel.send(f'You move to column {move + 1}\n' +
                               game.discord_message())


@Endpoint
async def ai_move(client: discord.Client,
                  message: discord.Message):
    game = get_user_game_info(message.author.mention)
    if game is None:
        await message.channel.send('Game not found')
        return
    if game.check_terminal() is not None:
        await message.channel.send('Game has ended')
        return
    # generate game string
    url = game.string_serialise()
    res = await request_pos_info(game.string_serialise())
    if not res['success'] or not res['moves']:
        await message.channel.send('Search failure')
        return
    move_data = res['moves']
    move_data.sort(key=lambda x: x['visits'], reverse=True)
    best_move = move_data[0]['move']
    game.play_move(best_move)
    serialised = game.serialise()
    db_data = json.loads(REDISDB.get('con4').decode())
    db_data[message.author.mention] = serialised
    REDISDB.set('con4', json.dumps(db_data).encode())
    move_str = ':regional_indicator_' + 'abcdefg'[best_move] + ':'
    await message.channel.send(f'Search complete! Moved to {move_str}\n' +
                               game.discord_message())


@Endpoint
async def test(client: discord.Client,
               message: discord.Message):
    msg = C4Game.deserialise(C4Game().serialise()).discord_message()
    await message.channel.send(msg)
