from wordler import Wordle, KnowledgeState, GREEN, YELLOW, GREY


def test_evaluate_guess():

    wordle = Wordle()
    answer = "apple"

    guess1 = "xzbor"
    guess2 = "axxxx"
    guess3 = "axxxp"
    guess4 = "axpxp"
    guess5 = "appxp"
    guess6 = "appep"

    assert wordle.evaluate_guess(guess1, answer) == [
        GREY, GREY, GREY, GREY, GREY]
    assert wordle.evaluate_guess(guess2, answer) == [
        GREEN, GREY, GREY, GREY, GREY]
    assert wordle.evaluate_guess(guess3, answer) == [
        GREEN, GREY, GREY, GREY, YELLOW]
    assert wordle.evaluate_guess(guess4, answer) == [
        GREEN, GREY, GREEN, GREY, YELLOW]
    assert wordle.evaluate_guess(guess5, answer) == [
        GREEN, GREEN, GREEN, GREY, GREY]
    assert wordle.evaluate_guess(guess6, answer) == [
        GREEN, GREEN, GREEN, YELLOW, GREY]

    answer = "aaaaa"
    guess = "aabbb"
    assert wordle.evaluate_guess(guess, answer) == [
        GREEN, GREEN, GREY, GREY, GREY]


def test_regex():
    ks = KnowledgeState()

    guess1 = {"word": "apple", "result": [GREEN, GREY, GREY, GREY, GREY]}
    regex1 = ks.regex(guess=guess1)

    guess2 = {"word": "apple", "result": [YELLOW, GREY, GREY, GREY, GREY]}
    regex2 = ks.regex(guess=guess2)

    guess3 = {"word": "apple", "result": [GREEN, GREY, YELLOW, GREY, GREY]}
    regex3 = ks.regex(guess=guess3)

    guess4 = {"word": "apple", "result": [GREEN, YELLOW, GREEN, GREY, GREY]}
    regex4 = ks.regex(guess=guess4)

    assert regex1 == "^a....[1-5]...0......0...0..........$"
    assert regex2 == "^[^a]....[1-5]...0......0...0..........$"
    assert regex3 == "^a.[^p]..[1-5]...0......0...1..........$"
    assert regex4 == "^a[^p]p..[1-5]...0......0...[2-5]..........$"
