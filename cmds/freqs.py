import re

from discord import Message

from util import corpora, parser

RESTRICTED = True

def get_reverse(ngram):
    return ngram[::-1]

def calculate_freq(item, ngrams):
    pattern = re.compile(re.escape(item).replace('_', '.'))
    count = sum(value for key, value in ngrams.items() if pattern.search(key))
    return count / sum(ngrams.values())

def exec(message: Message):
    id = message.author.id
    query = parser.get_args(message)

    ntype = len(query[0]) if len(query) > 0 else None

    if not query or ntype < 1 or ntype > len(corpora.NGRAMS):
        return f"Please provide at least 1 ngram between 1-{len(corpora.NGRAMS)} chars"

    if len(query) > 6:
        return "Please provide no more than 6 ngrams"

    ngrams = corpora.ngrams(ntype, id=id)
    corpus = corpora.get_corpus(id)

    processed_ngrams = set()
    total_freq = 0
    res = ['```', f'{corpus.upper()}']

    for item in query:
        if len(item) != ntype:
            return 'All ngrams must be the same length'

        reverse = get_reverse(item)

        if item in processed_ngrams or (ntype > 1 and reverse in processed_ngrams):
            continue

        processed_ngrams.update({item, reverse})

        freq_original = calculate_freq(item, ngrams)
        total_freq += freq_original
        
        if ntype > 1:
            freq_reverse = calculate_freq(reverse, ngrams)
            if item != reverse:
                res.extend([
                    f'{item} + {reverse}: {freq_original + freq_reverse:.2%}',
                    f'  {item}: {freq_original:.2%}',
                    f'  {reverse}: {freq_reverse:.2%}'
                ])
                total_freq += freq_reverse
            else: 
                res.append(f'{item}: {freq_original:.2%}')
        elif ntype == 1:
            res.append(f'{item}: {freq_original:.2%}')

    if total_freq == 0:
        return f'`{" ".join(query)}` not found in corpus `{corpus}`'

    if len(query) == 1 or all(item == query[0] or get_reverse(item) == query[0] for item in query):
        res.append('```')
    elif len(query) > 1:
        res.extend([f'Total: {total_freq:.2%}', '```'])
    return '\n'.join(res)
