import json
from discord import Message
from jellyfish import damerau_levenshtein_distance as lev

def update(message: Message):
    with open('authors.json', 'r') as f:
        authors = json.load(f)

    user = message.author.name
    id = message.author.id

    authors[user] = id

    with open('authors.json', 'w') as f:
        f.write(json.dumps(authors, indent=4))


def get_id(name: str) -> int:
    with open('authors.json', 'r') as f:
        authors = json.load(f)

    if name in authors:
        return int(authors[name])
    else:
        names = sorted(authors.keys(), key=lambda x: len(x))
        closest = min(names, key=lambda x: lev((''.join(y for y in x.lower() if y in name)), name))

        return int(authors[closest])


def get_name(id: int) -> str:
    with open('authors.json', 'r') as f:
        authors = json.load(f)

    names = [k for k, v in authors.items() if int(v) == id]

    if names:
        return names[-1:][0]
    else:
        return 'unknown'
