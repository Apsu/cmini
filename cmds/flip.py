import random
from discord import Message

RESTRICTED = False

def exec(message: Message):
    res = random.choices(
        population=['Heads', 'Tails', '🖕', 'Mail', 'Head', 'Sonic'],
        weights=   [    .46,     .46,  .05,    .03,    .03,     .03],
        k=1
    )[0]

    return f'You got `{res}`!'
