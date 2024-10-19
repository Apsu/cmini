from discord import Message, ChannelType

from util import corpora, memory, parser, consts
from util.analyzer import TABLE

def exec(message: Message):
    kwargs: dict[str, bool] = parser.get_kwargs(message, str, len=list, 
        inroll=bool, inward=bool, 
        outroll=bool, outward=bool, 
        samerow=bool, sr=bool, 
        adjacentfinger=bool, af=bool
    )
    layout_name = kwargs['args']
    ll = memory.find(layout_name.lower())
    is_dm = message.channel.type == ChannelType.private

    if not layout_name:
        tips = [
            'Usage: `rolls [layout_name] [--args]`',
            "```",
            "no arg:",
            "    view all rolls of a layout",
            "--inroll",
            "    view inrolls of a layout",
            "--outroll",
            "    view outrolls of a layout",
            "--samerow/sr:",
            "    view same row rolls of a layout",
            "--adjacentfinger/af:",
            "    view adjacent finger rolls of a layout",
            "--len [int]:",
            "    view set number of rolls in dms",
            "```"
        ]
        return '\n'.join(tips)

    sr = kwargs.get('sr') or kwargs.get('samerow')
    af = kwargs.get('af') or kwargs.get('adjacentfinger')
    inward = kwargs.get('inroll') or kwargs.get('inward')
    outward = kwargs.get('outroll') or kwargs.get('outward')
    arg = "roll"
    display_arg = "Rolls"
    if inward:
        arg += "-in"
        display_arg = "In" + display_arg.lower()
    elif outward:
        arg += "-out"
        display_arg = "Out" + display_arg.lower()
    no_args = not (sr or af or inward or outward)

    tag_parts = []
    if kwargs.get('sr') or kwargs.get('samerow'):
        tag_parts.append("Same-Row")
    if kwargs.get('af') or kwargs.get('adjacentfinger'):
        tag_parts.append("Adjacent-Finger")
    tag = " ".join(tag_parts)

    if kwargs['len'] and is_dm:
        leng = int(kwargs['len'][0]) if int(kwargs['len'][0]) <= 100 else 100
    else:
        leng = 10

    trigrams = corpora.ngrams(3, id=message.author.id)
    total = sum(trigrams.values())

    rolls = {}
    for gram, count in trigrams.items():
        gram = gram.lower()
        
        if len(set(gram)) != len(gram): # ignore repeats
            continue

        key = '-'.join([ll.keys[x].finger for x in gram if x in ll.keys])

        if key in TABLE and TABLE[key].startswith(arg) and (
            no_args or (not no_args and (
                (not sr or same_row(ll, key, gram)) and 
                (not af or adjacent_finger(ll, key, gram)
            )))):
            rolls[gram] = rolls.get(gram, 0) + count

    g_total = sum(count for (_, count) in rolls.items()) / total

    res = []
    format_len = len(f'{g_total:.3%}')
    for ngram, count in rolls.items():
        res.append(f'{ngram:{format_len}} {count / total:.3%}')

    return '\n'.join(['```', f'Top {len(res[:leng])} {ll.name}{f" {tag}" if tag else ""} {display_arg}:'] + res[:leng] + [f'Total: {g_total:.3%}'] + ['```'])

def use():
    return 'rolls [layout name] [--args]'

def desc():
    return 'see the highest rolls for a particular layout'

def same_row(ll, key, gram):
    first, second = key.split("-")[:2]
    rollfirst = first[0] == second[0]
    return (rollfirst and ll.keys[gram[0]].row == ll.keys[gram[1]].row) or (not rollfirst and ll.keys[gram[1]].row == ll.keys[gram[2]].row)

def adjacent_finger(ll, key, gram):
    first, second = key.split("-")[:2]
    rollfirst = first[0] == second[0]
    return (rollfirst and abs(consts.FINGER_VALUES[ll.keys[gram[0]].finger] - consts.FINGER_VALUES[ll.keys[gram[1]].finger]) == 1) or (not rollfirst and abs(consts.FINGER_VALUES[ll.keys[gram[1]].finger] - consts.FINGER_VALUES[ll.keys[gram[2]].finger]) == 1) 
