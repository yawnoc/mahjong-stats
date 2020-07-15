#!/usr/bin/env python3

"""
----------------------------------------------------------------
mahjong.py
----------------------------------------------------------------

Parse the Mahjong scores in {scores file}.txt and return a CSV of statistics
for full responsibility (全銃), one-n-two bucks (一二文), and half-spicy
increase (半辣上) under Kwong-tung (廣東牌) scoring:
  mahjong.py {scores file}.txt

Optional argument -m or --max for maximum number of faan (番) (default 8):
  mahjong.py {...} -m {max faan}

Optional argument -s or --start for start date (default 0):
  mahjong.py {...} -s {start date}

Optional argument -e or --end for end date (default 10 ** 8):
  mahjong.py {...} -e {end date}

Specifications for plain-text file of Mahjong scores:

1. Hash (#) comments out the remainder of a line
2. Date is specified by a line of digits {yyyymmdd}
    2.1 Extra digits are permitted but ignored
3. Players are specified by a line {P1} {P2} {P3} {P4}
    3.1 Whitespace can be any non-newline whitespace
    3.2 Player names cannot begin with a digit
    3.3 Player names cannot contain whitespace
    3.4 Player names cannot contain commas
    3.5 Player names cannot contain hyphens
4. A game is specified by a line {S1} {S2} {S3} {S4}
    4.1 Whitespace can be any non-newline whitespace
    4.2 Each {Sn} is either
        (1) an integer, the winning number of faan
        (2) d, for the discarding player (打出)
        (3) t, for taking on all losses for a self-drawn win (包自摸)
        (4) f, for a false win (詐糊)
        (5) -, otherwise
5. Any other non-comment non-whitespace text is invalid

3-player games can also be scored; simply omit {P4} and {S4}.
"""

from collections import OrderedDict
import argparse
import re



DEFAULT_MAX_FAAN = 8
DEFAULT_START_DATE = 0
DEFAULT_END_DATE = 10 ** 8



def add_player(stats_dict, player):
  """
  Add a player to a dictionary of statistics.
  """
  
  # If player has no previous record
  if player not in stats_dict:
    
    # Provide a clean slate of additive statistics
    stats_dict[player] = {stat: 0 for stat in stat_list_additive()}



def stat_list_additive():
  """
  Return list of the additive statistics.
  """
  
  return [
    'games_played',
    'games_won',
    'net_score'
  ]

def stat_list_rates():
  """
  Return list of the non-additive statistics (rates).
  """
  
  return [
    'games_won_pc',
    'net_score_avg'
  ]


def base_amount(faan):
  """
  Return the base amount for a given number of faan.
  Under one-n-two bucks (一二文) and half-spicy increase (半辣上):
    Faan  Amount
      0       1
      1       2
      2       4
      3       8
      4      16
      5      24
      6      32
      7      48
      8      64
      9      96
     10     128
  etc. (i.e. doubling up to 4 faan,
  then midpoint insertions for odd faan)
  """
  
  if faan <= 4:
    return 2 ** faan
    
  elif faan % 2 == 1:
    return 24 * 2 ** ((faan - 5) // 2)
    
  else:
    return 32 * 2 ** ((faan - 6) // 2)


def dict_to_csv(stats_dict):
  """
  Convert a dictionary of statistics to a CSV string.
  """
  
  # List of all statistics
  stat_list = stat_list_additive() + stat_list_rates()
  
  # Compute rates (non-additive statistics) for all players
  for player in stats_dict:
    p = stats_dict[player]
    p['games_won_pc'] = p['games_won'] / p['games_played'] * 100
    p['net_score_avg'] = p['net_score'] / p['games_played']
  
  # Sort dictionary by average net score (before rounding below)
  # with tie breaking by player name
  stats_dict_sorted = OrderedDict(
    sorted(
      stats_dict.items(),
      key = lambda x: (-x[1]['net_score'], x[0])
    )
  )
  
  # Round rates to sensible number of decimal places
  for player in stats_dict:
    p = stats_dict[player]
    p['games_won_pc'] = round(p['games_won_pc'])
    p['net_score_avg'] = round(p['net_score_avg'], 1)
  
  # Headings for CSV string of statistics
  stats_csv = list_to_csv_line(['player'] + stat_list)
  
  # Append all (non-combined) players' rows sorted by average cards lost
  for player in stats_dict_sorted:
    stats_csv += list_to_csv_line(
      [player] + [str(stats_dict[player][stat]) for stat in stat_list]
    )
  
  return stats_csv



def list_to_csv_line(list_):
  """
  Convert a list to a string for a line of a CSV.
  """
  
  return ','.join(list_) + '\n'


def file_to_dict(file_name, max_faan, start_date, end_date):
  """
  Generate a dictionary of stats from a file of Mahjong scores.
  """
  
  def raise_exception(message):
    """
    Raise an exception, noting the current line.
    """
    raise Exception(
      f'LINE {line_num} OF {file_name}.txt INVALID: {message}'
    )
  
  # Regular expression for line specifying player names
  name_pattern = r'([^0-9\s,\-][^\s,\-]*)'
  space_pattern = r'\s+'
  names_regex = re.compile(
    '^'
    + 2 * (name_pattern + space_pattern)
    + name_pattern
    + f'(?:{space_pattern + name_pattern})?'
    + '$'
  )
  
  # Regular expression for line specifying a game
  spec_pattern = r'([0-9]+|[dtf\-])'
  space_pattern = r'\s+'
  game_regex = re.compile(
    '^'
    + 2 * (spec_pattern + space_pattern)
    + spec_pattern
    + f'(?:{space_pattern + spec_pattern})?'
    + '$'
  )
  
  def cap_faan(faan):
    """
    Cap the winning number of faan at the maximum
    """
    return min(max_faan, int(faan))
  
  def parse_spec_list(spec_list, num_players):
    """
    Parse a list of scoring specifications into win and net score lists
    """
    hyphen_count = spec_list.count('-')
    is_integer_list = [spec.isdigit() for spec in spec_list]
    integer_count = is_integer_list.count(True)
    
    # Default to no change to additive statistics (except games played)
    win_list = num_players * [0]
    net_score_list = num_players * [0]
    
    # Draw (摸和)
    if hyphen_count == num_players:
      
      # No changes
      return [win_list, net_score_list]
    
    if hyphen_count == num_players - 1:
      
      # False win (詐糊)
      if spec_list.count('f') == 1:
        
        # False-winning player pays 2x max base amount
        # to each of the (N - 1) other players
        false_index = spec_list.index('f')
        for n in range(num_players):
          if n == false_index:
            net_score_list[n] = -2 * (num_players - 1) * base_amount(max_faan)
          else:
            net_score_list[n] = 2 * base_amount(max_faan)
        return [win_list, net_score_list]
      
      # Self-drawn win (自摸)
      if integer_count == 1:
        
        # Winning player receives 2x winning base amount
        # from each of the (N - 1) other players
        winner_index = is_integer_list.index(True)
        win_list[winner_index] = 1
        winning_faan = cap_faan(spec_list[winner_index])
        for n in range(num_players):
          if n == winner_index:
            net_score_list[n] = (
              2 * (num_players - 1) * base_amount(winning_faan)
            )
          else:
            net_score_list[n] = (
              -2 * base_amount(winning_faan)
            )
        return [win_list, net_score_list]
    
    if hyphen_count == num_players - 2:
      
      # Discarded win (打出)
      if integer_count == 1 and spec_list.count('d') == 1:
        
        # Winning player receives (2 + (N - 2))x == Nx winning base amount
        # from discarding player
        #   2     : 1 double-portion for the discarding player
        #   N - 2 : N - 2 single-portions on behalf of the bystanders (閒家)
        #           (since scoring is full responsibility (全銃))
        winner_index = is_integer_list.index(True)
        win_list[winner_index] = 1
        winning_faan = cap_faan(spec_list[winner_index])
        discarding_index = spec_list.index('d')
        net_score_list[winner_index] = (
          num_players * base_amount(winning_faan)
        )
        net_score_list[discarding_index] = (
          -num_players * base_amount(winning_faan)
        )
        return [win_list, net_score_list]
      
      # Taking on all losses for a self-drawn win (包自摸)
      if integer_count == 1 and spec_list.count('t') == 1:
        
        # Winning player receives 2(N - 1)x winning base amount
        # from taking-on player
        winner_index = is_integer_list.index(True)
        win_list[winner_index] = 1
        winning_faan = cap_faan(spec_list[winner_index])
        taking_on_index = spec_list.index('t')
        net_score_list[winner_index] = (
          2 * (num_players - 1) * base_amount(winning_faan)
        )
        net_score_list[taking_on_index] = (
          -2 * (num_players - 1) * base_amount(winning_faan)
        )
        return [win_list, net_score_list]
      
      # Otherwise the line is invalid
      raise_exception('does not properly specify a game')
  
  # Import .txt file as string
  with open(f'{file_name}.txt', 'r', encoding='utf-8') as txt_file:
    txt_file_string = txt_file.read()
  
  # Whether the start date has been reached
  start_reached = True
  
  # Whether the end date has been exceeded
  end_exceeded = False
  
  # Initialise dictionary
  stats_dict = {}
  
  # Line-by-line:
  for line_num, line in enumerate(txt_file_string.splitlines(), 1):
    
    # Strip comments
    line = re.sub(r'#[\s\S]*', '', line)
    
    # Strip leading and trailing whitespace
    line = re.sub(r'^\s+', '', line)
    line = re.sub(r'\s+$', '', line)
    
    # If line specifies date
    if line.isdigit():
      
      # Extract first 8 digits {yyyymmdd}
      yyyymmdd = int(line[:8])
      
      # Whether the start date has been reached
      start_reached = yyyymmdd >= start_date
      
      # Whether the end date has been exceeded
      end_exceeded = yyyymmdd > end_date
      
      # Go to next line
      continue
    
    # If within date range
    if start_reached and not end_exceeded:
      
      # If line specifies player names
      names_match = names_regex.match(line)
      if names_match:
        
        # Get number of players
        if names_match.group(4) is None:
          num_players = 3
        else:
          num_players = 4
        
        # Set list of players
        player_list = [names_match.group(n) for n in range(1, 1 + num_players)]
        
        # Check for duplicate players
        if len(player_list) != len(set(player_list)):
          raise_exception('duplicate player')
        
        # Add players to dictionary of statistics
        for player in player_list:
          add_player(stats_dict, player)
        
        # Go to next line
        continue
      
      # If line specifies a game
      game_match = game_regex.match(line)
      if game_match:
        
        # Players must already have been specified
        if 'player_list' not in locals():
          raise_exception('players must be specified before a game')
        
        # Get number of scoring specifications
        if game_match.group(4) is None:
          num_specs = 3
        else:
          num_specs = 4
        
        # Number of scoring specifications must match number of players
        if num_players != num_specs:
          raise_exception(
            f'{num_specs} scores given for {num_players} players'
          )
        
        # Extract list of scoring specifications
        spec_list = [game_match.group(n) for n in range(1, 1 + num_players)]
        
        # Parse into win and net (zero-sum) score lists
        win_list, net_score_list = parse_spec_list(spec_list, num_players)
        
        # Update players' games played, games won and net scores
        for n, player in enumerate(player_list):
          p = stats_dict[player]
          p['games_played'] += 1
          p['games_won'] += win_list[n]
          p['net_score'] += net_score_list[n]
        
        # Go to next line
        continue
      
      # Otherwise if the line is non-empty, it is invalid
      if line != '':
        raise_exception(
          'does not properly specify one of date, players or game'
        )
      
    # (If not within date range, ignore the line)
    
  return stats_dict

################################################################
# Main
################################################################

def main(args):
  
  # File name
  file_name = args.file_name
  
  # Remove trailing "." or ".txt" if provided
  file_name = re.sub(r'\.(txt)?$', '', file_name)
  
  # Export file name
  file_name_export = file_name
  
  # Maximum number of faan
  max_faan = args.max_faan
  if max_faan != DEFAULT_MAX_FAAN:
    file_name_export += f'-m_{max_faan}'
  
  # Start date
  start_date = args.start_date
  if start_date != DEFAULT_START_DATE:
    file_name_export += f'-s_{start_date}'
  
  # End date
  end_date = args.end_date
  if end_date != DEFAULT_END_DATE:
    file_name_export += f'-e_{end_date}'
  
  # Generate dictionary of statistics from file
  stats_dict = file_to_dict(file_name, max_faan, start_date, end_date)
  
  # Convert into CSV string of statistics
  stats_csv = dict_to_csv(stats_dict)
  
  # Export .csv file
  with open(file_name_export + '.csv', 'w', encoding='utf-8') as csv_file:
    csv_file.write(stats_csv)

################################################################
# Argument parsing
################################################################

if __name__ == '__main__':
  
  # Description
  parser = argparse.ArgumentParser(
    description='Generates Mahjong statistics'
  )
  
  # Arguments
  parser.add_argument(
    'file_name',
    help='File name of Mahjong scores file',
    metavar='file_name[.[txt]]'
  )
  parser.add_argument(
    '-m',
    '--max',
    dest='max_faan',
    help=f'Maximum number of faan (default {DEFAULT_MAX_FAAN})',
    nargs='?',
    default=DEFAULT_MAX_FAAN,
    type=int
  )
  parser.add_argument(
    '-s',
    '--start',
    dest='start_date',
    help=f'Start date (default {DEFAULT_START_DATE})',
    nargs='?',
    default=DEFAULT_START_DATE,
    type=int
  )
  parser.add_argument(
    '-e',
    '--end',
    dest='end_date',
    help=f'End date (default {DEFAULT_END_DATE})',
    nargs='?',
    default=DEFAULT_END_DATE,
    type=int
  )
  
  # Run
  main(parser.parse_args())
