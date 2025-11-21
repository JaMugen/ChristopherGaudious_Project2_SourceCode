import random
import os

try:
    from app.rules import Rules
    from app.exceptions import InvalidActionException, InvalidMoveException
    from app.board import Board
    from app.player import Player, ActivePlayer, InactivePlayer, EliminatedPlayer
    from app.config import Config
    from app.cluedo_actions import (
        PlayerActionFactory, DisplayBoardAction, MoveAction, EnterRoomAction,
        ExitRoomAction, MakeSuggestionAction, ViewLogAction, EndTurnAction,
        EndGameAction, ClearScreenAction, DisplayPlayersCardsAction,
        DisplaySolutionAction, ShowAvailableActionsAction, AccuseAction,
        SecretPassageAction, ShowCardsAction
    )
except ImportError:
    from rules import Rules
    from board import Board
    from player import Player, ActivePlayer, InactivePlayer, EliminatedPlayer
    from config import Config
    from exceptions import InvalidActionException, InvalidMoveException
    from cluedo_actions import (
        PlayerActionFactory, DisplayBoardAction, MoveAction, EnterRoomAction,
        ExitRoomAction, MakeSuggestionAction, ViewLogAction, EndTurnAction,
        EndGameAction, ClearScreenAction, DisplayPlayersCardsAction,
        DisplaySolutionAction, ShowAvailableActionsAction, AccuseAction,
        SecretPassageAction, ShowCardsAction
    )

class Cluedo:
    '''Main class to run the Cluedo game.'''

    # Action constants
    ACTION_DISPLAY_BOARD = "display"
    ACTION_MOVE = "move"
    ACTION_ENTER_ROOM = "enter"
    ACTION_EXIT_ROOM = "exit"
    ACTION_MAKE_SUGGESTION = "suggest"
    ACTION_VIEW_LOG = "log"
    ACTION_END_TURN = "end"
    ACTION_END_GAME = "end game"
    ACTION_CLEAR_SCREEN = "clear"
    ACTION_ACCUSE = "accuse"
    ACTION_SECRET_PASSAGE = "secret"
    ACTION_SHOW_CARDS = "show"
    
    # Actions that automatically end the turn
    ACTIONS_THAT_END_TURN = ["accuse", "suggest", "enter", "secret", "end"]

    # Dev input
    DEV_INPUT_TEST_MOVEMENT = "uula"
    DEV_INPUT_DISPLAY_PLAYERS_CARDS = "uulc"
    DEV_INPUT_DISPLAY_SOLUTIONS_CARDS = "uuls"

    

    # Initialization
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
        self.previous_moves = []  # Track positions during current player's turn
        self.suggestion_log = []  # Track all suggestions and refutations
        for card in self.solution.values():
            self.remove_card_from_deck(card, self.cards)
            self.add_card_to_deck(card, self.removed_cards)
        self.create_players()
        self.distribute_cards()
        self.setup_action_factory()
    
    def setup_action_factory(self):
        '''Sets up the player action factory with all available actions.'''
        self.action_factory = PlayerActionFactory()
        
        # Register all actions
        self.action_factory.register_action(self.ACTION_DISPLAY_BOARD, DisplayBoardAction)
        self.action_factory.register_action(self.ACTION_MOVE, MoveAction)
        self.action_factory.register_action(self.ACTION_ENTER_ROOM, EnterRoomAction)
        self.action_factory.register_action(self.ACTION_EXIT_ROOM, ExitRoomAction)
        self.action_factory.register_action(self.ACTION_MAKE_SUGGESTION, MakeSuggestionAction)
        self.action_factory.register_action(self.ACTION_VIEW_LOG, ViewLogAction)
        self.action_factory.register_action(self.ACTION_END_TURN, EndTurnAction)
        self.action_factory.register_action(self.ACTION_END_GAME, EndGameAction)
        self.action_factory.register_action(self.ACTION_CLEAR_SCREEN, ClearScreenAction)
        self.action_factory.register_action(self.DEV_INPUT_DISPLAY_PLAYERS_CARDS, DisplayPlayersCardsAction)
        self.action_factory.register_action(self.DEV_INPUT_DISPLAY_SOLUTIONS_CARDS, DisplaySolutionAction)
        self.action_factory.register_action("", ShowAvailableActionsAction)
        self.action_factory.register_action(self.ACTION_ACCUSE, AccuseAction)
        self.action_factory.register_action(self.ACTION_SECRET_PASSAGE, SecretPassageAction)
        self.action_factory.register_action(self.ACTION_SHOW_CARDS, ShowCardsAction)

    def distribute_cards(self):
        '''Distributes the remaining cards equally among all players.'''
        random.shuffle(self.cards)
        num_players = len(self.players)
        
        card_index = 0
        for card in self.cards:
            player = self.players[card_index % num_players]
            player.add_card(card)
            card_index += 1
        
        print(f"\nCards have been distributed to the {num_players} players.")

    def start(self):
        '''Starts the main game loop.'''
        while not self.get_end():
            player = self.get_current_player()
            
            # Skip players who cannot take turns (inactive or eliminated)
            if not player.can_take_turn():
                if player.is_eliminated_player():
                    print(f"\n{player.get_colored_name()} is eliminated and skips their turn.")
                else:
                    print(f"\n{player.get_colored_name()} is inactive and skips their turn.")
                self.next_turn()
                continue
            
            self.end = self.play_turn(player)
            self.next_turn()
    def get_end(self):
        '''Returns whether the game has ended.'''
        return self.end
    
    def get_current_player(self):
        '''Returns the current player based on turn index.'''
        return self.players[self.current_turn_index]
    
    def next_turn(self):
        '''Advances to the next player's turn.'''
        self.current_turn_index = (self.current_turn_index + 1) % len(self.players)

    # Player 

    def create_players(self):
        '''Creates all player objects for the game.'''
        suspects = self.rules.get_suspects()
        player_symbols = self.rules.get_player_symbols()
        player_colors = self.config.get_player_colors()
        start_positions = self.config.get_player_start_positions()
        
        print("\n=== PLAYER SETUP ===")
        for suspect in suspects:
            # Prompt whether each player is active
            while True:
                response = input(f"Is {suspect} active? (y/n): ").strip().lower()
                if response == 'y':
                    player = ActivePlayer(
                        name=suspect,
                        color=player_colors[suspect],
                        symbol=player_symbols[suspect],
                        start_position=start_positions[suspect]
                    )
                    self.players.append(player)
                    print(f"{suspect} is set as ACTIVE.")
                    break
                elif response == 'n':
                    player = InactivePlayer(
                        name=suspect,
                        color=player_colors[suspect],
                        symbol=player_symbols[suspect],
                        start_position=start_positions[suspect]
                    )
                    self.players.append(player)
                    print(f"{suspect} is set as INACTIVE (can refute but won't take turns).")
                    break
                else:
                    print("Please enter 'y' or 'n'.")
        
        print(f"\nCreated {len(self.players)} players for the game.")
        print("=" * 40)
    
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
    
    def replace_player_with_eliminated(self, player):
        '''Replace a player with an EliminatedPlayer instance.
        
        Args:
            player: The player to replace
            
        Returns:
            The new EliminatedPlayer instance
        '''
        # Find player index
        player_index = self.players.index(player)
        
        # Create eliminated player from existing player
        eliminated = EliminatedPlayer.from_player(player)
        
        # Replace in players list
        self.players[player_index] = eliminated
        
        return eliminated

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
    
    def check_accusation(self, accusation):
        '''Checks if an accusation matches the solution.
        
        Args:
            accusation: Dict with 'suspect', 'weapon', 'room' keys
            
        Returns:
            bool: True if accusation matches solution exactly
        '''
        return (accusation['suspect'] == self.solution['suspect'] and
                accusation['weapon'] == self.solution['weapon'] and
                accusation['room'] == self.solution['room'])

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
        
        # Clear previous moves list at start of turn
        self.previous_moves = []
        
        moves = self.roll_die(player)
        print(f"{player.get_colored_name()} has {moves} moves for their turn.")
        while True:
            try:
                choice = input("Enter an action or leave blank to see the list of actions: ")
                
                # Special handling for move action (needs move count check)
                if choice == self.ACTION_MOVE:
                    if moves <= 0:
                        print("Out of moves for this turn.")
                        continue
                
                # Special handling for end turn action (needs to break loop)
                
                # Use factory to create and execute action
                try:
                    action = self.action_factory.create_action(choice)
                    end_game, moves_used = action.execute(self, player)
                    
                    if end_game:
                        return True
                    
                    # Check if this action automatically ends the turn
                    if choice in self.ACTIONS_THAT_END_TURN:
                        break
                    
                    moves -= moves_used
                    if moves_used > 0:
                        print(f"\nMoves remaining: {moves}")
                        
                except InvalidActionException as e:
                    if "Unknown action" in str(e):
                        raise InvalidActionException("Invalid action. Please choose a valid action.")
                    raise
                    
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
        if devop == self.DEV_INPUT_TEST_MOVEMENT: # Code for testing movement
            value = 100
            return value
        value = player.roll_die()
        player.display_roll()
        return value

    def clear_screen(self):
        '''Clears the terminal screen.'''
        os.system('clear' if os.name == 'posix' else 'cls')

    def refute_suggestion(self, suggesting_player: Player, suggestion: dict) -> tuple:
        '''Handles the refutation process for a suggestion.
        
        Goes clockwise from the suggesting player. Stops after the first player
        shows a matching card.
        
        Args:
            suggesting_player: The player who made the suggestion
            suggestion: Dict with 'suspect', 'weapon', 'room' keys
            
        Returns:
            tuple: (refuting_player, shown_card) or (None, None) if no one can refute
        '''
        # Get suggesting player's index
        suggester_index = self.players.index(suggesting_player)
        
        refuting_player = None
        shown_card = None
        
        # Check players clockwise starting from the next player
        # Include all players who can refute (active, inactive, and eliminated)
        for i in range(1, len(self.players)):
            player_index = (suggester_index + i) % len(self.players)
            player = self.players[player_index]
            
            # Skip players who cannot refute
            if not player.can_refute():
                continue
            
            input(f"\nPress enter to have {player.get_colored_name()} check for refutation...")
            # Check which cards this player has that match the suggestion
            matching_cards = []
            for card in [suggestion['suspect'], suggestion['weapon'], suggestion['room']]:
                if player.has_card(card):
                    matching_cards.append(card)
            
            # If player has matching cards, they must show one
            if matching_cards:
                print(f"\n{player.get_colored_name()} has a card to show.")
                
                if len(matching_cards) == 1:
                    # Only one card to show
                    card_to_show = matching_cards[0]
                else:
                    # Player chooses which card to show
                    card_to_show = player.choose_card_to_show(matching_cards, suggesting_player)
                
                # Only the suggesting player sees the actual card
                self.clear_screen()
                input(f"\nPress enter to reveal the card to {suggesting_player.get_colored_name()}...")
                print(f"\n{suggesting_player.get_colored_name()} privately sees: {card_to_show}")
                input("Press enter to continue...")
                input("Press Enter to continue...")
                self.clear_screen()
                refuting_player = player
                shown_card = card_to_show
                # Stop after first refutation
                break
        
        # Return refutation result
        if refuting_player:
            return (refuting_player, shown_card)
        return (None, None)
    
    def log_suggestion(self, suggesting_player: Player, suggestion: dict, refuting_player: Player, shown_card: str) -> None:
        '''Logs a suggestion and its refutation to the game log.
        
        Args:
            suggesting_player: Player who made the suggestion
            suggestion: Dict with 'suspect', 'weapon', 'room' keys
            refuting_player: Player who refuted (or None)
            shown_card: Card that was shown (or None)
        '''
        refuting_player_name = None
        if refuting_player:
            refuting_player_name = refuting_player.get_colored_name()
        
        log_entry = {
            "turn": len(self.suggestion_log) + 1,
            "suggesting_player": suggesting_player.name,
            "suggestion": suggestion.copy(),
            "refuting_player": refuting_player_name,
            "shown_card": shown_card
        }
        self.suggestion_log.append(log_entry)
    
    def display_suggestion_log(self) -> None:
        '''Displays the complete suggestion log.'''
        if not self.suggestion_log:
            print("\nNo suggestions have been made yet.")
            return
        
        print("\n" + "=" * 80)
        print("SUGGESTION LOG".center(80))
        print("=" * 80)
        
        for entry in self.suggestion_log:
            print(f"\nTurn {entry['turn']}: {entry['suggesting_player']}")
            print(f"  Suggested: {entry['suggestion']['suspect']} with the {entry['suggestion']['weapon']} in the {entry['suggestion']['room']}")
            
            if entry['refuting_player']:
                print(f"  Refuted by: {entry['refuting_player']}")
                # Note: shown_card is visible to all players in the log
                print(f"    Card shown: {entry['shown_card']}")
            else:
                print("  No one could refute!")
        
        print("\n" + "=" * 80)


    def print_available_actions(self) -> None:
        '''Prints the available actions for the player using descriptions from action classes.'''
        print("Available actions:")
        for action_name in self.action_factory.get_registered_actions():
            if action_name:  # Skip empty string action
                try:
                    action = self.action_factory.create_action(action_name)
                    description = action.get_description()
                    print(f"- {action_name}: {description}")
                except Exception:
                    print(f"- {action_name}: (No description available)")

    def display_players_cards(self) -> None:
        '''Displays all players and their cards (for dev/testing purposes).'''
        print("\n=== PLAYERS AND THEIR CARDS ===")
        for player in self.players:
            print(f"\n{player.get_colored_name()}'s cards:")
            for card in player.get_cards():
                print(f"- {card}")
        print("================================\n")

