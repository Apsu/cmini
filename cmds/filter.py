import glob
import random
from discord import Message, ChannelType

from util import parser, memory, corpora, cache
from .search import is_similar, get_line_limit, FINGERS, FINGER_ALIASES
from .homerow import is_homerow
from .rank import STATS as LAYOUT_STATS

from typing import Callable

METRIC_NAMES = {
    'sfb', 'sfs', 'alt', 'red', 'roll', 'oneh', 'inroll', 'outroll', 'rolltal', 'inrolltal'
}
REVERSE_METRIC_NAMES = {
    'alt', 'roll', 'oneh', 'inroll', 'outroll', 'rolltal', 'inrolltal'
}
FULL_LAYOUT = set('abcdefghijklmnopqrstuvwxyz')


def exec(message: Message):
    is_dm = message.channel.type is ChannelType.private
    kwargs: dict[str, str | bool | list]
    kwargs, err = parser.get_kwargs(message, str, column=list, homerow=str, sort=str,
                                    sfb=str, sfs=str, alt=str, red=str,
                                    roll=str, oneh=str, inroll=str, outroll=str,
                                    rolltal=str, inrolltal=str,
                                    name=str,
                                    partial=bool,
                                    )
    if err is not None:
        return (f'{str(err)}\n'
                f'```\n'
                f'{use()}\n'
                f'```')

    column: list[str] = kwargs['column']
    row: str = kwargs['homerow']
    filter_name: str = kwargs['name']
    filter_partial: bool = kwargs['partial']
    sort_metric: str = kwargs['sort']

    filter_stats: dict[str, str] = {stat: kwargs[stat] for stat in METRIC_NAMES}
    corpus = corpora.get_corpus(message.author.id)
    sort_method: Callable[[dict], float] | None = LAYOUT_STATS[sort_metric] if sort_metric in METRIC_NAMES else None
    res_unordered: list[str] = []
    res_ordered: dict[str, float] = {}

    sfb = column[0] if len(column) > 0 else ''
    temp_fingers: list[str] = column[1:]
    sfb_fingers: set[str] = set()
    # Add sfb fingers and their aliases to set
    for finger in FINGERS:
        if finger.lower() in temp_fingers:
            sfb_fingers.add(finger)
    for finger_alias, finger_set in FINGER_ALIASES.items():
        if finger_alias in temp_fingers:
            sfb_fingers |= finger_set

    # No positional arguments
    kwargs.pop('args')

    if all(not arg for arg in kwargs.values()):
        return f'```\n{use()}\n```'

    for file in glob.glob('layouts/*.json'):
        ll = memory.parse_file(file)

        # Filter by sfb/column
        if sfb:
            # no such key in layout
            if not all(x in ll.keys for x in sfb):
                continue

            finger_set = set(ll.keys[x].finger for x in sfb)
            # not sfb
            if len(finger_set) != 1:
                continue
            # have finger constraints but finger is not in constrained fingers
            if sfb_fingers and not finger_set.issubset(sfb_fingers):
                continue

        # Filter by homerow but not homerow
        if row:
            keys = sorted(ll.keys.items(), key=lambda k: (k[1].row, k[1].col))
            homerow = ''.join(k for k, v in keys if v.row == 1)
            if not is_homerow(row, homerow):
                continue

        # Filter by name but not similar
        if filter_name and not is_similar(filter_name, ll.name):
            continue

        # Loop through the stats
        filtered = True
        try:
            cached_stats: dict[str, float] = cache.get(ll.name, corpus)
        except OSError:
            continue
        for stat_name, stat_str in filter_stats.items():
            if not stat_str:
                continue
            stat_method = LAYOUT_STATS[stat_name]
            stat_value = stat_method(cached_stats)
            res, err = compare_with_str(stat_str, stat_value)
            # Syntax error
            if err is not None:
                return str(err)
            if not res:
                filtered = False
                break

        # Stats failed comparison checks
        if not filtered:
            continue

        # Partial layout disabled but layout does not contain a-z
        if not filter_partial and not set(ll.keys).issuperset(FULL_LAYOUT):
            continue

        if sort_method:
            res_ordered[ll.name] = sort_method(cached_stats)
        else:
            res_unordered.append(ll.name)

    if sort_method:
        res: list[str] = sorted(res_ordered, key=res_ordered.get, reverse=sort_metric in REVERSE_METRIC_NAMES)
    else:
        res = res_unordered
        random.shuffle(res)

    res_len = get_line_limit(res) if is_dm else 20
    if res_len < 1:
        return 'No matches found'
    all_or_n = 'all' if res_len == len(res) else res_len

    lines = [f'I found {len(res)} matches, here are {all_or_n} of them:', '```']
    lines.extend(res[:res_len] if sort_method else sorted(res[:res_len], key=str.lower))
    lines.append('```')

    return '\n'.join(lines)


def compare_with_str(rule: str, value: float) -> tuple[bool, Exception | None]:
    if not rule.startswith('>') and not rule.startswith('<'):
        return False, ValueError(f"Error: '{rule}' does not start with greater or less than operator")
    value2_percent, ok = try_into_float(rule[1:])
    if not ok:
        return False, ValueError(f"Error: cannot convert '{rule[1:]}' into a number")
    return value * 100 > value2_percent if rule.startswith('>') else value * 100 < value2_percent, None


def try_into_float(s: str) -> tuple[float, bool]:
    try:
        f = float(s)
    except ValueError:
        return 0, False
    return f, True


def use():
    return ('filter [--kwargs]\n'
            'Supported options: \n'
            '[--column <sfb/column, ...fingers>],\n'
            '[--homerow <keys / "sequence">],\n'
            '[--sort <metric>],\n'
            '[--name <name>]\n'
            '[--<metric> {< or >}{num}]\n'
            '[--partial]\n'
            'metrics: sfb, sfs, alt, red, roll, oneh, inroll, outroll, rolltal, inrolltal\n'
            )


def desc():
    return ('Filters layouts by column, homerow, name, metric.\n'
            'Sort the layouts alphabetically or by metric.\n'
            "Filters out layouts that doesn't complete the English alphabet\n"
            'Use `--partial` to include partial layouts'
            )
