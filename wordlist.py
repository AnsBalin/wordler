import pandas as pd
import base64


def get_word_freq():

    words_list = []
    words_freq = {}
    words_rank = {}

    with open("wordlist_condensed.txt", "rb") as f:
        n = 1

        content = f.read()
        content = base64.b64decode(content)
        content = content.decode("ascii")

        lines = content.split("\n")
        for line in lines:

            line = line.split("\t")
            words_list.append([n, line[0], float(line[1]), int(line[2])])
            words_freq[line[0]] = float(line[1])
            words_rank[line[0]] = n

            n += 1

    return words_list


class Wordlist:
    def __init__(self, top_n=None):

        word_list = get_word_freq()

        for row in word_list:
            word = row[1]
            counts = []
            for ch in "abcdefghijklmnopqrstuvwxyz":
                counts.append(str(word.count(ch)))

            row.append("".join(counts))
            row.append(word + "".join(counts))

        self.data = pd.DataFrame(
            word_list,
            columns=[
                "rank",
                "word",
                "freq",
                "wordle_solution",
                "counts",
                "matchstring",
            ],
        )

        if top_n is not None:
            self.data = self.data.nlargest(top_n, columns="freq")

    def top_by_rank(self, n):
        return self.data.nlargest(n, columns="freq")["word"].tolist()
