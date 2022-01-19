import pandas as pd
import base64


def read_wordlist():
    """
    Read wordlist from local file.
    """

    words_list = []

    with open("wordlist.b64", "rb") as f:

        content = f.read()
        content = base64.b64decode(content)
        content = content.decode("ascii")

        lines = content.split("\n")
        for n, line in enumerate(lines):

            line = line.split("\t")
            words_list.append([n, line[0], float(line[1]), int(line[2])])

    return words_list


class Wordlist:
    def __init__(self, top_n=None):

        word_list = read_wordlist()

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
