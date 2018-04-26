"""
Discord bot - Luke
"""
import os
import json
import asyncio
import discord
from routing.mapper import automatch
from msgs import msgpatterns
from redisdb import REDISDB
import botutils


REDISDB_CONF = {
    'AUTOYEET': dict()
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
    await client.edit_profile(username='TheRobot')
    # TODO: Resume any polls, yeeting
    yeetdb = json.loads(REDISDB.get('AUTOYEET').decode())
    yeet_coros = []
    for entry in yeetdb:
        if yeetdb[entry]:
            yeet_coros.append(botutils.autoyeet_loop_channelid(client, entry))
    await asyncio.gather(*yeet_coros)


@client.event
async def on_message(message: discord.Message):
    func = automatch(msgpatterns, message.content)
    if func:
        await func(client, message)
    elif not callable(func) and message.content.startswith('$'):
        await client.send_message(message.channel,
                                  'The command you tried to invoke was not '
                                  'found\nThe below regex patterns were '
                                  'searched in the following order:\n\n' +
                                  '\n'.join(x.d_pattern for x in msgpatterns))


client.run(os.environ.get('bot_key'))
