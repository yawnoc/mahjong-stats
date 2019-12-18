# Mahjong scoring statistics

A score parser for Mahjong, written in Python.

## Usage

Parse the Mahjong scores in `{scores file}.txt` and return a CSV of statistics
for full responsibility (全銃), one-n-two bucks (一二文), and half-spicy
increase (半辣上) under Kwong-tung (廣東牌) scoring:

    mahjong.py {scores file}

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

## Simple example

Running `mahjong.py scores` for the following [`scores.txt`](scores.txt)

    20191214
    
    伯 仲 叔 季
    - - - - # 摸和
    6 - - - # 伯自摸六番
    - 3 d - # 叔出銃三番畀仲
    - - t 8 # 叔包季自摸
    - - f - # 叔食詐糊
    
    # 叔誓不再打牌而賭神替之
    
    伯 仲 賭神 季
    - - 8 - # 賭神自摸十三么

results in the following output [`scores.csv`](scores.csv):

| player | games_played | games_won | net_score | games_won_pc | net_score_avg |
| --- | --- | --- | --- | --- | --- |
| 賭神 | 1 | 1 | 384 | 100 | 384.0 |
| 季 | 6 | 1 | 320 | 17 | 53.3 |
| 伯 | 6 | 1 | 192 | 17 | 32.0 |
| 仲 | 6 | 1 | -32 | 17 | -5.3 |
| 叔 | 5 | 0 | -864 | 0 | -172.8 |