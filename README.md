# `wordler.py`

`wordler` is a Wordle auto-solver which uses a tree-pruning strategy to compute sequential optimal guesses, able to solve most games in 3 or 4 guesses.

## Example Usage 
### 1. Run manually (with external game)

Instantiate a wordler strategy with an initial guess, and a dictionary size. `init_guess` can be any valid 5-letter word, and `top_n` will populate the dictionary with the _n_ highest ranked 5-letter words in the [Project Gutenberg frequency list](https://en.wiktionary.org/wiki/Wiktionary:Frequency_lists#Project_Gutenberg).

```python
from wordler import PruneStrategy, Tile
strat = PruneStrategy(top_n=4000, init_guess="stare")
```

Assuming you are manually playing the game, you can update the strategy with each result, and extract the next optimal guess. 

```python
strat.update_state(
    {
       "word": "stare",
       "result": [ Tile.GREY, Tile.YELLOW, Tile.GREY, Tile.GREY, Tile.GREY ]
    }
)
guess = strat.decide_guess()
print(guess)
```

This will print the next guess:

```
month
``` 


### 2. Run on simulated games 

To simulate the strategy on a wordle game with a particular answer, instantiate a `Wordle` object with an answer, and pass it to the strategy. The strategy will perform repeated guesses, updating its internal state with the gained knowledge and pruning its word list accordingly. 

You can run the strategy over many games this way to benchmark its performance:

```python
from wordler import Wordle 

for answer in [ "crate", "groom", "hello", "tiger", "proxy" ]:
    
    # Set up Wordle game with given answer
    wordle_game = Wordle(answer)
    
    # Initialize a PruneStrategy with the 4000 most common words in the dictionary and run it
    strat = PruneStrategy(top_n=4000, init_guess="stare")
    strat.run_strategy(wordle_game)
    
    print( answer, strat.guesses_made )
```
This will print:
```
crate ['stare', 'trace', 'crate']
groom ['stare', 'croon', 'brood', 'proof', 'groom']
hello ['stare', 'olden', 'hello']
tiger ['stare', 'tenor', 'tiger']
proxy ['stare', 'croon', 'proud', 'proxy']
```

## How does `PruneStrategy` work?

By considering the uncertaintly reduction that results from every (guess, answer) pair composed of words from the remaining possible word list, `PruneStrategy` selects the guess that maximises the _average_ uncertaintly reduction across all answers.

The uncertainty reduction is just the number of words we are able to rule out after making a particular guess, and is also dependent on knowledge gained from previous guesses.

## Benchmarking 

`benchmarking.py` provides some functions to benchmark a strategy and perform other analyses:

* `bench_simple(fn,top_n)`: Pass a function `fn` that instantiates a strategy, and dictionary size `top_n`, and this will compute the number of guesses required to obtain every possible answer in the dictionary.

```python
import benchmarking

def strat_factory():
    return PruneStrategy(init_guess="raise",top_n=2000)

benchmarking.bench_simple(strat_factory,2000)
```

* `starting_guess(top_n)`: For a dictionary containing the `top_n` most frequent words, find the best starting guess words based on the average wordlist reduction obtained. For example, the following are some of the better words when using a dictionary of size 2000:

```
word    avg. reduction
------------------------------
great   1915.8809404702274
those   1916.736368184117
years   1938.3111555777882
least   1946.3071535767901
tears   1956.0560280140282
raise   1957.1265632816398
```

With this dictionary size, the guess _great_ rules out 1915 words on average, which is not as good as _raise_ which averages 1957.