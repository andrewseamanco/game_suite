import random

class Card:
    def __init__(self, suit, name, value):
        self.suit = suit
        self.name = name
        self.value = value
    
    def __str__(self):
        return f"{self.name} of {self.suit}"


class Deck:
    def __init__(self, deck_num):
        SUITS = ["Hearts", "Diamonds", "Clubs", "Spades"]
        CARDS = [("Ace", 11), ("Two", 2), ("Three", 3), ("Four", 4), ("Five", 5), ("Six", 6), ("Seven", 7), ("Eight", 8), ("Nine", 9), ("Ten", 10), ("Jack", 10), ("Queen", 10), ("King", 10)]

        deck = [Card(suit, card[0], card[1]) for suit in SUITS for card in CARDS]
        self.Cards = []
        for _ in range(0, deck_num):
            self.Cards = self.Cards + deck

    def __str__(self):
        deckString = ""
        for card in self.Cards:
            deckString += str(card) + "\n"
        return deckString
    
    def shuffle(self):
        deck_size = len(self.Cards)
        for index in range(deck_size):
            random_index = random.randint(0, (deck_size-1))
            temp = self.Cards[random_index]
            self.Cards[random_index] = self.Cards[index]
            self.Cards[index] = temp

