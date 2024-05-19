from discord import Message, ChannelType

from util import corpora, memory, parser, consts
from util.analyzer import TABLE

def exec(message: Message):
    kwargs: dict[str, bool] = parser.get_kwargs(message, str, len=list, sfs=bool, bad=bool)
    layout_name = kwargs['args']
    ll = memory.find(layout_name.lower())
    is_dm = message.channel.type == ChannelType.private

    if not layout_name:
        tips = [
            'Usage: `redirects [layout_name] [--arg]`',
            "```",
            "no arg:",
            "    view all redirects of a layout",
            "--sfs:",
            "    view sfs redirects of a layout",
            "--bad:",
            "    view bad redirects of a layout",
            "--len [int]:",
            "    view set number of redirects in dms",
            "```"
        ]
        return '\n'.join(tips)

    arg = 'Redirect'
    if kwargs['bad']:
        arg = 'Bad-Redirect'
    if kwargs['sfs']:
        arg = 'dsfb-Red'
    no_args = not(kwargs['bad'] or kwargs['sfs'])

    tag_parts = []
    if kwargs.get('bad'):
        tag_parts.append("Bad")
    if kwargs.get('sfs'):
        tag_parts.append("SFS")
    tag = " ".join(tag_parts)


    if kwargs['len'] and is_dm:
        leng = int(kwargs['len'][0]) if int(kwargs['len'][0]) <= 100 else 100
    else:
        leng = 10

    trigrams = corpora.ngrams(3, id=message.author.id)
    total = sum(trigrams.values())

    red = {}
    for gram, count in trigrams.items():
        gram = gram.lower()

        if len(set(gram)) != len(gram): # ignore repeats
            continue

        key = '-'.join([ll.keys[x].finger for x in gram if x in ll.keys])

        if key in TABLE and TABLE[key].lower().endswith(arg.lower()) and (
            no_args or (not no_args and (
                (not kwargs['bad'] or weak_check(key)
            )))):
            red[gram] = red.get(gram, 0) + count

    g_total = sum(count for (_, count) in red.items()) / total

    res = []
    format_len = len(f'{g_total:.3%}')
    for ngram, count in red.items():
        res.append(f'{ngram:<{format_len}} {count / total:.3%}')

    return '\n'.join(['```', f'Top {len(res[:leng])} {ll.name}{f" {tag}" if tag else ""} Redirects:'] + res[:leng] + [f'Total: {g_total:.3%}'] + ['```'])

def use():
    return 'redirects [layout name] [--arg]'

def desc():
    return 'see the worst redirects for a particular layout'

def finger_type(finger):
    if finger == 0 or finger == 8:
        return 0
    elif finger == 1 or finger == 6:
        return 1
    elif finger == 2 or finger == 5:
        return 2
    elif finger == 3 or finger == 4:
        return 3
    return finger

def weak_check(key):
    return all(finger_type(consts.FINGER_VALUES[f]) != 3 for f in key.split("-"))
