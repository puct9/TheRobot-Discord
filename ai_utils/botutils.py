import re
from string import ascii_uppercase

import discord
import numpy as np
from keras.models import load_model

from routing.mapper import Endpoint


MODEL = load_model('./ai_utils/model.hdf5', compile=False)


@Endpoint
async def predict_gender(client: discord.Client,
                         message: discord.Message):
    """
    Predict the gender of a name
    """
    re_match = re.match(r'^\$ai gender ([a-zA-Z]{1,16})$', message.content)
    inp = re_match.group(1)
    try:
        name = np.array([[ascii_uppercase.index(c.upper()) for c in inp] +
                         [26] * (16 - len(inp))])
    except ValueError:
        await message.channel.send('An error has occurred')
    male, female = MODEL.predict(name)[0]
    await message.channel.send(f'Name {inp} is\n'
                               f'Male: {round(float(male * 100))}%\n'
                               f'Female: {round(float(female * 100))}%')


@Endpoint
async def get_summary(client: discord.Client,
                      message: discord.Message):
    """
    Message the graph
    """
    msg = []
    MODEL.summary(print_fn=msg.append)
    await message.channel.send('Model\n```' + '\n'.join(msg) + '```')
