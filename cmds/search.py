import glob
import random
from jellyfish import jaro_winkler_similarity as jw
from discord import Message, ChannelType

from util import parser, memory

# RESTRICTED = True

FINGERS = ['LI', 'LM', 'LR', 'LP', 'RI', 'RM', 'RR', 'RP', 'LT', 'RT', 'TB']
FINGER_ALIASES = {
    'index': {'LI', 'RI'},
    'middle': {'LM', 'RM'},
    'ring': {'LR', 'RR'},
    'pinky': {'LP', 'RP'},
    'thumb': {'LT', 'RT', 'TB'},
    'lh': {'LI', 'LM', 'LR', 'LP', 'LT'},
    'rh': {'RI', 'RM', 'RR', 'RP', 'RT', 'TB'},
}
SIMILARITY_THRES = 0.7


def exec(message: Message):
    is_dm = message.channel.type is ChannelType.private
    kwargs: dict[str, str | bool]
    kwargs, err = parser.get_kwargs(message, str,
                                    li=bool, lm=bool, lr=bool, lp=bool, lt=bool,
                                    ri=bool, rm=bool, rr=bool, rp=bool, rt=bool, tb=bool,
                                    index=bool, middle=bool, ring=bool, pinky=bool, thumb=bool,
                                    lh=bool, rh=bool,
                                    name=list,
                                    )
    if err is not None:
        return (f'{str(err)}\n'
                f'```\n'
                f'{use()}\n'
                f'```')

    filter_name: str = "".join(kwargs['name'])
    sfb: str = kwargs['args']
    # No arguments
    if not sfb and not filter_name:
        return f'```\n{use()}\n```'

    # Only filter by name
    if not sfb:
        res: list[str] = []
        for file in glob.glob('layouts/*.json'):
            name = memory.parse_file(file).name
            if is_similar(filter_name, name):
                res.append(name)
        return return_message(res, is_dm)

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

        # not sfb
        if len(fingers) != 1:
            continue
        # have finger constraints but finger is not in constrained fingers
        if sfb_fingers and not fingers.issubset(sfb_fingers):
            continue
        # have name filter but name is not similar enough
        if filter_name and not is_similar(filter_name, ll.name):
            continue
        res.append(ll.name)

    return return_message(res, is_dm)


def get_line_limit(res: list[str]) -> int:
    # Find the max number of lines that fit in the message (only for DMs)
    char_count = 0
    line_limit = 0
    for line in res:
        char_count += len(line) + 1
        if char_count > 1900:
            break
        line_limit += 1
    return line_limit


def return_message(res: list[str], is_dm: bool) -> str:
    random.shuffle(res)
    res_len = get_line_limit(res) if is_dm else 20
    if res_len < 1:
        return 'No matches found'
    all_or_n = 'all' if res_len == len(res) else res_len

    lines = [f'I found {len(res)} matches, here are {all_or_n} of them:', '```']
    lines += list(sorted(res[:res_len], key=str.lower))
    lines.append('```')

    return '\n'.join(lines)


def is_similar(s1: str, s2: str) -> bool:
    return jw(s1, s2) > SIMILARITY_THRES


def use():
    return ('search [sfb/column] [--fingers] [--name <name>]\n'
            'Supported fingers: \n'
            'li, lm, lr, lp, ri, rm, rr, rp, lt, rt, tb, index, middle, ring, pinky, thumb, lh, rh, name\n')


def desc():
    return 'find layouts with a particular set of sfbs'
