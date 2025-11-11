import random

from colorama import Fore, Style
try:
    from app.config import Config
    from app.rules import Rules
    from app.exceptions import InvalidActionException, InvalidMoveException
    from app.validation import validation
except ImportError:
    from config import Config
    from rules import Rules
    from exceptions import InvalidActionException, InvalidMoveException
    from app.validation import validation


class Player:
    '''Represents a player in the Cluedo game.'''
    
    def __init__(self, name, color, symbol, start_position):
        '''
        Initialize a player with their character details.
        
        Args:
            name (str): The character name (e.g., "Miss Scarlet")
            color (str): Colorama color code for display
            symbol (str): Single character symbol for board display
            start_position (tuple): (row, col) starting position on board
        '''

        self.name = name
        self.color = color
        self.symbol = symbol
        self.start_position = start_position
        self.current_position = start_position
        self.previous_position = None
        self.current_room = None  # Name of room player is in, None if in hallway
        self.cards = []  # Cards held by this player
        self.is_active = True  # Whether player is still in game
        self.roll = 0  # Current dice roll (die1, die2)
        
    def __str__(self):
        '''String representation of the player.'''
        return f"{self.name} ({self.symbol})"
    
    def __repr__(self):
        '''Detailed representation for debugging.'''
        return f"Player(name='{self.name}', position={self.current_position}, cards={len(self.cards)})"
    
    def add_card(self, card):
        '''Add a card to the player's hand.'''
        if card not in self.cards:
            self.cards.append(card)
    
    def has_card(self, card):
        '''Check if player has a specific card.'''
        return card in self.cards
    
    def get_cards(self):
        '''Return list of cards held by player.'''
        return self.cards.copy()
    
    def get_colored_name(self):
        '''Returns the player name with color formatting and reset.'''
        return f"{self.color}{self.name}{Style.RESET_ALL}"
    
    def display_info(self):
        '''Display player information.'''
        print(f"\n{self.get_colored_name()}")
        print(f"  Symbol: {self.symbol}")
        print(f"  Position: {self.current_position}")
        print(f"  Cards: {len(self.cards)}")
        if self.cards:
            print(f"  Hand: {', '.join(self.cards)}")

    def roll_die(self):
        '''Set the player's current dice roll.'''
        die = random.randint(1, 6)
        self.roll = die
        return die

    def get_roll(self):
        '''Return the player's current dice roll.'''
        return self.roll
    
    def display_roll(self):
        '''Display the player's current dice roll.'''
        print(f"{self.get_colored_name()} rolled a {self.roll}")

    
    def move(self, direction):
        '''Move the player in the specified direction.'''
        row, col = self.current_position
        if direction.lower() == 'up':
            self.move_to((row - 1, col))
        elif direction.lower() == 'down':
            self.move_to((row + 1, col))
        elif direction.lower() == 'left':
            self.move_to((row, col - 1))
        elif direction.lower() == 'right':
            self.move_to((row, col + 1))
        else:
            raise InvalidMoveException("Invalid move direction. Use 'up', 'down', 'left', or 'right'.")
    
    def get_player_position(self):
        '''Return the player's current position.'''
        return self.current_position

    def move_to(self, position):
        '''Move player to a new position.'''
        self.previous_position = self.current_position
        self.current_position = position
    
    def reset_to_start_position(self):
        '''Reset player to their starting position.'''
        self.current_position = self.start_position
    
    def reset_to_previous_position(self):
        '''Reset player to their previous position (undo last move).'''
        if self.previous_position is not None:
            self.current_position = self.previous_position
        

if __name__ == "__main__":
    # Test player creation and movement
    player = Player(
        name="Miss Scarlet",
        color=Fore.RED,  # Red
        symbol="S",
        start_position=(0, 9)
    )
    
    player.display_info()
    player.move('down')
    print(f"After moving down: {player.current_position}")
    player.move('right')
    print(f"After moving right: {player.current_position}")
    try:
        player.move('invalid_direction')
    except InvalidMoveException as e:
        print(e)