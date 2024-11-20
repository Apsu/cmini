import json

from util import analyzer, authors, corpora, links
from util.consts import *
from util.returns import *

from core.keyboard import Layout


def check_name(name: str):
    if name[0] == '_':
        return Error('names cannot start with an underscore')

    if len(name) < 3:
        return Error('names must be at least 3 characters long')

    if not set(name).issubset(NAME_SET):
        disallowed = list(set(name).difference(NAME_SET))
        return Error(f'names cannot contain `{disallowed[0]}`')

    return Success()


def get_matrix(ll: Layout) -> list[list[str]]:
    max_width = max(x.col for x in ll.keys.values()) + 1
    max_height = max(x.row for x in ll.keys.values()) + 1

    matrix = [[' '] * max_width for _ in range(max_height)]

    for char, info in ll.keys.items():
        row = info.row
        col = info.col

        matrix[row][col] = char

    for i, row in enumerate(matrix):
        for j, char in enumerate(row):
            if j == 0:
                matrix[i][j] = '  ' + char
            elif j == 4:
                matrix[i][j] += ' '

    if ll.board == 'stagger':
        matrix[1][0] = ' ' + matrix[1][0]
        matrix[2][0] = '  ' + matrix[2][0]
    elif ll.board == 'angle':
        matrix[2][0] = ' ' + matrix[2][0]
    elif ll.board == 'mini':
        matrix[2][0] = '  ' + matrix[2][0]

    if len(matrix) > 3:
        indent = 6 if ll.keys[matrix[3][0].strip()].finger == 'LT' else 13
        matrix[3][0] = ' ' * indent + matrix[3][0]

    return matrix


def get_matrix_str(ll: Layout) -> str:
    return '\n'.join(' '.join(x) for x in get_matrix(ll))


def get_commonmatrix(ll1, ll2) -> list[list[str]]:
    max_width = max(max((x.col if x else 0) for x in ll1.keys.values()),
                max((x.col if x else 0) for x in ll2.keys.values())) + 1
    max_height = max(max((x.row if x else 0) for x in ll1.keys.values()),
                    max((x.row if x else 0) for x in ll2.keys.values())) + 1

    matrix =  [[' '] * max_width for _ in range(max_height)]
    matrix1 = [[' '] * max_width for _ in range(max_height)]
    matrix2 = [[' '] * max_width for _ in range(max_height)]

    for char, info in ll1.keys.items():
        matrix1[info.row][info.col] = char

    for char, info in ll2.keys.items():
        matrix2[info.row][info.col] = char

    for i in range(max_height):
        for j in range(max_width):
            char1 = matrix1[i][j]
            char2 = matrix2[i][j]
            matrix[i][j] = char1 if char1 == char2 else FREE_CHAR

    for i, row in enumerate(matrix):
        for j, char in enumerate(row):
            if j == 0:
                matrix[i][0] = '  ' + char
            elif j == 4:
                matrix[i][4] += ' '

    if ll1.board == ll2.board == 'stagger':
        matrix[1][0] = ' ' + matrix[1][0]
        matrix[2][0] = '  ' + matrix[2][0]
    elif ll1.board == ll2.board == 'angle':
        matrix[2][0] = ' ' + matrix[2][0]
    elif ll1.board == ll2.board == 'mini':
        matrix[2][0] = '  ' + matrix[2][0]

    if len(matrix) > 3:
        try:
            finger1 = ll1.keys.get(matrix[3][0].strip(), None).finger
            finger2 = ll2.keys.get(matrix[3][0].strip(), None).finger
        except Exception:
            finger1 = None
            finger2 = None

        indent = 6 if finger1 == 'LT' or finger2 == 'LT' else 13

        matrix[3][0] = ' ' * indent + matrix[3][0]

    return matrix


def get_commonmatrix_str(ll1: Layout, ll2: Layout) -> str:
    return '\n'.join(' '.join(x) for x in get_commonmatrix(ll1, ll2))


def get_fingermatrix(ll: Layout) -> list[list[str]]:
    max_width = max(x.col for x in ll.keys.values()) + 1
    max_height = max(x.row for x in ll.keys.values()) + 1

    matrix = [[' '] * max_width for _ in range(max_height)]

    for pos in ll.keys.values():
        finger = pos.finger
        finger_val = FINGER_VALUES.get(finger, finger)

        matrix[pos.row][pos.col] = finger_val

    for i, row in enumerate(matrix):
        for j, val in enumerate(row):
            if j == 0:
                matrix[i][j] = '  ' + val
            elif j == 4:
                matrix[i][j] += ' '

    if ll.board == 'stagger':
        matrix[1][0] = ' ' + matrix[1][0]
        matrix[2][0] = '  ' + matrix[2][0]
    elif ll.board == 'angle':
        matrix[2][0] = ' ' + matrix[2][0]
    elif ll.board == 'mini':
        matrix[2][0] = '  ' + matrix[2][0]

    if len(matrix) > 3:
        indent = 6 if matrix[3][0].strip() == '8' else 13
        matrix[3][0] = ' ' * indent + matrix[3][0]

    return matrix


def get_fingermatrix_str(ll: Layout) -> str:
    return '\n'.join(' '.join(x) for x in get_fingermatrix(ll))


def stats_str(stats: JSON|dict[str, float], use: JSON|dict[str, float]) -> str:
    try:
        return (f'  Alt: {stats["alternate"]:>7.2%}\n'
                f'  Rol: {stats["roll-in"] + stats["roll-out"]:>7.2%}'
                f'   (In/Out: {stats["roll-in"]:>7.2%} | {stats["roll-out"]:>7.2%})\n'
                # f'   (In: {stats["roll-in"]:>6.2%} Out: {stats["roll-out"]:>6.2%})\n'
                f'  One: {stats["oneh-in"] + stats["oneh-out"]:>7.2%}'
                f'   (In/Out: {stats["oneh-in"]:>7.2%} | {stats["oneh-out"]:>7.2%})\n'
                # f'   (In: {stats["oneh-in"]:>6.2%} Out: {stats["oneh-out"]:>6.2%})\n'
                f'  Rtl: {stats["roll-in"] + stats["roll-out"] + stats["oneh-in"] + stats["oneh-out"]:>7.2%}'
                f'   (In/Out: {stats["roll-in"] + stats["oneh-in"]:>7.2%} | {stats["roll-out"] + stats["oneh-out"]:>7.2%})\n'
                f'  Red: {stats["redirect"] + stats["bad-redirect"]:>7.2%}'
                f'   (Bad: {stats["bad-redirect"]:>9.2%})\n'
                '\n'
                f'  SFB: {stats["sfb"]:>7.2%}\n'
                f'  SFS: {stats["dsfb-red"] + stats["dsfb-alt"]:>7.2%}'
                f'   (Red/Alt: {stats["dsfb-red"]:>7.2%} | {stats["dsfb-alt"]:>7.2%})\n'
                '\n'
                f'  LH/RH: {use["LH"]:.2%} | {use["RH"]:.2%}')
    except Exception:
        return ""


def to_string(ll: Layout, id: int):
    author = authors.get_name(ll.user)

    monogram = corpora.ngrams(1, id=id)
    bigram = corpora.ngrams(2, id=id)
    trigram = corpora.ngrams(3, id=id)

    matrix_str = get_matrix_str(ll)

    stats = analyzer.trigrams(ll, trigram) | analyzer.bigrams(ll, bigram)
    use = analyzer.use(ll, monogram)

    with open('likes.json', 'r') as f:
        likes = json.load(f)

    if ll.name in likes:
        likes = len(likes[ll.name])
    else:
        likes = 0

    if likes == 1:
        like_string = 'like'
    else:
        like_string = 'likes'

    external_link = links.get_link(ll.name.lower())

    res = (
        f'```\n'
        f'{ll.name} ({author}) ({likes} {like_string})\n'
        f'{matrix_str}\n'
        f'\n'
        f'{corpora.get_corpus(id).upper()}:\n'
        f'{stats_str(stats, use)}'
        f'```\n'
        f'{external_link}\n'
    )

    return res


def fingermap_to_string(ll: Layout):
    author: str = authors.get_name(ll.user)

    matrix_str = get_matrix_str(ll)
    fmatrix_str = get_fingermatrix_str(ll)

    with open('likes.json', 'r') as f:
        likes = json.load(f)

    if ll.name in likes:
        likes = len(likes[ll.name])
    else:
        likes = 0

    if likes == 1:
        like_string = 'like'
    else:
        like_string = 'likes'

    external_link = links.get_link(ll.name.lower())

    res = (
        f'```\n'
        f'{ll.name} ({author}) ({likes} {like_string})\n'
        f'{matrix_str}\n'
        f'\n'
        f'{fmatrix_str}\n'
        f'```\n'
        f'{external_link}\n'
    )

    return res
