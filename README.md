# `wordler.py`

`wordler` is a Wordle auto-solver which uses a tree-pruning strategy to compute sequential optimal guesses, able to solve most games in 3 or 4 guesses.

## Example Usage 
### 1. Run manually (with external game)

Instantiate a wordler strategy with an initial guess, and a dictionary size. `init_guess` can be any valid 5-letter word, and `top_n` will ensure the dictionary is populated with the $n$ highest ranked 5-letter words in the [Project Gutenberg frequency list](https://en.wiktionary.org/wiki/Wiktionary:Frequency_lists#Project_Gutenberg).

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

To simulate the strategy on a wordle game with a particular answer, instantiate a `Wordle` with an answer, and pass it to the strategy. The strategy will perform repeated guesses, updating its internal state with the gained knowledge and pruning its word list accordingly. 

We can run the strategy over many games this way to benchmark its performance:

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