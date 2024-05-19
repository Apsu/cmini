from discord import Message

from util import corpora, memory, parser

def exec(message: Message):
    name = parser.get_arg(message)
    ll = memory.find(name.lower())

    bigrams = corpora.ngrams(2, id=message.author.id)
    total = sum(bigrams.values())

    sfbs = {}
    for gram, count in bigrams.items():
        gram = gram.lower()

        if len(set(gram)) != len(gram): # ignore repeats
            continue

        fingers = [ll.keys[x].finger for x in gram if x in ll.keys]

        if len(set(fingers)) != len(fingers):
            sfbs[gram] = sfbs.get(gram, 0) + count

    g_total = sum(count for (_, count) in sfbs.items())

    res = []
    for ngram, count in sfbs.items():
        res.append(f'{ngram:<6} {count / total:.3%}')

    return '\n'.join(['```', f'Top 10 {ll.name} SFBs:'] + res[:10] + [f'Total: {g_total / total:.3%}'] + ['```'])

def use():
    return 'sfbs [layout name]'

def desc():
    return 'see the worst sfbs for a particular layout'
