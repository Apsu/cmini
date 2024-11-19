import os
import json

import multiprocessing as mp

import time
from core.keyboard import Layout
from util import corpora, analyzer, memory


def cache_get(name: str) -> dict | None:
    name = name.lower()
    if not os.path.exists(f'cache/{name}.json'):
        return None

    with open(f'cache/{name}.json') as f:
        return json.load(f)


def layout_get(name: str):
    return memory.parse_file(f"layouts/{name}.json")


def cache_fill(ll: Layout, data: dict | None, corpus: str) -> dict[str, dict]:
    stats = {
        **analyzer.trigrams(ll, corpora.load_json(f'corpora/{corpus}/trigrams.json')),
        **analyzer.bigrams(ll, corpora.load_json(f'corpora/{corpus}/bigrams.json'))
    }
    update = {corpus: stats}

    if data is not None:
        # print("Existing cache updating")
        data.update(update)
        return data
    else:
        # print("Fresh cache")
        return update


def update(name: str, data: dict):
    with open(f'cache/{name}.json', "w", encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)

    return data


def get(name: str, corpus: str):
    name = name.lower()
    corpus = corpus.lower()

    if not name or not corpus:
        return None

    if (data := cache_get(name)) is not None:
        if corpus in data:
            # print("Returning cached data")
            return data[corpus]

    data = update(name, cache_fill(memory.find(name), data, corpus))
    return data[corpus]


def cache_files(file_chunks: list[str]):
    for file in file_chunks:
        name = os.path.splitext(file)[0]
        ll = memory.parse_file(f"layouts/{name}.json")
        data = cache_get(name)

        for corpus_file in os.scandir('corpora'):
            corpus = corpus_file.name.split(".json")[0]
            print(f"Layout: {name}, Corpus: {corpus}")
            data = cache_fill(ll, data, corpus)

        update(name, data)

def timing(func):
    def wrapper(*args, **kwargs):
        start_t = time.perf_counter()
        res = func(*args, **kwargs)
        end_t = time.perf_counter()
        print(f"Time elapsed for {func.__name__}: {end_t - start_t}s")
        return res
    return wrapper

@timing
def cache_main_new():
    files = os.listdir('layouts')
    num_processes = mp.cpu_count()

    with mp.Pool(processes=num_processes) as pool:
        pool.map(cache_files, [files[i::num_processes] for i in range(num_processes)])

@timing
def cache_main_original():
    files = os.listdir('layouts')
    cache_files(files)

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        cache_main_original()
        # cache_main_new()
    else:
        print(get(sys.argv[1], sys.argv[2]))
