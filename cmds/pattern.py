from discord import Message
from util import corpora, memory, parser
from util.analyzer import TABLE
import re

RESTRICTED = True
MAX_NGRAM = len(corpora.NGRAMS)

def exec(message: Message):
    args = parser.get_args(message)
    name = args[0] if len(args) > 0 else ''
    query = [arg.upper() for arg in args[1:]]

    if not name:
        return "Error: Please provide a layout name"
    
    ll = memory.find(name)
    if not ll:
        return f'Error: couldn\'t find any layout named `{name}`'
    
    allowed_fingers = ["LI", "LM", "LR", "LP", "RI", "RM", "RR", "RP", "LT", "RT", "TB", "RH", "LH", "__"]

    if not query:
        return f'```\nSupported finger values:\n{" ".join(allowed_fingers)}```'

    for finger in query:
        if finger not in allowed_fingers:
            return '\n'.join([
            f'```{finger} is not a supported finger values',
            f'Supported finger values:',
            f'{" ".join(allowed_fingers)}',
            '```'
        ])

    if len(query) > MAX_NGRAM:
        return f'Please provide no more than {MAX_NGRAM} finger values'
    
    ngrams = {ngram: count for ngram, count in corpora.ngrams(len(query), id=message.author.id).items()}
    total = sum(ngrams.values())
    freq = 0
    lines = {}

    fingers = '-'.join(query)
    pattern = re.compile(fingers.replace('_', '.').replace('H', '.'))

    for gram, count in ngrams.items():
        gram = gram.lower()
        
        if len(set(gram)) != len(gram):
            continue

        key = '-'.join([ll.keys[x].finger for x in gram if x in ll.keys])
        
        if pattern.search(key):
            freq += count
            lines[gram] = lines.get(gram, 0) + count
            
    lines = sorted(lines.items(), key=lambda x: x[1], reverse=True)[:10]
    lines = [f'{gram:<5} {count / total:.3%}' for gram, count in lines]

    return '\n'.join([
        '```',
        f'Top {ll.name} Patterns for {fingers}{f" ({TABLE[fingers]})" if fingers in TABLE and len(query) == 3 else ""}:',
        *lines[:10],
        f'Total {freq / total:.3%}',
        '```'
    ])

def use():
    return 'pattern [layout name] [finger string]'

def desc():
    return 'see the most common pattern for a given finger string (e.g., RM LI or LP LR LM)'
