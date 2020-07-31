"""
Discord bot - Luke
"""
import asyncio
import json
import os
import sys

import discord

import botutils
from msgs import msgpatterns
from redisdb import REDISDB
from routing.mapper import automatch, check_walk

REDISDB_CONF = {
    'con4': dict()
}
for conf in REDISDB_CONF:
    if not REDISDB.get(conf):
        REDISDB.set(conf, json.dumps(REDISDB_CONF[conf]))


loop = asyncio.get_event_loop()
client = discord.Client(loop=loop)


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    await client.user.edit(username='TheRobot')


@client.event
async def on_message(message: discord.Message):
    func = automatch(msgpatterns, message.content)
    if func:
        await func(client, message)
    elif not callable(func) and message.content.startswith('$'):
        await message.channel.send('The command you tried to invoke was not '
                                  'found\nThe below regex patterns were '
                                  'searched in the following order:\n\n' +
                                  '\n'.join(x.d_pattern
                                            for x in endpoint_patterns))


endpoint_patterns = list(check_walk(msgpatterns))

if __name__ == '__main__':
    client.run(os.environ.get('bot_key'))
