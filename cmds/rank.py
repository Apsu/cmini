import os
import json
import logging

from discord import Message
from util import parser, corpora, analyzer, authors, cache
from admins import ADMINS

RESTRICTED = False

def exec(message: Message):
    user = message.author.id
    user_name = authors.get_name(user).lower()
    corpus = corpora.get_corpus(user)
    # Check current user
    # if user_name in ADMINS:
        # length = 100
    # else:
        # length = 15

    length = 15

    args = [item.lower() for item in  parser.get_args(message)]
    stat = args[0]

    if len(args) > 1:
        start = int(args[1])
    else:
        start = 0

    if stat == '':
        return '```\n' + \
            'Supported rank stats:\n' + \
            'alt sfb sfs red oneh inroll outroll roll inrollratio outrollratio inrolltal outrolltal rolltal' + \
            '```'
    results = {}
    reverse = False
    percent = True
    # trigram = corpora.ngrams(3, id=message.author.id)
    for file in os.scandir('cache'):
        # print(f'Opening: {file.name}')
        # with open(f'layouts/{file.name}', 'r') as f:
        #     data = json.load(f)

        # name = data['name']

        # stats = analyzer.trigrams(data, trigram)

        name = file.name.split(".json")[0]
        stats = cache.get(name, corpus)

        # print(f"Name: {name}, Corpus: {corpus}")
        try:
            match stat:
                case 'alt' | 'alts' | 'alternate':
                    stat = 'alt'
                    results[name] = {
                        stat: stats["alternate"]
                    }
                    reverse = True
                case 'sfb' | 'sfbs':
                    stat = 'sfb'
                    results[name] = {
                        stat: stats["sfb"] / 2
                    }
                case 'sfs' | 'dsfb' | 'dsfbs':
                    stat = 'sfs'
                    results[name] = {
                        stat: stats["dsfb-red"] + stats["dsfb-alt"]
                    }
                case 'red' | 'redirect' | 'redirects':
                    stat = 'redirect'
                    results[name] = {
                        stat: stats["redirect"] + stats["bad-redirect"]
                    }
                case 'oneh' | 'onehand' | 'onehands':
                    stat = 'onehand'
                    results[name] = {
                        stat: stats["oneh-in"] + stats["oneh-out"]
                    }
                    reverse = True
                case 'inroll' | 'inrolls' | 'roll-in':
                    stat = 'roll-in'
                    results[name] = {
                        stat: stats["roll-in"]
                    }
                    reverse = True
                case 'outroll' | 'outrolls' | 'roll-out':
                    stat = 'roll-out'
                    results[name] = {
                        stat: stats["roll-out"]
                    }
                    reverse = True
                case 'roll' | 'rolls' | 'roll-total':
                    stat = 'roll-total'
                    results[name] = {
                        stat: stats["roll-in"] + stats["roll-out"]
                    }
                    reverse = True
                case 'inrollratio' | 'roll-in-ratio':
                    stat = 'roll-in-ratio'
                    results[name] = {
                        stat: stats["roll-in"] / stats["roll-out"]
                    }
                    reverse = True
                    percent = False
                case 'outrollratio' | 'roll-out-ratio':
                    stat = 'roll-out-ratio'
                    results[name] = {
                        stat: stats["roll-out"] / stats["roll-in"]
                    }
                    reverse = True
                    percent = False
                case 'inrolltal' | 'inrolltals' | 'rolltal-in' | 'in':
                    stat = 'rolltal-in'
                    results[name] = {
                        stat: stats["roll-in"] + stats["oneh-in"]
                    }
                    reverse = True
                case 'outrolltal' | 'outrolltals' | 'rolltal-out' | 'out':
                    stat = 'rolltal-out'
                    results[name] = {
                        stat: stats["roll-out"] + stats["oneh-out"]
                    }
                    reverse = True
                case 'rolltal' | 'rolltals' | 'rolltotal'
                    stat = 'rolltal'
                    results[name] = {
                        stat: stats["roll-in"] + stats["oneh-in"] + stats["roll-out"] + stats["oneh-out"]
                    }
                    reverse = True
                case _:
                    return f'{stat} not supported'
        except:
            print(f"{name}: Error computing {stat}")

    sorted_results = sorted(results.items(), key=lambda x:x[1][stat])
    if reverse:
        sorted_results = list(reversed(sorted_results))

    if percent: 
        return '```\n' + f'{corpus.upper()}\n' + '\n'.join(
            [f'{index+start}: {value}' for index, value
                in enumerate([f'{result[stat]:.2%} -- {name}' for name, result
                in sorted_results
                if result[stat] > 0.001][start:start+length % len(sorted_results)])
            ]
            ) + '```'
    else:
        return '```\n' + f'{corpus.upper()}\n' + '\n'.join(
            [f'{index+start}: {value}' for index, value
                in enumerate([f'{result[stat]:.3} -- {name}' for name, result
                in sorted_results
                if result[stat] > 0.001][start:start+length % len(sorted_results)])
            ]
            ) + '```'
