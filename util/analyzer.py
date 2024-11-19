import json
from typing import Dict

from core.keyboard import Layout

with open('table.json', 'r') as f:
    TABLE: Dict[str, str] = json.load(f)
DEFAULT_COUNTER: dict[str, float] = dict.fromkeys(set(TABLE.values()) | {'sfR', 'unknown'}, 0)

def use(ll: Layout, grams: Dict[str, str]):
    fingers = {}

    for gram, count in grams.items():
        gram = gram.lower()

        if gram not in ll.keys:
            continue

        finger = ll.keys[gram].finger

        if finger not in fingers:
            fingers[finger] = 0

        fingers[finger] += count

    total = sum(fingers.values())
    for finger in fingers:
        fingers[finger] /= total

    fingers['LH'] = sum(fingers[x] for x in fingers if x[0] in 'L')
    fingers['RH'] = sum(fingers[x] for x in fingers if x[0] in 'RT')

    return fingers


def bigrams(ll: Layout, grams: Dict[str, int]) -> dict[str, float]:
    counts = DEFAULT_COUNTER.copy()
    fingers = {key: value.finger for key, value in ll.keys.items()}
    total = 0

    for gram, count in grams.items():
        gram = gram.lower()

        if ' ' in gram:
            continue

        if not (gram[0] in fingers and gram[1] in fingers):
            continue

        total += count

        if gram[0] == gram[1]:
            counts['sfR'] += count
            continue

        if fingers[gram[0]] == fingers[gram[1]]:
            counts['sfb'] += count
            continue

    for stat in counts:
        counts[stat] /= total

    return counts


def trigrams(ll: Layout, grams: Dict[str, int]):
    counts = DEFAULT_COUNTER.copy()
    fingers = {key: value.finger for key, value in ll.keys.items()}
    total = 0

    for gram, count in grams.items():
        gram = gram.lower()

        if ' ' in gram:
            continue

        if not all(char in fingers.keys() for char in gram):
            continue

        total += count

        # Skips on sfr sfb sfsr
        if fingers[gram[0]] == fingers[gram[1]] or fingers[gram[1]] == fingers[gram[2]] or gram[1] == gram[2]:
            continue

        finger_combo = '-'.join(fingers[x] for x in gram if x in fingers)
        finger_combo = finger_combo.replace('TB', 'RT')
        gram_type = TABLE.get(finger_combo, 'unknown')

        counts[gram_type] += count

    for stat in counts:
        counts[stat] /= total

    return counts
