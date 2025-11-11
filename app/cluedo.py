from calendar import c
from encodings.punycode import T
import random
import os

from colorama import Fore
try:
    from app.rules import Rules
    from app.exceptions import InvalidActionException, InvalidMoveException
    from app.board import Board
    from app.player import Player
    from app.config import Config
    from app.validation import validation
except ImportError:
    from rules import Rules
    from board import Board
    from player import Player
    from config import Config
    from validation import validation
    from exceptions import InvalidActionException, InvalidMoveException

class Cluedo:
    '''Main class to run the Cluedo game.'''
    def __init__(self, end = False):
        self.end = end
        self.rules = Rules()
        self.board = Board()
        self.config = Config()
        self.cards = []
        self.removed_cards = []
        self.initialize_cards()
        self.players = []
        self.current_turn_index = 0
        self.solution = self.generate_solution()
        for card in self.solution.values():
            self.remove_card_from_deck(card, self.cards)
            self.add_card_to_deck(card, self.removed_cards)
        self.create_players()
        while not self.end:
            player = self.players[self.current_turn_index]
            self.end = self.play_turn(player)
            self.current_turn_index = (self.current_turn_index + 1) % len(self.players)

    # Player 

    def create_players(self):
        '''Creates all player objects for the game.'''
        suspects = self.rules.get_suspects()
        player_symbols = self.rules.get_player_symbols()
        player_colors = self.config.get_player_colors()
        start_positions = self.config.get_player_start_positions()
        
        for suspect in suspects:
            player = Player(
                name=suspect,
                color=player_colors[suspect],
                symbol=player_symbols[suspect],
                start_position=start_positions[suspect]
            )
            self.players.append(player)
        
        print(f"Created {len(self.players)} players for the game.")
    
    def get_players(self):
        '''Returns the list of players.'''
        return self.players
    
    def get_player_by_name(self, name):
        '''Returns a player by their name.'''
        for player in self.players:
            if player.name == name:
                return player
        return None
    
    def display_players(self):
        '''Display information about all players.'''
        print("\n=== GAME PLAYERS ===")
        for player in self.players:
            player.display_info()
        print("===================\n")

    # Solution 

    def generate_solution(self):
        '''Generates a random solution by selecting one suspect, one weapon, and one room.'''
        suspects = self.rules.get_suspects()
        weapons = self.rules.get_weapons()
        rooms = self.rules.get_rooms()
        
        # Randomly select one from each category
        solution_suspect = random.choice(suspects)
        solution_weapon = random.choice(weapons)
        solution_room = random.choice(rooms)
        
        solution = {
            "suspect": solution_suspect,
            "weapon": solution_weapon,
            "room": solution_room
        }
        
        return solution

    def get_solution(self):
        '''Returns the current solution.'''
        return self.solution

    def display_solution(self, solution):
        '''Displays the solution in a formatted way.'''
        print("\n=== CLUEDO SOLUTION ===")
        print(f"Suspect: {solution['suspect']}")
        print(f"Weapon: {solution['weapon']}")
        print(f"Room: {solution['room']}")
        print("=======================\n")
        
    def get_solution_summary(self, solution) -> None:
        '''Returns a formatted string summary of the solution.'''
        return f"{solution['suspect']} with the {solution['weapon']} in the {solution['room']}"
    
    # Cards 

    def initialize_cards(self) -> None:
        '''Initializes the deck of cards for the game.'''
        self.cards = (
            self.rules.get_suspects() +
            self.rules.get_weapons() +
            self.rules.get_rooms()
        )
    
    def display_cards(self, cards: list) -> None:
        '''Prints all the cards in the deck.'''
        print("\n=== CLUEDO CARDS ===")
        for card in cards:
            print(f"- {card}")
        print("=====================\n")

    def remove_card_from_deck(self, card: str, cards: list) -> None:
        '''Removes a specific card from the deck.'''
        if card in cards:
            cards.remove(card)

    def add_card_to_deck(self, card: str, cards: list) -> None:
        '''Adds a specific card back to the deck.'''
        if card not in cards:
            cards.append(card)

    def get_cards(self) -> list:
        '''Returns the current deck of cards.'''
        return self.cards
    
    def get_removed_cards(self) -> list:
        '''Returns the list of removed cards (solution cards).'''
        return self.removed_cards

# Player Turns
    def play_turn(self, player: Player) -> bool:
        print(f"\nIt's {player.get_colored_name()}'s turn!")
        moves = self.roll_die(player)
        print(f"{player.get_colored_name()} has {moves} moves for their turn.")
        while True:
            try:
                choice = input("Enter an action (move/display/end) or leave blank to list of actions: ")
                if choice == "display":
                    self.board.display_board(self.players)
                elif choice == "move":
                    if moves <= 0:
                        print("Out of moves for this turn.")
                        continue
                    self.move(player)
                    moves -= 1
                    print(f"\nMoves remaining: {moves}")
                elif choice == "end":
                    break
                elif choice == "end game":
                    return True
                elif choice == "":
                    print("Available actions: move, display, end, end game")
            except InvalidMoveException as e:
                print(f"Invalid move: {e}")

        # Clear screen at end of turn
        self.clear_screen()
        return False


    def roll_die(self, player: Player) -> int:
        '''Play a turn for the given player.'''
        input("\n Press enter to roll dice...")
        value = player.roll_die()
        player.display_roll()
        return value

    def move(self, player: Player) -> None:
        try:
            move = input("Enter movement direction: ")
            
            # Let the player handle their own movement
            player.move(move)
            
            # Validate the new position
            validation.validate_position(player.get_player_position(), self.board)
            
            # If validation passes, update the board
            self.board.move_player(player)
            print(f"Moved {move} successfully!")
            
        except Exception as e:
            # If validation fails, reset player to previous position
            player.reset_to_previous_position()
            raise InvalidMoveException(str(e))

    def clear_screen(self):
        '''Clears the terminal screen.'''
        os.system('clear' if os.name == 'posix' else 'cls')

if __name__ == "__main__":
    # Test the game initialization with players
    game = Cluedo(True)
    
    # Display the board with legend
    game.board.display_legend()
    
    print("\n=== INITIAL BOARD (All players in hallways) ===")
    game.board.display_board(game.players)
    
    # Test moving players into rooms
    print("\n\n=== TEST 1: MOVING PLAYERS INTO ROOMS ===")
    print("Moving Miss Scarlet to Kitchen...")
    game.board.place_player_in_room(game.players[0], "Kitchen")
    
    print("Moving Colonel Mustard to Ballroom...")
    game.board.place_player_in_room(game.players[1], "Ballroom")
    
    print("Moving Mrs. White to Kitchen...")
    game.board.place_player_in_room(game.players[2], "Kitchen")
    
    print("\n=== BOARD AFTER MOVING PLAYERS TO ROOMS ===")
    print("(Notice old positions are now '.' again)")
    game.board.display_board(game.players)
    
    # Test moving players in hallways
    print("\n\n=== TEST 2: MOVING PLAYER IN HALLWAY ===")
    print(f"Mr. Green starting position: {game.players[3].current_position}")
    print("Moving Mr. Green from (14, 0) to (14, 1)...")
    game.board.move_player(game.players[3], (14, 1))
    print(f"Mr. Green new position: {game.players[3].current_position}")
    
    print("\n=== BOARD AFTER HALLWAY MOVE ===")
    print("(Notice (14, 0) is now '.' again)")
    game.board.display_board(game.players)
    
    # Test moving player from room to hallway
    print("\n\n=== TEST 3: MOVING PLAYER FROM ROOM TO HALLWAY ===")
    print("Moving Miss Scarlet from Kitchen to hallway position (5, 5)...")
    game.board.move_player_to_hallway(game.players[0], (5, 5))
    
    print("\n=== FINAL BOARD STATE ===")
    game.board.display_board(game.players)
    
    # Display all players
    print("\n")
    game.display_players()
    game.display_cards(game.get_cards())
    game.display_cards(game.get_removed_cards())

    print("\nGenerating random Cluedo solutions:")
    print("-" * 40)

    game.display_solution(game.get_solution())