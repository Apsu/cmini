from discord import Message

from util import parser

RESTRICTED = False

def exec(message: Message):
    suggestion = parser.get_arg(message)

    with open('suggestions.txt', 'a') as f:
        f.write(f'\n{message.author.name}: {suggestion}')

    return 'https://tenor.com/view/andersomviolao-gif-12381443319241980618'

def use():
    return 'suggest [message]'

def desc():
    return 'send me a suggestion for how to improve cmini :)'
