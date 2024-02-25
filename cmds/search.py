import json
import glob
import random
from discord import Message, ChannelType

from util import parser, memory

# RESTRICTED = True

FINGERS = ['LI', 'LM', 'LR', 'LP', 'RI', 'RM', 'RR', 'RP', 'LT', 'RT', 'TB']
FINGER_ALIASES = {
    'index':  {'LI', 'RI'},
    'middle': {'LM', 'RM'},
    'ring':   {'LR', 'RR'},
    'pinky':  {'LP', 'RP'},
    'thumb':  {'LT', 'RT', 'TB'},
    'rt': {'RT', 'TB'},
    'lh': {'LI', 'LM', 'LR', 'LP', 'LT'},
    'rh': {'RI', 'RM', 'RR', 'RP', 'RT', 'TB'},
}

def exec(message: Message):
    kwargs: dict[str, str | bool] = parser.get_kwargs(message, str,
                                                      li=bool, lm=bool, lr=bool, lp=bool, lt=bool,
                                                      ri=bool, rm=bool, rr=bool, rp=bool, rt=bool,
                                                      index=bool, middle=bool, ring=bool, pinky=bool, thumb=bool, tb=bool,
                                                      lh=bool, rh=bool
                                                      )

    sfb: str = kwargs['args']
    if not sfb:
        return '```\n' \
               'search [sfb/column] [--fingers]\n' \
               'Supported fingers: \n' \
               'li, lm, lr, lp, ri, rm, rr, rp, lt, rt, tb, index, middle, ring, pinky, thumb, lh, rh\n' \
               '```'

    # Add fingers to the set
    sfb_fingers: set[str] = {finger for finger in FINGERS if kwargs[finger.lower()]}

    # Add sets in finger aliases to the set
    for finger, finger_set in FINGER_ALIASES.items():
        if kwargs[finger]:
            sfb_fingers |= finger_set

    res: list[str] = []
    for file in glob.glob('layouts/*.json'):
        ll = memory.parse_file(file)

        if not all(x in ll.keys for x in sfb):
            continue

        fingers = set(ll.keys[x].finger for x in sfb)

        if len(fingers) == 1:
            # any finger or in constrained fingers
            if not sfb_fingers or fingers.issubset(sfb_fingers):
                res.append(ll.name)

    random.shuffle(res)

    res_len = min(len(res), 20)
    if res_len < 1:
        return 'No matches found'

    is_dm = message.channel.type is ChannelType.private

    # Find the max number of lines that fit in the message (only for DMs)
    if is_dm:
        char_count = 0
        line_limit = 0
        for line in res:
            char_count += len(line) + 1
            if char_count > 1900:
                break
            line_limit += 1
        # set the new result length to the line limit
        res_len = line_limit

    all_or_n = 'all' if res_len == len(res) else res_len

    lines = [f'I found {len(res)} matches, here are {all_or_n} of them:']

    lines.append('```')
    lines += list(sorted(res[:res_len], key=str.lower))
    lines.append('```')

    return '\n'.join(lines)


def use():
    return 'search [sfb/column] [--fingers]'


def desc():
    return 'find layouts with a particular set of sfbs'
