import wordlist
import copy
import string
import itertools
from collections import defaultdict

GREEN = 0
YELLOW = 1
GREY = 2

alphabet = string.ascii_lowercase


class Wordle:
    def __init__(self, answer=""):
        self.answer = answer

    def evaluate_guess(self, guess, answer=None):

        if answer is None:
            answer = self.answer

        result = [None, None, None, None, None]

        guess = list(guess)
        answer = list(answer)
        loose_chars = answer.copy()

        for i, (ch_pred, ch_target) in enumerate(zip(guess, answer)):

            if ch_pred == ch_target:
                result[i] = GREEN
                loose_chars.remove(ch_pred)

        for i, (ch_pred, ch_target) in enumerate(zip(guess, answer)):

            if result[i] == None:
                if ch_pred in loose_chars:
                    result[i] = YELLOW
                    loose_chars.remove(ch_pred)

                else:
                    result[i] = GREY

        return result


class KnowledgeState:
    def __init__(self):
        self.unknown_length = 5
        self.greens = ["" for _ in range(5)]
        self.yellows = [[] for _ in range(5)]
        self.greys = []

        self.mins = {ch: 0 for ch in alphabet}

    def guess_to_knowledge(self, guess, greens, yellows, greys):
        mins = {ch: 0 for ch in alphabet}
        word = list(guess["word"])
        result = guess["result"]
        for i, (ch, col) in enumerate(zip(word, result)):
            if col == GREEN:
                greens[i] = ch
                mins[ch] += 1

            elif col == YELLOW:
                yellows[i].append(ch)
                mins[ch] += 1

            else:  # col == GREY:
                greys.append(ch)
        return mins, greens, yellows, greys

    def commit_guess(self, guess):
        mins, _, _, _ = self.guess_to_knowledge(
            guess, self.greens, self.yellows, self.greys
        )

        self.mins = mins

    def regex(self, guess={}):

        greens = self.greens.copy()
        yellows = copy.deepcopy(self.yellows)
        greys = self.greys.copy()
        mins = self.mins.copy()

        word_regex = ["" for _ in range(5)]
        counts_regex = ["" for _ in range(26)]

        if guess:
            mins, greens, yellows, greys = self.guess_to_knowledge(
                guess, greens, yellows, greys
            )

        for i in range(5):
            if greens[i]:
                word_regex[i] = greens[i]

            elif yellows[i]:
                word_regex[i] = "[^" + "|".join(yellows[i]) + "]"

            else:
                word_regex[i] = "."

        for i, ch in enumerate(alphabet):
            min_count = mins[ch]
            if ch in greys:

                max_count = min_count
            else:
                max_count = 5

            if max_count == 5 and min_count == 0:
                counts_regex[i] = "."
            elif max_count == min_count:
                counts_regex[i] = str(min_count)
            else:
                counts_regex[i] = "[" + str(min_count) + "-" + str(max_count) + "]"

        return "^" + "".join(word_regex) + "".join(counts_regex) + "$"


class Strategy:
    def __init__(self, top_n=6000, init_guess="stare"):
        self.ks = KnowledgeState()
        self.init_guess = init_guess
        self.wl = wordlist.Wordlist(top_n=top_n)
        self.wd = Wordle()
        self.guesses_made = []

    def decide_guess(self):
        # Implement in derived classes
        return ""

    def make_guess(self):

        if len(self.guesses_made) == 0:
            guess = self.init_guess

        else:
            guess = self.decide_guess()

        return guess

    def update_state(self, guess_result):
        self.ks.commit_guess(guess_result)
        regex = self.ks.regex()
        self.wl.data = self.wl.data[self.wl.data["matchstring"].str.contains(regex)]
        self.guesses_made.append(guess_result["word"])

    def run_strategy(self, wd_real):

        while len(self.wl.data) > 1:
            guess = self.make_guess()
            result = wd_real.evaluate_guess(guess)
            self.update_state({"word": guess, "result": result})

        guess = self.wl.data["word"].tolist()[0]
        self.guesses_made.append(guess)


class PruneStrategy(Strategy):
    def decide_guess(self):

        words = self.wl.data["word"].tolist()
        total = defaultdict(int)

        for (guess, answer) in itertools.product(words, words):
            if answer == guess:
                continue
            print(guess, answer)
            result = self.wd.evaluate_guess(guess, answer)
            regex = self.ks.regex(guess={"word": guess, "result": result})
            wl2data = self.wl.data[self.wl.data["matchstring"].str.contains(regex)]
            reduction = len(self.wl.data) - len(wl2data)
            total[guess] += reduction / (len(words) - 1)

        max_reduction = max(total.values())
        best = [
            word for (word, reduction) in total.items() if reduction == max_reduction
        ][0]

        return best


class FreqStrategy(Strategy):
    def decide_guess(self):
        # just guess most common word as baseline
        return self.wl.top_by_rank(1)[0]


if __name__ == "__main__":
    exit()
