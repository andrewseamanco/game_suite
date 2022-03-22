import card_classes
import blackjack_enums
from prompt_toolkit import prompt
import blackjack_player_classes
from regression_agent import Regression_Agent
import argparse
import random
import time


class game_setup:
    def __init__(self, args):
        self.users = []
        if not args.use_args:
            self.setup()
        else:
            self.users = [blackjack_player_classes.user(name) for name in args.players]
            self.min_bet = args.min_bet
            self.bot_num = args.bot_num
            self.players = self.generate_table_players(args.bot_num)
            self.num_rounds = args.num_rounds

    def setup(self):
        print(f"Welcome to the Blackjack Table!")
        self.min_bet = int(prompt(f"What do you want this tables minimum bet to be? \n"))
        player_num = prompt(f"How many players would like to play? \n")
        print(f"How many rounds would you like to play?")
        self.num_rounds = int(prompt(f"(Hint) Enter -1 to play until you run out of chips or are the last player at the table. \n"))
        for _ in range(int(player_num)):
            self.users.append(self.create_player())
        self.bot_num = int(prompt(f"How many other players would you like to be at this table? \n"))
        self.players = self.generate_table_players(self.bot_num)

    def create_player(self):
        player_name = prompt("What is your player name? \n")
        print(f"Welcome to the blackjack table!")

        return blackjack_player_classes.user(player_name)

    def generate_table_players(self, bot_num):
        bots = []
        for _ in range(0, bot_num):
            bot_name = self.generate_bot_name()
            while bot_name in [bot.name for bot in bots]:
                bot_name = self.generate_bot_name()

            bots.append(blackjack_player_classes.bot(bot_name))
            bots.append(Regression_Agent("Ringer", 'blackjack-data.json', False))

        table = bots + self.users
        random.shuffle(table)

        return table

    def generate_bot_name(self):
        BOT_ADJECTIVES = ["Random", "Perfect", "Great", "Fortuitous", "Data", "Fast", "Slow", "Fantastic", "Dream", "Late", "California", "Colorado", "Surfer", "Lucky"]
        BOT_NAMES = ["Hedgehog", "Intern", "Heart", "Bronco", "Andrew", "Annie", "Wave", "Horse", "Monkey", "Papi", "Skiis", "Lover", "Island", "Spaceship", "Scientist"]

        return f"{random.choice(BOT_ADJECTIVES)}_{random.choice(BOT_NAMES)}_{random.randint(0,99)}"

class blackjack_game:
    def __init__(self, setup):
        self.deck = card_classes.Deck(2)
        self.deck.shuffle()
        self.min_bet = setup.min_bet
        self.players = setup.players
        self.num_rounds = setup.num_rounds
        self.dealer = blackjack_player_classes.Dealer()
        self.dealerScore = 0

    def deal_hand(self):
        for round in range(0,2):
            for player in self.players:
                card = player.dealCard(self.deck)
                print(f"The dealer has dealed {player.name} a {card}")
                time.sleep(1)
            dealerCard = self.dealer.dealCard(self.deck)
            card_notification = "hidden card" if round == 1 else dealerCard
            print(f"The dealer has dealed themself a {card_notification}")
        print()

    def play_round(self):
        for player in self.players:
            player.bet(self)
            player.turnInfo(self)           
            player.play_turn(self)
            print()
        self.dealer.turnInfo()
        self.dealer.play_turn(self)
        print()

    def evaluate_round(self):
        dealer_score = self.dealer.evaluate()
        if dealer_score > 21:
            for player in self.players:
                if player.evaluate() > 21:
                    player.gameState = blackjack_enums.GameState.Push
                elif player.evaluate() == 21:
                    player.gameState = blackjack_enums.GameState.Blackjack
                else:
                    player.gameState = blackjack_enums.GameState.Win
        if dealer_score == 21:
            for player in self.players:
                if player.evaluate() > 21 or player.evaluate() < 21:
                    player.gameState = blackjack_enums.GameState.Loss
                elif player.evaluate() == 21:
                    player.gameState = blackjack_enums.GameState.Push
        if dealer_score < 21:
            for player in self.players:
                if player.evaluate() == dealer_score:
                    player.gameState = blackjack_enums.GameState.Push
                elif player.evaluate() > 21:
                    player.gameState = blackjack_enums.GameState.Loss
                elif player.evaluate() < dealer_score:
                    player.gameState = blackjack_enums.GameState.Loss                   
                elif player.evaluate() > dealer_score:
                    player.gameState = blackjack_enums.GameState.Win
                elif player.evaluate() == 21:
                    player.gameState = blackjack_enums.GameState.Blackjack

    def distribute_chips(self):
        for player in self.players:
            if player.gameState == blackjack_enums.GameState.Blackjack:
                win = int((player.wager * 1.5)+.5)
                player.chips = player.chips + win
                print(f"{player.name} has recieved a blackjack and been paid {win} chips at {player.evaluate()}")
            elif player.gameState == blackjack_enums.GameState.Win:
                win = player.wager
                player.chips = player.chips + win
                print(f"{player.name} has won and been paid {win} chips at {player.evaluate()}")
            elif player.gameState == blackjack_enums.GameState.Push:
                print(f"{player.name} has pushed at {player.evaluate()}")
            elif player.gameState == blackjack_enums.GameState.Loss:
                loss = player.wager
                player.chips = player.chips - loss
                print(f"{player.name} has lost {loss} chips at {player.evaluate()}")

            if player.chips < self.min_bet:
                self.players.remove(player)
        
            time.sleep(1)
        print()

        for player in self.players:
            print(f"{player.name} has {player.chips} chips left")
            time.sleep(1)

        print()

    def reset_hands(self):
        for player in self.players:
            player.hand = []
        self.dealer.hand = []

    def play_full_round(self):
        self.deal_hand()
        self.play_round()
        self.evaluate_round()
        self.distribute_chips()
        self.reset_hands()

    def run_table(self):
        play = True
        while len(self.players) > 1 and play == True:
            if self.num_rounds != -1:
                self.num_rounds -= 1
                play = self.num_rounds > 0
            self.play_full_round()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--use_args', help='increase output verbosity', action='store_true')
    parser.add_argument('--min_bet', type=int, default=15)
    parser.add_argument('--players','--list', nargs='*', default=['Andrew'])
    parser.add_argument('--bot_num', type=int, default=2)
    parser.add_argument('--num_rounds', type=int, default=-1)
    args = parser.parse_args()

    setup = game_setup(args)
    game = blackjack_game(setup)
    game.run_table()
