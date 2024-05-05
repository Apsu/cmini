import glob
import json
import random
import re

from discord import Message, ChannelType
from util import parser, memory

def exec(message: Message):
    row = ''.join(parser.get_args(message))
    lines = []
    for file in glob.glob('layouts/*.json'):
        ll = memory.parse_file(file)

        keys = sorted(ll.keys.items(), key=lambda k: (k[1].row, k[1].col))
        homerow = ''.join(k for k,v in keys if v.row == 1)

        if is_homerow(row, homerow):
            lines.append(ll.name)

    is_dm = message.channel.type == ChannelType.private

    if is_dm:
        res = lines
        res_len = len(lines)
    else:
        if len(lines) < 20:
            res = lines
            res_len = len(lines)
            if res_len < 1:
                return "No matches found"
        else:
            res = random.sample(lines, k=20)
            res_len = 20

    res = list(sorted(res, key=lambda x: x.lower()))
    note = "" if is_dm else f", here are {res_len} of them"

    return '\n'.join([f'I found {len(lines)} matches{note}', '```'] + res + ['```'])


def use():
    return 'homerow [string]'

def desc():
    return 'search for layouts with a particular string in homerow'


def is_homerow(row: str, homerow: str) -> bool:
    if row.startswith('"') and row.endswith('"'):
        pattern = re.compile(row.strip('"').replace('.', '\.').replace('_', '.'))
        return bool(pattern.search(homerow) or pattern.search("".join(reversed(homerow))))
    else:
        return all(i in homerow for i in row)