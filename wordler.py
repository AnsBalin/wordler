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

        # Need two passes through. To determine if a letter is yellow or not, we need to
        # have already counted any green instances of it. The loose_chars list effectively
        # keeps track of this.
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
        # represents the location of any known greens
        self.greens = ["" for _ in range(5)]
        # represents a list of known excluded characters from a given position.
        self.yellows = [[] for _ in range(5)]
        # represents list of characters excluded from any position
        self.greys = []
        # known min bound for each character (eg if we know there is at least 1 'p')
        self.mins = {ch: 0 for ch in alphabet}

    def guess_to_knowledge(self, guess, greens, yellows, greys):
        '''
        Take a guess result in the form { word: "apple", result: [GREEN, GREY, GREY, YELLOW, GREY])
        and update the internal representation of the knowledge state based on this result.
        '''

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
        '''
        Actually update the current knowledge state.
        '''
        mins, _, _, _ = self.guess_to_knowledge(
            guess, self.greens, self.yellows, self.greys
        )

        self.mins = mins

    def regex(self, guess={}):
        '''
        Express knowledge state as a regex to be used to filter wordlist matchstring. 

        Matchstrings are of the form WORD + COUNT 

            apple10001000000120000000000000
            |WORD|-----COUNT histogram----|

        If we know the following
            * first letter is a (GREEN)
            * does not contain k, b, i (GREY)
            * contains at least one p, not in position 3 (YELLOW)

        then the regex which will match all such words is:

            /^a..[^p]..0......0.0....[1-5]..........$/
              123  4 5abcdefghijklmno  p  qrstuvwxyz
        '''

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

        # WORD regex
        for i in range(5):
            if greens[i]:
                # match exact char
                word_regex[i] = greens[i]

            elif yellows[i]:
                # match anything other than set of chars eg. not x,y,z: [^x|y|z]
                word_regex[i] = "[^" + "|".join(yellows[i]) + "]"

            else:
                # match any char
                word_regex[i] = "."

        # COUNTS regex
        for i, ch in enumerate(alphabet):
            min_count = mins[ch]

            # Set upper bounds based on greys
            if ch in greys:
                # if grey, bound by known min
                max_count = min_count
            else:
                max_count = 5

            # If count is bounded [0-5] then match any count
            if max_count == 5 and min_count == 0:
                counts_regex[i] = "."

            # if max = min = 1, then just match '1'
            elif max_count == min_count:
                counts_regex[i] = str(min_count)

            # Match any count char in range '[min-max]'
            else:
                counts_regex[i] = "[" + \
                    str(min_count) + "-" + str(max_count) + "]"

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

    def update_state(self, guess_result):
        self.ks.commit_guess(guess_result)
        regex = self.ks.regex()
        self.wl.data = self.wl.data[self.wl.data["matchstring"].str.contains(
            regex)]
        self.guesses_made.append(guess_result["word"])

    def run_strategy(self, wd_real):

        while len(self.wl.data) > 1:
            guess = self.decide_guess()
            result = wd_real.evaluate_guess(guess)
            self.update_state({"word": guess, "result": result})

        final_guess = self.wl.data["word"].tolist()[0]
        if final_guess != guess:
            self.guesses_made.append(final_guess)


class PruneStrategy(Strategy):
    def decide_guess(self):
        # For every possible guess (given knowledge state), compute the wordlist reduction
        # that would occur as a result of making that guess averaged across all other possible words.

        if len(self.guesses_made) == 0:
            return self.init_guess

        words = self.wl.data["word"].tolist()
        total = defaultdict(int)

        for (guess, answer) in itertools.product(words, words):
            if answer == guess:
                continue

            result = self.wd.evaluate_guess(guess, answer)
            regex = self.ks.regex(guess={"word": guess, "result": result})
            wl2data = self.wl.data[self.wl.data["matchstring"].str.contains(
                regex)]
            reduction = len(self.wl.data) - len(wl2data)
            total[guess] += reduction / (len(words) - 1)

        return max(total, key=total.get)


class FreqStrategy(Strategy):
    def decide_guess(self):
        # just guess most common word as baseline

        if len(self.guesses_made) == 0:
            return self.init_guess

        return self.wl.top_by_rank(1)[0]


if __name__ == "__main__":
    exit()
