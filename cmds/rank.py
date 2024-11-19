import os

from discord import Message
from util import parser, corpora, cache

from typing import Final

RESTRICTED = False

class GetLayoutStats:
    __slots__ = ('stats', 'operator', 'reverse', 'percent')

    def __init__(self, *stats: str, operator='+', reverse=False, percent=True):
        self.stats: tuple[str] = stats
        self.operator = operator
        self.reverse = reverse
        self.percent = percent

    def __call__(self, cached_stats: dict[str, float]):
        if len(self.stats) == 1:
            return cached_stats[self.stats[0]]
        if self.operator == '/':
            return cached_stats[self.stats[0]] / cached_stats[self.stats[1]]
        return sum(cached_stats[stat] for stat in self.stats)

STATS: Final[dict[str, GetLayoutStats]] = {
    'alt': GetLayoutStats('alternate', reverse=True),
    'sfb': GetLayoutStats('sfb'),
    'sfs': GetLayoutStats('dsfb', 'dsfb-red', 'dsfb-alt', operator='+'),
    'red': GetLayoutStats('redirect', 'bad-redirect', operator='+'),
    'oneh': GetLayoutStats('oneh-in', 'oneh-out', operator='+', reverse=True),
    'inroll': GetLayoutStats('roll-in', reverse=True),
    'outroll': GetLayoutStats('roll-out', reverse=True),
    'roll': GetLayoutStats('roll-in', 'roll-out', operator='+', reverse=True),
    'inrollratio': GetLayoutStats('roll-in', 'roll-out', operator='/', reverse=True, percent=False),
    'outrollratio': GetLayoutStats('roll-out', 'roll-in', operator='/', reverse=True, percent=False),
    'inrolltal': GetLayoutStats('roll-in', 'oneh-in', operator='+', reverse=True),
    'outrolltal': GetLayoutStats('roll-out', 'oneh-out', operator='+', reverse=True),
    'rolltal': GetLayoutStats('roll-in', 'oneh-in', 'roll-out', 'oneh-out', operator='+', reverse=True)
}

STATS_ALIAS: Final[dict[str, str]] = {
    'alts': 'alt', 'alternate': 'alt',
    'sfbs': 'sfb',
    'dsfb': 'sfs', 'dsfbs': 'sfs',
    'redirect': 'red', 'redirects': 'red',
    'onehand': 'oneh', 'onehands': 'oneh',
    'inrolls': 'inroll', 'roll-in': 'inroll',
    'outrolls': 'outroll', 'roll-out': 'outroll',
    'rolls': 'roll', 'roll-total': 'roll',
    'roll-in-ratio': 'inrollratio',
    'roll-out-ratio': 'outrollratio',
    'inrolltals': 'inrolltal',
    'outrolltals': 'outrolltal',
    'rolltals': 'rolltal', 'rolltotal': 'rolltal'
}

def exec(message: Message):
    user = message.author.id
    corpus = corpora.get_corpus(user)

    length = 15

    kwargs, err = parser.get_kwargs(message, list[str], min=bool, max=bool)
    if err is not None:
        return (f'{str(err)}\n'
                f'```\n'
                f'{use()}\n'
                f'```')

    args = kwargs['args']
    stat = args[0] if len(args) > 0 else ''
    if stat == '':
        return f'```\n{use()}\n```'

    start = args[1] if len(args) > 1 else 0
    sort_asc = kwargs['min']
    sort_desc = kwargs['max']

    try:
        start = int(start)
    except ValueError:
        return 'Error: Invalid starting index'

    if sort_asc and sort_desc:
        return 'Error: Cannot rank ascending and descending altogether'

    use_override_reverse = sort_asc or sort_desc
    override_reverse = sort_desc

    results: list[tuple[float, str]] = []

    if stat not in STATS:
        if stat not in STATS_ALIAS:
            return f'{stat} not supported'
        stat = STATS_ALIAS[stat]

    get_layout_stats = STATS[stat]
    reverse: bool = get_layout_stats.reverse
    percent: bool = get_layout_stats.percent

    for file in os.scandir('cache'):
        name: str = file.name.split(".json")[0]
        cached_stats: dict[str, float] = cache.get(name, corpus)
        try:
            if (value := get_layout_stats(cached_stats)) > 0.001:
                results.append((value, name))
        except:
            print(f"{name}: Error computing {stat}")

    if use_override_reverse:
        reverse = override_reverse

    results.sort(key=lambda x: x[0], reverse=reverse)
    results = results[start: start + length]

    value_formatter = '.2%' if percent else '.3'

    return '```\n' + f'{corpus.upper()}\n' + '\n'.join(
        f'{index}: {value:{value_formatter}} -- {name}'
        for index, (value, name) in enumerate(results, start=start)
        ) + '```'

def use():
    return ('rank [metric]\n'
            'Supported rank stats:\n'
            'alt sfb sfs red oneh inroll outroll roll inrollratio outrollratio inrolltal outrolltal rolltal')

def desc():
    return 'rank layouts based on a metric'
