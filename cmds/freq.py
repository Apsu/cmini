import re

from discord import Message

from util import corpora, parser

RESTRICTED = True

def exec(message: Message):
    id = message.author.id
    query = parser.get_args(message)

    ntype = len(query[0]) if len(query) > 0 else None

    if not query or not 1 <= ntype <= len(corpora.NGRAMS):
        return f'Please provide at least 1 ngram between 1-{len(corpora.NGRAMS)} chars'

    if len(query) > 6:
        return "Please provide no more than 6 ngrams"

    ngrams = corpora.ngrams(ntype, id=id)
    corpus = corpora.get_corpus(id)
    res = ['```', f'{corpus.upper()}']

    count = 0
    for item in query:
        if len(item) != ntype:
            return "All ngrams must be the same length"
        freq = calculate_freq(item, ngrams)
        count += freq
        res.append(f'{item}: {freq:.2%}')
    
    if count == 0:
        return f"`{' '.join(query)}` not found in corpus `{corpus}`"

    if len(query) > 1:
        res.extend([f'Total: {count:.2%}'])
    res.append('```')
    return '\n'.join(res)

def use():
    return "freq [ngrams ...]"

def desc():
    return "see the frequency of ngrams"

def calculate_freq(item, ngrams):
    pattern = re.compile(re.escape(item).replace('_', '.'))
    count = sum(value for key, value in ngrams.items() if pattern.search(key))
    return count / sum(ngrams.values())
