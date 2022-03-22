import json
import card_classes
from tqdm import tqdm
import pandas as pd
import json
from sklearn.linear_model import LinearRegression
import blackjack_enums
import blackjack_player_classes
import numpy as np

class Regression_Agent(blackjack_player_classes.bot):
    def __init__(self, name, sample_file, collect_samples):
        super().__init__(name)
        self.sample_file = sample_file
        if collect_samples:
            sampler = blackjack_sample(sample_file, 1000)
            sampler.generate_samples()
        self.train_agent()

    def train_agent(self):
        file = open(self.sample_file)
        data = json.load(file)
        df = pd.json_normalize(data,record_path=['data'])
        X = df[['aces', 'hand_value']]
        print(X)
        y = df['label']
        print(y)
        self.model = LinearRegression()
        self.model.fit(X, y)

    def ace_count(self):
        return sum([1 for card in self.hand if card.name == "Ace"])

    def turnDecision(self):
        X = pd.DataFrame(columns=['aces', 'hand_value'])
        X.loc[0] = [self.ace_count(), self.evaluate()]
        decision = self.model.predict(X)
        print(decision)
        if decision >= .5:
            return blackjack_enums.Decision.Hit
        else:
            return blackjack_enums.Decision.Stand


class blackjack_sample:
    def __init__(self, sample_file, num_samples):
        self.sample_file = sample_file
        self.num_samples = num_samples
        self.samples = []
        self.deck = card_classes.Deck(2)
        self.sample_collector = blackjack_player_classes.bot("")
        self.dealer = blackjack_player_classes.Dealer()

    def evaluatePotential(self, hand):
        aceCount = 0
        handEvaluation = 0
        for card in hand:
            if card.name == "Ace":
                aceCount = aceCount + 1
            handEvaluation += card.value
        if handEvaluation > 21:
            while aceCount > 0:
                handEvaluation -= 10
                aceCount = aceCount - 1
        return handEvaluation

    def aceNum(self, hand):
        return sum([1 for card in hand if card.name == "Ace"])

    def generate_samples(self):

        # Label 0 means to stand
        # Label 1 means to hit
        print("Collecting samples:")
        for run in tqdm(range(self.num_samples)):
            self.dealer.hand = []
            self.sample_collector.hand = []
            
            self.sample_collector.dealCard(self.deck)
            self.dealer.dealCard(self.deck)
            self.sample_collector.dealCard(self.deck)
            self.dealer.dealCard(self.deck)

            potentialHand = list(self.sample_collector.hand)

            # Protect against drawing a null card
            if len(self.deck.Cards) == 0:
                self.deck = card_classes.Deck(2)
            nextCard = self.deck.Cards[len(self.deck.Cards)-1]

            potentialHand.append(nextCard)

            while self.evaluatePotential(potentialHand) < 21:
                sample = {
                    "aces": self.aceNum(self.sample_collector.hand),
                    "hand_value": self.evaluatePotential(self.sample_collector.hand),
                    "label" : 1
                }

                self.collect_sample(sample)
                self.sample_collector.dealCard(self.deck)

                if len(self.deck.Cards) == 0:
                    self.deck = card_classes.Deck(2)

                potentialHand.append(self.deck.Cards[len(self.deck.Cards)-1])

            sample = {
                "aces": self.aceNum(self.sample_collector.hand),
                "hand_value": self.evaluatePotential(self.sample_collector.hand),
                "label" : 0
            }

            self.collect_sample(sample)

        while self.evaluatePotential(self.dealer.hand) < 21:
            self.dealer.dealCard(self.deck)


    def collect_sample(self, sample):
        with open(self.sample_file,'r+') as file:
            file_data = json.load(file)
            # Join new_data with file_data inside emp_details
            file_data["data"].append(sample)
            # Sets file's current position at offset.
            file.seek(0)
            # convert back to json.
            json.dump(file_data, file, indent = 4)     