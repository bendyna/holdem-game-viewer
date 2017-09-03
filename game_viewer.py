import json
from termcolor import colored
from collections import defaultdict
import pandas as pd

CARD_COLORS = {'H': 'red', 'D': 'green', 'C': 'cyan', 'S': 'magenta'}
STREET_CARDS = {'preflop': 0, 'flop': 3, 'turn': 4, 'river': 5}
NAME_USER = {}
players_table = pd.read_csv('players.csv', header=0)
for i, row in players_table.iterrows():
    NAME_USER[row['name']] = row['User']


def pretty_cards_str(cards):
    return ' '.join(colored(s[1], CARD_COLORS[s[0]]) for s in cards)


class Player:

    SHORT_ACTION = {'SMALLBLIND': 'SB', 'BIGBLIND': 'BB', 'FOLD': 'F',
                    'CALL': 'C', 'RAISE': 'R'}

    def __init__(self, pos, json_seat):
        self.pos = pos
        self.start_stack = json_seat['start_stack']
        self.uuid = json_seat['uuid']
        self.name = json_seat['name']
        self.hole_card = json_seat['hole_card']
        self.actions = defaultdict(list)
        self.current_street = ''

    def add_action(self, action_street, circle_num, json_action):
        short_name = self.SHORT_ACTION[json_action['action']]
        amount = 0 if short_name == 'F' else json_action['amount']
        self.actions[action_street].append((circle_num, short_name, amount))

    def actions_str(self):
        circle_last = -1
        strs = []
        for circle_num, short_name, amount in self.actions[self.current_street]:
            if circle_num - circle_last > 1:
                strs.append(' ' * 12 * (circle_num - circle_last - 1))
            circle_last = circle_num
            strs.append('{:>5} {:6}'.format(short_name, amount if amount > 0 else ''))
        return ''.join(strs)

    def __str__(self):
        return '{:<4} {:25}  {:4}    {}   {}'.format(self.pos,
                                                     NAME_USER[self.name],
                                                     self.start_stack,
                                                     pretty_cards_str(self.hole_card),
                                                     self.actions_str())

with open('games_09_02/game_0000.json') as json_data:
    game = json.load(json_data)
    for num_round, curr_round in enumerate(game['rounds']):
        print('\n{:=^70}'.format('ROUND {}'.format(num_round)))
        players = [Player(i, seat) for i, seat in enumerate(curr_round['round_state']['seats'])]
        uuid_player = {}
        for seat, player in enumerate(players):
            uuid_player[player.uuid] = seat, player
        action_histories = curr_round['round_state']['action_histories']
        community_cards = curr_round['round_state']['community_card']
        for street in ['preflop', 'flop', 'turn', 'river']:

            if street in action_histories and action_histories[street]:
                street_cards = pretty_cards_str(community_cards[:STREET_CARDS[street]])
                print('\n{:-^50}\n\n{:^20}{}\n'.format(street, '', street_cards))
                num = 0
                last = None
                for i, action in enumerate(action_histories[street]):
                    seat, player = uuid_player[action['uuid']]
                    if last is not None and seat < last:
                        num += 1
                    player.add_action(street, num, action)
                    last = seat
                for player in players:
                    player.current_street = street
                    if player.start_stack > 0:
                        print(player)
        print('\n{:^20}{}\n'.format('', pretty_cards_str(community_cards)))
