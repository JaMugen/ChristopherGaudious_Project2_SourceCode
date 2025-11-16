import random
import os

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
                choice = input("Enter an action or leave blank to see the list of actions: ")
                match choice:
                    case "display":
                        self.board.display_board(self.players)
                    case "move":
                        if moves <= 0:
                            print("Out of moves for this turn.")
                            continue
                        self.move(player)
                        moves -= 1
                        print(f"\nMoves remaining: {moves}")
                    case "enter":
                        self.enter_room(player)
                    case "exit":
                        self.exit_room(player)
                    case "end":
                        break
                    case "end game":
                        return True
                    case "clear":
                        self.clear_screen()
                    case "":
                        self.print_available_actions(player)
                    case _: # default because python
                        raise InvalidActionException("Invalid action. Please choose a valid action.")
            except InvalidMoveException as e:
                print(f"Invalid move: {e}")
            except InvalidActionException as e:
                print(f"Invalid action: {e}")

        # Clear previous moves at end of turn
        self.previous_moves = []
        
        # Clear screen at end of turn
        self.clear_screen()
        return False

    def get_previous_moves(self) -> list:
        '''Returns the list of previous moves in the current turn.'''
        return self.previous_moves
    
    def get_board(self) -> Board:
        '''Returns the game board.'''
        return self.board

    def roll_die(self, player: Player) -> int:
        '''Play a turn for the given player.'''
        devop = input("\n Press enter to roll dice...")
        if devop == "uula": # Code for testing movement
            value = 100
            return value
        value = player.roll_die()
        player.display_roll()
        return value

    def move(self, player: Player) -> None:
        move = input("Enter movement direction: ")
        
        try:
            # Let the player handle their own movement
            player.move(move)
            
            # Validate the new position
            validation.validate_position(player.get_player_position(), self.get_board(), self.get_previous_moves())
            
            # If validation passes, update the board
            self.board.move_player(player)
            
            # Track this position in previous_moves
            self.previous_moves.append(player.get_previous_position())
            print(f"Moved {move} successfully!")
            
        except InvalidMoveException as e:
            # Reset player to previous position for invalid moves
            player.reset_to_previous_position()
            raise InvalidMoveException(str(e))
        except InvalidActionException as e:
            # Just print error for invalid actions
            print(f"Error: {e}")

    def enter_room(self, player: Player) -> None:
        '''Handles player entering a room.'''
        # Display the board first
        self.board.display_board(self.players)
        
        # Display available rooms with their letters from rules
        room_list = []
        for room_name in self.rules.get_rooms():
            room_symbol = self.board.get_room_symbol(room_name)
            room_list.append(f"{room_name} ({room_symbol})")
        print(f"\nRooms available to enter: {', '.join(room_list)}")
        
        room_name = input("Enter the room name to enter: ")
        if room_name not in self.rules.get_rooms():
            raise InvalidActionException(f"{room_name} is not a valid room.")
        try:
            player.enter_room(room_name)
            validation.validate_enter_room(player, room_name, self.board)
            self.board.place_player_in_room(player, room_name)
            print(f"{player.get_colored_name()} has entered the {room_name}.")
        except Exception as e:
            player.exit_room()
            raise InvalidActionException(str(e))

    def exit_room(self, player: Player) -> None:
        '''Handles player exiting a room.'''
        room_name = player.current_room
        if not room_name:
            raise InvalidActionException(f"{player.get_colored_name()} is not currently in a room.")
        
        room_layouts = self.board.get_room_layouts()
        room_layout = room_layouts.get(room_name)
        
        # Print the room layout with numbered doors
        print(f"\n{room_name} Layout:")
        door_locations = room_layout['door_locations']
        layout = room_layout['layout']
        
        # Create a copy of the layout with numbered doors
        for row_idx, row in enumerate(layout):
            row_str = ""
            for col_idx, cell in enumerate(row):
                # Check if this position is a door
                door_number = None
                for idx, door_pos in enumerate(door_locations):
                    if (row_idx, col_idx) == door_pos:
                        door_number = idx + 1
                        break
                
                if door_number:
                    row_str += str(door_number) + " "
                else:
                    row_str += cell + " "
            print(row_str)
        
        # Ask player to select a door
        print(f"\nAvailable doors: {', '.join([str(i+1) for i in range(len(door_locations))])}")
        door_choice = input("Enter door number to exit through: ")
        
        try:
            door_index = int(door_choice) - 1
            if door_index < 0 or door_index >= len(door_locations):
                raise InvalidActionException(f"Invalid door number. Choose between 1 and {len(door_locations)}.")
            
            # Get the exit position using the exit_offsets
            exit_offsets = room_layout['exit_offsets']
            exit_offset = exit_offsets[door_index]
            
            # Calculate the board position where player exits to
            exit_row = room_layout['position'][0] + exit_offset[0]
            exit_col = room_layout['position'][1] + exit_offset[1]
            exit_position = (exit_row, exit_col)
            
            # Exit the room first (updates player's current_position and clears current_room)
            player.exit_room()
            player.current_position = exit_position
            
            # Validate the exit position using validation class
            try:
                validation.validate_position(exit_position, self.board, [])
            except Exception as e:
                player.enter_room(room_name)
                raise InvalidActionException(f"Cannot exit through door {door_choice}: {e}")
            
            self.board.move_player_to_hallway(player, exit_position)
            print(f"{player.get_colored_name()} has exited the {room_name} through door {door_choice}.")
            
        except ValueError:
            raise InvalidActionException("Please enter a valid number.")

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