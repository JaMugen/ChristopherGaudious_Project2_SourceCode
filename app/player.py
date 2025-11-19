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
        self.is_eliminated = False  # Whether player made wrong accusation
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
    
    def choose_card_to_show(self, matching_cards, to_player):
        '''Allows this player to choose which card to show when they have multiple matches.
        
        Args:
            matching_cards: List of cards that match the suggestion
            to_player: The player who will see the card
            
        Returns:
            str: The card chosen to show
        '''
        print(f"\n{self.get_colored_name()}, you have multiple matching cards: {', '.join(matching_cards)}")
        print(f"Choose which card to show to {to_player.get_colored_name()}:")
        
        for idx, card in enumerate(matching_cards, 1):
            print(f"{idx}. {card}")
        
        while True:
            try:
                choice = int(input("Enter card number: "))
                if 1 <= choice <= len(matching_cards):
                    return matching_cards[choice - 1]
                else:
                    print(f"Please enter a number between 1 and {len(matching_cards)}.")
            except ValueError:
                print("Please enter a valid number.")
    
    def make_suggestion_choices(self, available_suspects, available_weapons):
        '''Allows this player to choose suspect and weapon for a suggestion.
        
        Args:
            available_suspects: List of available suspect names
            available_weapons: List of available weapon names
            
        Returns:
            tuple: (suspect, weapon) chosen by the player
        '''
        print(f"\nAvailable suspects: {', '.join(available_suspects)}")
        suspect = input("Enter suspect name: ")
        if suspect not in available_suspects:
            raise InvalidActionException(f"{suspect} is not a valid suspect.")
        
        print(f"\nAvailable weapons: {', '.join(available_weapons)}")
        weapon = input("Enter weapon name: ")
        if weapon not in available_weapons:
            raise InvalidActionException(f"{weapon} is not a valid weapon.")
        
        return (suspect, weapon)
    
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
        self.previous_position = self.current_position
        self.current_position = None  # Position is now undefined in room context

    def exit_room(self, position: tuple):
        '''Set the player's current room to None (in hallway).'''
        self.current_room = None
        self.current_position = position
        self.previous_position = position

    def get_current_room(self):
        '''Return the name of the room the player is currently in, or None.'''
        return self.current_room
    
    def eliminate(self):
        '''Eliminates the player from taking turns.'''
        self.is_eliminated = True
        print(f"\n{self.get_colored_name()} has been eliminated from the game!")
        input("Press Enter to continue...")
    
    def is_eliminated_player(self):
        '''Returns whether the player is eliminated.'''
        return self.is_eliminated
    
    def get_colored_symbol(self):
        '''Returns the player's symbol with color formatting and reset.'''
        return f"{self.color}{self.symbol}{Style.RESET_ALL}"

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