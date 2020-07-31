import asyncio
import json
import random
import re
import time
from datetime import timedelta
from typing import Tuple

import discord
from num2words import num2words

from redisdb import REDISDB
from routing.mapper import Endpoint


@Endpoint
async def poll(client: discord.Client,
               message: discord.Message) -> Tuple[str, str]:
    # Regex stuff
    re_match = re.match(r'^\$poll (\d{1,4}) (.+)', message.content)
    seconds = int(re_match.group(1))
    prompt = re_match.group(2)
    channel = message.channel

    try:
        # delete previous command
        await client.delete_message(message)
    except discord.errors.Forbidden:
        # missing permissions
        pass

    td = lambda s: str(timedelta(seconds=int(s)))

    embed = discord.Embed(title='Poll', description=prompt +
                          '\nUse :thumbsup: or :thumbsdown: to vote!' +
                          f'\nPoll finalizes in {td(seconds)}')
    poll_msg = await message.channel.send(embed=embed)
    # Show how much seconds the poll has got
    rem_seconds = seconds
    poll_seconds_refresh = 5
    while rem_seconds >= poll_seconds_refresh:
        await asyncio.sleep(poll_seconds_refresh)
        rem_seconds -= poll_seconds_refresh
        embed = discord.Embed(title='Poll', description=prompt +
                              '\nUse :thumbsup: or :thumbsdown: to vote!' +
                              f'\nPoll finalizes in {td(rem_seconds)}')
        ctime = time.time()
        poll_msg = await poll_msg.edit(poll_msg, embed=embed)
        deltatime = time.time() - ctime
        rem_seconds -= deltatime
    if rem_seconds > 0:
        await asyncio.sleep(rem_seconds)
    # Poll finalized
    poll_msg = await discord.abc.Messageable.fetch_message(poll_msg.id)
    yes = 0
    no = 0
    for r in poll_msg.reactions:
        r: discord.Reaction
        print(r.emoji)
        if r.emoji == '👍':
            yes = r.count
        if r.emoji == '👎':
            no = r.count
    embed = discord.Embed(title='Poll', description=prompt +
                          '\nUse :thumbsup: or :thumbsdown: to vote!' +
                          f'\nPoll has been finished, results are final.' +
                          f'\n\nYes: {yes}\nNo: {no}')
    await poll_msg.edit(poll_msg, embed=embed)


@Endpoint
async def num_convert_word(client: discord.Client,
                           message: discord.Message):
    re_match = re.match(r'^\$word (\d{1,308})( [a-zA-Z_]{0,5})?',
                        message.content)
    num = re_match.group(1)
    locale = re_match.group(2)
    if int(num) >= int('1' + '0' * 306):  # floating point precision
        word = 'Number must be less than 1' + '0' * 306
    else:
        if locale is not None:
            try:
                word = num2words(int(num), lang=locale.strip())
            except NotImplementedError:
                word = 'Unsupported language'
        else:
            word = num2words(int(num))
    # Special cases
    spec_cases = {
        '69': 'NSFW!',
        '420': 'Trees',
        '666': 'o_O',
        '1337': 'WOW UR COOL',
    }
    if num in spec_cases:
        word += ' ' + spec_cases[num]
    try:
        await message.channel.send(word)
    except discord.errors.HTTPException:
        await message.channel.send('Resulting text was too '
                                   'long to send!')


@Endpoint
async def reminder(client: discord.Client,
                   message: discord.Message):
    re_match = re.match(r'^\$reminder (\d+) (.+)', message.content)
    seconds = re_match.group(1)
    reminder_text = re_match.group(2)
    await message.channel.send(f'Reminder `{reminder_text}`'
                               ' has been set.')
    await asyncio.sleep(int(seconds))
    await message.channel.send(f'{message.author.mention}'
                               f' {reminder_text}')
