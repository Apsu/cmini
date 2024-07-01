import math
import json
from dataclasses import dataclass, field

from discord import Message

from core.keyboard import Layout, Position
from util import authors, corpora, memory, parser

FINGERS = ('LP', 'LR', 'LM', 'LI', 'RI', 'RM', 'RR', 'RP')


def exec(message: Message):
    id = message.author.id
    kwargs, err = parser.get_kwargs(message, str,
                                    stagger=bool, lateral=str, sfb=str, dsfb=str, sfs=str, key_travel=str,
                                    kps=list, weights=list)
    if err is not None:
        return (f'{str(err)}\n'
                f'```\n'
                f'{use()}\n'
                f'```')

    ll_name: str = kwargs['args']

    if not ll_name:
        return f'```\n{use()}\n```'

    kwargs['dsfb'] = kwargs['dsfb'] or kwargs['sfs']
    kwargs['kps'] = kwargs['kps'] or kwargs['weights']
    try:
        fspeed_params = {}
        if kwargs['stagger']:
            fspeed_params['stagger'] = True
        if kps := kwargs['kps']:
            fspeed_params['kps'] = parse_kps(kps)
        for param in ('lateral', 'dsfb', 'key_travel'):
            if not (num_str := kwargs[param]):
                continue
            fspeed_params[param] = parse_number(num_str)
    except ValueError as err:
        return str(err)

    ll = memory.find(ll_name)
    fspeed = FSpeed(**fspeed_params)
    unweighted_speeds, weighted_speeds = fspeed.fingerspeed(ll, id)

    with open('likes.json', 'r') as f:
        likes: dict[str, list[int]] = json.load(f)

    like_count = len(likes.get(ll.name, ()))
    like_string = 'like' if likes == 1 else 'likes'

    res = ['```',
           f'{ll.name} ({authors.get_name(ll.user)}) ({like_count} {like_string})',
           f'{corpora.get_corpus(id).upper()}:',
           'Unweighted Speed']
    for finger in FINGERS:
        res.append(f'    {finger}: {unweighted_speeds[finger]:.3f}')
    res.extend(('', 'Weighted Speed'))
    for finger in FINGERS:
        res.append(f'    {finger}: {weighted_speeds[finger]:.3f}')
    res.append('```')
    return '\n'.join(res)


@dataclass
class FSpeed:
    stagger: bool = False
    lateral: float = 1.4
    sfb: float = 1.0
    dsfb: float = 0.5
    key_travel: float = 0.01
    kps: dict[str, float] = field(default_factory=lambda:
    dict(zip(FINGERS,
             (1.5, 3.6, 4.8, 5.5, 5.5, 4.8, 3.6, 1.5))))

    def fingerspeed(self, ll: Layout, id: int) -> tuple[dict[str, float], dict[str, float]]:
        bigrams: dict[str, float] = corpora.ngrams(2, id=id)
        trigrams: dict[str, float] = corpora.ngrams(3, id=id)
        bigram_total = sum(bigrams.values())
        skipgram_total = sum(trigrams.values())

        sfb_speeds = dict.fromkeys(FINGERS, 0.0)
        dsfb_speeds = sfb_speeds.copy()

        for gram, freq in bigrams.items():
            p1 = ll.keys.get(gram[0].lower(), None)
            p2 = ll.keys.get(gram[1].lower(), None)
            if not p1 or not p2 or p1.finger != p2.finger:
                continue
            dist = self.two_key_dist(p1, p2, True) + 2 * self.key_travel
            sfb_speeds[p1.finger] += freq * dist

        for gram, freq in trigrams.items():
            p1 = ll.keys.get(gram[0].lower(), None)
            p2 = ll.keys.get(gram[2].lower(), None)
            if not p1 or not p2 or p1.finger != p2.finger:
                continue
            dist = self.two_key_dist(p1, p2, True) + 2 * self.key_travel
            dsfb_speeds[p1.finger] += freq * dist

        speeds: dict[str, float] = {finger:
                                        self.sfb * sfb_speeds[finger] / bigram_total +
                                        self.dsfb * dsfb_speeds[finger] / skipgram_total
                                    for finger in FINGERS}
        unweighted_speeds = {finger: speed * 800 for finger, speed in speeds.items()}
        weighted_speeds = {finger: speed / self.kps[finger] for finger, speed in unweighted_speeds.items()}
        return unweighted_speeds, weighted_speeds

    def two_key_dist(self, p1: Position, p2: Position, weighted: bool) -> float:
        c1, r1 = p1.col, p1.row
        c2, r2 = p2.col, p2.row
        x = staggered_x(c1, r1) - staggered_x(c2, r2) if self.stagger else c1 - c2
        y = r1 - r2
        return self.lateral * x * x + y * y if weighted else math.sqrt(x * x + y * y)


def staggered_x(c: int, r: int) -> float:
    if r == 0:
        return c - 0.25
    if r == 2:
        return c + 0.5
    return c


def parse_number(s: str) -> float:
    try:
        return float(s)
    except ValueError:
        raise ValueError(f"Error: Could not convert '{s}' into a number")


def parse_kps(s: list[str]) -> dict[str, float]:
    if len(s) != 8:
        raise ValueError(f'Error: length of kps is not 8')
    return dict(zip(FINGERS, (parse_number(item) for item in s)))


def use():
    return ('fspeed [layout name] [--kwargs]\n'
            'see the finger speed of a layout\n'
            'Options:\n'
            '--stagger\n'
            '--[lateral, sfb, dsfb, key_travel] [num]\n'
            '--kps [num...]\n')


def desc():
    return 'see the finger speed of a layout'
