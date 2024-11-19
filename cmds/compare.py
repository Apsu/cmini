from discord import Message

from util import analyzer, corpora, layout, parser, memory

RESTRICTED = False

def exec(message: Message):
    args = parser.get_args(message)
    new_ll_name = args[0] if len(args) > 0 else ''
    old_ll_name = args[1] if len(args) > 1 else ''

    if not new_ll_name:
        return '`compare [new_layout] [old_layout] (new - old)`'
    if not old_ll_name:
        return f'Error: missing old layout name'

    old_ll = memory.find(old_ll_name)
    new_ll = memory.find(new_ll_name)
    if not old_ll or not new_ll:
        return f'Error: could not find layout(s)'

    user_id = message.author.id
    monograms = corpora.ngrams(1, id=user_id)
    trigrams = corpora.ngrams(3, id=user_id)
    bigrams = corpora.ngrams(2, id=user_id)

    old_stats = {
        **analyzer.trigrams(old_ll, trigrams),
        **analyzer.bigrams(old_ll, bigrams)
    }
    new_stats = {
        **analyzer.trigrams(new_ll, trigrams),
        **analyzer.bigrams(new_ll, bigrams)
    }
    old_use = analyzer.use(old_ll, monograms)
    new_use = analyzer.use(new_ll, monograms)

    for stat in new_stats:
        new_stats[stat] -= old_stats.get(stat, 0)
    for finger_or_hand in new_use:
        new_use[finger_or_hand] -= old_use.get(finger_or_hand, 0)

    corpus_name = corpora.get_corpus(user_id).upper()

    return f'```\n' \
           f'{new_ll.name}(new) - {old_ll.name}(old)\n' \
           f'{layout.get_commonmatrix_str(old_ll, new_ll)}\n' \
           f'\n' \
           f'{corpus_name}:\n' \
           f'{layout.stats_str(new_stats, new_use)}' \
           f'```'

def use():
    return 'compare [new_layout] [old_layout]'

def desc():
    return 'compare the stats of two layouts'
