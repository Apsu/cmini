from discord import Message, ChannelType

from util import corpora, memory, parser, consts
from util.analyzer import TABLE

def exec(message: Message):
    kwargs: dict[str, bool] = parser.get_kwargs(message, str, len=list, inward=bool, outward=bool, samerow=bool, sr=bool, adjacentfinger=bool, af=bool)
    layout_name = kwargs['args']
    ll = memory.find(layout_name.lower())
    is_dm = message.channel.type == ChannelType.private

    if not layout_name:
        tips = [
            'Usage: `alternates [layout_name] [--args]`',
            "```",
            "no arg:",
            "    view all alternates of a layout",
            "--inward",
            "    view inward alternates of a layout",
            "--outward",
            "    view outward alternates of a layout",
            "--samerow/sr:",
            "    view same row alternates of a layout",
            "--adjacentfinger/af:",
            "    view adjacent finger alternates of a layout",
            "--len [int]:",
            "    view set number of alternates in dms",
            "```"
        ]
        return '\n'.join(tips)

    sr = kwargs.get('sr') or kwargs.get('samerow')
    af = kwargs.get('af') or kwargs.get('adjacentfinger')
    inward = kwargs.get('inward')
    outward = kwargs.get('outward')
    no_args = not (sr or af or inward or outward)

    tag_parts = []
    if kwargs.get('inward'):
        tag_parts.append("Inward")
    if kwargs.get('outward'):
        tag_parts.append("Outward")
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

    alts = {}
    for gram, count in trigrams.items():
        gram = gram.lower()

        if len(set(gram)) != len(gram): # ignore repeats
            continue

        key = '-'.join([ll.keys[x].finger for x in gram if x in ll.keys])
        
        if key in TABLE and TABLE[key].startswith('alt') and (
            no_args or (not no_args and (
                (not sr or same_row(ll, key, gram)) and 
                (not af or adjacent_finger(ll, key, gram)) and 
                (not inward  or dir(key)) and 
                (not outward or not dir(key)
            )))):
            alts[gram] = alts.get(gram, 0) + count

    g_total = sum(count for (_, count) in alts.items()) / total

    res = []
    format_len = len(f'{g_total:.3%}')
    for ngram, count in alts.items():
        res.append(f'{ngram:{format_len}} {count / total:.3%}')

    return '\n'.join(['```', f'Top {len(res[:leng])} {ll.name}{f" {tag}" if tag else ""} Alternates:'] + res[:leng] + [f'Total: {g_total:.3%}'] + ['```'])

def use():
    return 'alternates [layout name]'

def desc():
    return 'see the highest alternates for a particular layout'

def same_row(ll, key, gram):
    first, third = key.split("-")[::2]
    return first[0] == third[0] and ll.keys[gram[0]].row == ll.keys[gram[2]].row

def adjacent_finger(ll, key, gram):
    first, third = key.split("-")[::2]
    return first[0] == third[0] and abs(consts.FINGER_VALUES[ll.keys[gram[0]].finger] - consts.FINGER_VALUES[ll.keys[gram[2]].finger]) == 1

def dir(key):
    first, third = key.split("-")[::2]
    f1, f3 = consts.FINGER_VALUES[first], consts.FINGER_VALUES[third]
    return (f1 < 4 and f1 < f3) or (f1 >= 4 and f1 > f3)
