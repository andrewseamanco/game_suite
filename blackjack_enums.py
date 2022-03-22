import enum

class GameState(enum.Enum):
    Win = 1
    Blackjack = 2
    Loss = 3
    Push = 4
    Undecided = 5

class Decision(enum.Enum):
    Hit = 1
    Stand = 2
    Undecided = 3
