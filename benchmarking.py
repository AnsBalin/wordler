import pandas as pd
from wordler import Wordle, KnowledgeState
import wordlist
from tqdm.notebook import tqdm
from collections import defaultdict


def bench_simple(strategy_factory, top_n=2000):
    wl = wordlist.Wordlist(top_n=top_n)
    score = {}

    for answer in tqdm(wl.data["word"].tolist()):

        wd = Wordle(answer)
        s = strategy_factory()
        s.run_strategy(wd)
        score[answer] = len(s.guesses_made)

    wl.data["score"] = wl.data.apply(lambda row: score.get(row["word"]), axis=1)
    return wl.data


def starting_guess(top_n):
    wl = wordlist.Wordlist(top_n=top_n)
    ks = KnowledgeState()
    words = wl.data["word"].tolist()
    total = defaultdict(int)
    max_so_far = 0

    for guess in tqdm(words):
        for answer in words:
            wd = Wordle(answer=answer)
            result = wd.evaluate_guess(guess, answer)
            regex = ks.regex(guess={"word": guess, "result": result})
            wl2data = wl.data[wl.data["matchstring"].str.contains(regex)]
            reduction = len(wl.data) - len(wl2data)
            total[guess] += reduction / (len(words) - 1)

        if total[guess] > max_so_far:
            max_so_far = total[guess]
            print(guess, max_so_far)

    wl.data["score"] = wl.data.apply(lambda row: total.get(row["word"]), axis=1)
    return wl.data
