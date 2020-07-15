# Mahjong scoring statistics

A score parser for Mahjong, written in Python.

Licensed under "MIT No Attribution" (MIT-0), see [LICENSE](LICENSE).

## Usage

Parse the Mahjong scores in `{scores file}.txt` and return a CSV of statistics
for full responsibility (全銃), one-n-two bucks (一二文), and half-spicy
increase (半辣上) under Kwong-tung (廣東牌) scoring:

    mahjong.py {scores file}.txt

### Optional argument `-m` or `--max` for maximum number of faan (番) (default 8)

    mahjong.py {...} -m {max faan}

### Optional argument `-s` or `--start` for start date (default 0)

    mahjong.py {...} -s {start date}

### Optional argument `-e` or `--end` for end date (default 10 ** 8)

    mahjong.py {...} -e {end date}

## Specifications for scores text file

1. Hash (`#`) **comments** out the remainder of a line
2. **Date** is specified by a line of digits `{yyyymmdd}`
   1. Extra digits are permitted but ignored
3. **Players** are specified by a line `{P1} {P2} {P3} {P4}`
   1. Whitespace can be any non-newline whitespace
   2. Player names cannot begin with a digit
   3. Player names cannot contain whitespace
   4. Player names cannot contain commas
   5. Player names cannot contain hyphens
4. A **game** is specified by a line `{S1} {S2} {S3} {S4}`
   1. Whitespace can be any non-newline whitespace
   2. Each `{Sn}` is either
      1. an integer, the winning number of faan
      2. `d`, for the discarding player (打出)
      3. `t`, for taking on all losses for a self-drawn win (包自摸)
      4. `f`, for a false win (詐糊)
      5. `-`, otherwise
5. Any other non-comment non-whitespace text is invalid

3-player games can also be scored; simply omit `{P4}` and `{S4}`.

## Simple example

Running `mahjong.py scores` for the following [`scores.txt`](scores.txt)

    20191214
    
    w x y z
    - - - - # Draw
    6 - - - # w self-drawn win, 6 faan
    - 3 d - # y discards, x wins, 3 faan
    - - t 8 # y takes on all losses, z self-drawn win
    - - f - # y false win
    
    # y swears never to play again and q replaces him
    
    w x q z
    - - 8 - # q self-drawn win, 8 faan
    
    # A 3-player game
    
    A B C
    d 3 - # A discards, B wins, 3 faan

results in the following output [`scores.csv`](scores.csv):

| player | games_played | games_won | net_score | games_won_pc | net_score_avg |
| --- | --- | --- | --- | --- | --- |
| q | 1 | 1 | 384 | 100 | 384.0 |
| z | 6 | 1 | 320 | 17 | 53.3 |
| w | 6 | 1 | 192 | 17 | 32.0 |
| B | 1 | 1 | 24 | 100 | 24.0 |
| C | 1 | 0 | 0 | 0 | 0.0 |
| A | 1 | 0 | -24 | 0 | -24.0 |
| x | 6 | 1 | -32 | 17 | -5.3 |
| y | 5 | 0 | -864 | 0 | -172.8 |
