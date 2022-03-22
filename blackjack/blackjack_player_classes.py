import card_classes
import blackjack_enums
from prompt_toolkit import prompt
import time

class TablePlayer:
    def __init__(self):
        self.hand = []
        self.busted = False
        self.stand = False

    def dealCard(self, deck):
        if len(deck.Cards) == 0:
            deck.Cards = card_classes.Deck(2).Cards
            deck.shuffle()
        card = deck.Cards.pop()
        self.hand.append(card)
        return card

    def evaluate(self):
        aceCount = 0
        handEvaluation = 0
        for card in self.hand:
            if card.name == "Ace":
                aceCount = aceCount + 1
            handEvaluation += card.value
        if handEvaluation > 21:
            while aceCount > 0:
                handEvaluation -= 10
                aceCount = aceCount - 1
        return handEvaluation

    def play_turn(self, game):
        while not self.busted and not self.stand:
            decision = self.turnDecision()
            if decision == blackjack_enums.Decision.Hit:
                self.hit(game)
            elif decision == blackjack_enums.Decision.Stand:
                self.keep_hand()

class Gambler(TablePlayer):
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.gameState = blackjack_enums.GameState.Undecided
        self.chips = 100
        self.wager = 0

    def turnInfo(self, game):
        print(f"It is {self.name}'s turn")
        print(f"(Reminder) Dealer is showing card {game.dealer.hand[0]}")
        print(f"(Reminder) {self.name} has cards:")
        print(f"{self.hand[0]}")
        print(f"{self.hand[1]}")
        self.busted = False
        self.stand = False

    def hit(self, game):
        card = self.dealCard(game.deck)
        print(f"{self.name} has drawn {card}")
        if self.evaluate() > 21:
            self.busted = True
            print(f"{self.name} has busted")
        time.sleep(1)

    def keep_hand(self):
        print(f"{self.name} stands")
        self.stand = True
        time.sleep(1)

class bot(Gambler):
    def __init__(self, name):
        super().__init__(name)

    def turnDecision(self):
        score = self.evaluate()
        if score < 17:
            return blackjack_enums.Decision.Hit
        else:
            return blackjack_enums.Decision.Stand

    def bet(self, game):
        self.wager = game.min_bet
        print(f"{self.name} bets {game.min_bet}")

class user(Gambler):
    def __init__(self, name):
        super().__init__(name)

    def turnDecision(self):
        print("\n Would you like to:")
        print("1) Hit")
        print("2) Stand")
        choice = prompt("")
        if choice == "1":
            return blackjack_enums.Decision.Hit
        elif choice == "2":
            return blackjack_enums.Decision.Stand
        else:
            print("Invalid choice try again.")
            return self.turnDecision()

    def bet(self, game):
        print(f"How much would {self.name} like to bet?")
        print(f"The minimum table bet is {game.min_bet}")
        bet = prompt("")
        try:
            bet_amt = int(bet)
            if bet_amt < game.min_bet and bet_amt > self.chips:
                raise Exception("Under table minimum")
            else:
                self.wager = bet_amt
        except:
            print("Invalid bet amount.  Try again")
            self.bet(game)

class Dealer(TablePlayer):
    def __init__(self):
        super().__init__()
        self.hand = []
        self.busted = False
        self.stand = False

    def turnDecision(self):
        score = self.evaluate()
        if score < 17:
            return blackjack_enums.Decision.Hit
        else:
            return blackjack_enums.Decision.Stand
    
    def turnInfo(self):
        print(f"It is the dealer's turn")
        print(f"(Reminder) The dealer is showing {self.hand[0]}")
        print(f"The dealer flips their hidden card to reveal {self.hand[1]}")
        self.busted = False
        self.stand = False


    def hit(self, game):
        card = self.dealCard(game.deck)
        print(f"The dealer has drawn {card}")
        if self.evaluate() > 21:
            self.busted = True
            print(f"The dealer has busted")
        time.sleep(1)

    def keep_hand(self):
        print(f"The dealer stands")
        self.stand = True
        time.sleep(1)
