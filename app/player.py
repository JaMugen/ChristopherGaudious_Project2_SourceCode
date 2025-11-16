import random

from colorama import Fore, Style
try:
    from app.exceptions import InvalidMoveException, InvalidActionException
except ImportError:
    from exceptions import InvalidMoveException, InvalidActionException


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
        match direction.lower():
            case 'up':
                self.move_to((row - 1, col))
            case 'down':
                self.move_to((row + 1, col))
            case 'left':
                self.move_to((row, col - 1))
            case 'right':
                self.move_to((row, col + 1))
            case _:
                raise InvalidActionException("Invalid move direction. Use 'up', 'down', 'left', or 'right'.")
    
    def get_player_position(self):
        '''Return the player's current position.'''
        return self.current_position

    def get_previous_position(self):
        '''Return the player's previous position.'''
        return self.previous_position

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

    def enter_room(self, room_name):
        '''Set the player's current room.'''
        self.current_room = room_name

    def exit_room(self):
        '''Set the player's current room to None (in hallway).'''
        self.current_room = None

    def get_current_room(self):
        '''Return the name of the room the player is currently in, or None.'''
        return self.current_room
        

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