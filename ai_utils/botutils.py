import io
import re
from string import ascii_uppercase

import discord
import numpy as np
import PIL
import httpx
from keras.models import load_model
from keras.utils import model_to_dot
from PIL import Image
from routing.mapper import Endpoint

GENDER = load_model('./ai_utils/gender.hdf5', compile=False)
DIGITS = load_model('./ai_utils/mnist.hdf5', compile=False)


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
    male, female = GENDER.predict(name)[0]
    await message.channel.send(f'Name {inp} is\n'
                               f'Male: {round(float(male * 100))}%\n'
                               f'Female: {round(float(female * 100))}%')


@Endpoint
async def get_summary_gender(client: discord.Client,
                             message: discord.Message):
    """
    Message the graph
    """
    msg = []
    GENDER.summary(print_fn=msg.append)
    await message.channel.send('Model\n```' + '\n'.join(msg) + '```')


@Endpoint
async def get_visualisation_gender(client: discord.Client,
                                   message: discord.Message):
    """
    Message the visual representation of the graph
    """
    dot = model_to_dot(GENDER, show_shapes=True)
    image_bytes = dot.create(format='png')
    await message.channel.send(
        file=discord.File(io.BytesIO(image_bytes),
                          filename='model.png')
    )


@Endpoint
async def predict_digit(client: discord.Client,
                        message: discord.Message):
    """
    Predict the digit in the image
    """
    if len(message.attachments) != 1:
        await message.channel.send('Please attach an image with the message '
                                   'with a digit in black on a white background')
        return
    try:
        async with httpx.AsyncClient() as client:
            req = await client.get(message.attachments[0].url)
    except Exception:
        await message.channel.send('Unable to download image')
        return
    try:
        img = Image.open(io.BytesIO(req.content))
    except PIL.UnidentifiedImageError:
        await message.channel.send('Unable to load image')
        return
    img = img.convert('L').resize((28, 28))
    img_arr = np.array(img)
    img_arr = np.expand_dims(img_arr, -1) / 255
    img_arr = np.expand_dims(img_arr, 0)
    probs = DIGITS.predict(img_arr)[0]
    pred = np.argmax(probs)
    conf = int(round(probs[pred] * 100))
    await message.channel.send(f'I\'m {conf}% sure that\'s {pred}!')


@Endpoint
async def get_summary_digit(client: discord.Client,
                            message: discord.Message):
    """
    Message the graph
    """
    msg = []
    DIGITS.summary(print_fn=msg.append)
    await message.channel.send('Model\n```' + '\n'.join(msg) + '```')


@Endpoint
async def get_visualisation_digit(client: discord.Client,
                                  message: discord.Message):
    """
    Message the visual representation of the graph
    """
    dot = model_to_dot(DIGITS, show_shapes=True)
    image_bytes = dot.create(format='png')
    await message.channel.send(
        file=discord.File(io.BytesIO(image_bytes),
                          filename='model.png')
    )
