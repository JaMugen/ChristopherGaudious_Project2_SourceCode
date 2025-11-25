'''Factory pattern for cluedo actions (renamed from player_actions).'''

try:
    from app.exceptions import InvalidActionException, InvalidMoveException
    from app.validation import validation
except ImportError:
    from exceptions import InvalidActionException, InvalidMoveException
    from validation import validation


class PlayerAction:
    '''Base class for player actions.'''
    
    def execute(self, game, player):
        '''Execute the action.
        
        Args:
            game: The Cluedo game instance
            player: The player performing the action
            
        Returns:
            Tuple of (should_end_game: bool, moves_used: int)
        '''
        raise NotImplementedError("Subclasses must implement execute()")
    
    def get_description(self):
        '''Returns a description of what this action does.
        
        Returns:
            str: Description of the action
        '''
        return "Perform an action"

    def suggestion(self, game, player):
        """Run the suggestion action with retry on recoverable errors.

        The `MakeSuggestionAction` itself handles the optional accusation
        prompt after a successful suggestion, so this helper only needs to
        call it and return the result. If the suggestion raises
        `InvalidActionException` it will prompt the player to retry.

        Returns:
            Tuple of (should_end_game: bool, moves_used: int)
        """
        while True:
            try:
                suggestion_action = MakeSuggestionAction()
                end_game, moves_used = suggestion_action.execute(game, player)
                return (end_game, moves_used)
            except InvalidActionException as e:
                print(f"Suggestion error: {e}")
                print("Please try your suggestion again.")
                continue
            except Exception as e:
                raise InvalidActionException(str(e))


class DisplayBoardAction(PlayerAction):
    '''Action to display the game board.'''
    
    def execute(self, game, player):
        game.board.display_board(game.get_players())
        return (False, 0)
    
    def get_description(self):
        return "Display the game board with all player positions"


class MoveAction(PlayerAction):
    '''Action to move a player.'''
    
    def execute(self, game, player):
        move = input("Enter movement direction: ")
        
        try:
            # Let the player handle their own movement
            player.move(move)
            
            # Validate the new position
            validation.validate_position(player.get_player_position(), game.get_board(), game.get_previous_moves())
            
            # If validation passes, update the board
            game.board.move_player(player)
            
            # Track this position in previous_moves
            game.previous_moves.append(player.get_previous_position())
            print(f"Moved {move} successfully!")
            
            return (False, 1)
            
        except InvalidMoveException as e:
            # Reset player to previous position for invalid moves
            player.reset_to_previous_position()
            raise InvalidMoveException(str(e))
        except InvalidActionException as e:
            # Just print error for invalid actions
            print(f"Error: {e}")
            return (False, 0)
    
    def get_description(self):
        return "Move your player in a direction (up, down, left, right)"



class EnterRoomAction(PlayerAction):
    '''Action to enter a room.'''
    
    def execute(self, game, player):
        # Display the board first
        game.board.display_board(game.get_players())
        
        # Display available rooms with their letters from rules
        room_list = []
        for room_name in game.rules.get_rooms():
            room_symbol = game.board.get_room_symbol(room_name)
            room_list.append(f"{room_name} ({room_symbol})")
        print(f"\nRooms available to enter: {', '.join(room_list)}")
        
        room_name = input("Enter the room name to enter: ")
        if room_name not in game.rules.get_rooms():
            raise InvalidActionException(f"{room_name} is not a valid room.")
        try:
            player.enter_room(room_name)
            validation.validate_enter_room(player, room_name, game.board)
            game.board.place_player_in_room(player, room_name)
            print(f"{player.get_colored_name()} has entered the {room_name}.")
            
            # Run the suggestion + optional-accuse flow using the shared helper
            end_game, moves_used = self.suggestion(game, player)
            return (end_game, moves_used)
        except Exception as e:
            player.exit_room(player.get_previous_position())
            raise InvalidActionException(str(e))
    
    def get_description(self):
        return "Enter a room and automatically make a suggestion"



class ExitRoomAction(PlayerAction):
    '''Action to exit a room.'''
    
    def execute(self, game, player):
        room_name = player.current_room
        if not room_name:
            raise InvalidActionException(f"{player.get_colored_name()} is not currently in a room.")
        
        # Display the room layout with numbered doors
        game.board.display_room_layout(room_name)
        
        door_locations = game.board.get_door_locations(room_name)
        room_layout = game.board.get_room_layout(room_name)
        
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
            player.exit_room(exit_position)
            
            # Validate the exit position using validation class
            try:
                validation.validate_position(exit_position, game.board, [])
            except Exception as e:
                player.enter_room(room_name)
                raise InvalidActionException(f"Cannot exit through door {door_choice}: {e}")
            
            game.board.move_player_to_hallway(player, exit_position)
            print(f"{player.get_colored_name()} has exited the {room_name} through door {door_choice}.")
            return (False, 0)
            
        except ValueError:
            raise InvalidActionException("Please enter a valid number.")
    
    def get_description(self):
        return "Exit the current room through a numbered door"



class MakeSuggestionAction(PlayerAction):
    '''Action to make a suggestion.'''
    
    def execute(self, game, player):
        # Check if player is in a room
        if player.current_room is None:
            raise InvalidActionException("You must be in a room to make a suggestion.")
        
        print(f"\n{player.get_colored_name()} is making a suggestion in the {player.current_room}.")
        
        # Get suggestion details from the player
        suspect, weapon = player.make_suggestion_choices(game.rules.get_suspects(), game.rules.get_weapons())
        
        # Room is automatically the current room
        room = player.current_room
        
        suggestion = {
            "suspect": suspect,
            "weapon": weapon,
            "room": room
        }
        
        print(f"\n{player.get_colored_name()} suggests: {suspect} with the {weapon} in the {room}")
        
        # Move the suggested suspect player to the room
        suspected_player = game.get_player_by_name(suspect)
        if suspected_player:
            suspected_player.enter_room(room)
            game.board.place_player_in_room(suspected_player, room)
            print(f"\n{suspected_player.get_colored_name()} has been moved to {room}.")

        # Move the suggested weapon to the room
        game.board.place_weapon_in_room(weapon, room)
        
        # Start refutation process clockwise from the suggesting player
        refuting_players, shown_card = game.refute_suggestion(player, suggestion)
        
        # Notify AI observers about the suggestion and refutation
        game.notify_ai_observers(player, suggestion, refuting_players, shown_card)
        
        # Log the suggestion and refutation
        game.log_suggestion(player, suggestion, refuting_players[-1] , shown_card)
        
        if refuting_players:
            print(f"\n{refuting_players[-1].get_colored_name()} showed a card to {player.get_colored_name()}.")
        else:
            print("\nNo one could refute the suggestion!")
        
        # After the suggestion, allow the suggesting player to optionally make an accusation
        while True:
            try:
                resp = input("\nDo you want to make an accusation (y/n): ")
                if resp.lower() == 'y':
                    accusation_action = AccuseAction()
                    end_game_accuse, moves_used_accuse = accusation_action.execute(game, player)
                    return (end_game_accuse, moves_used_accuse)
                elif resp.lower() == 'n':
                    return (False, 0)
                else:
                    print("Please enter 'y' or 'n'.")
            except Exception as e:
                print(f"Error: {e}")
                continue
    
    def get_description(self):
        return "Make a suggestion in your current room (must be in a room)"

class AccuseAction(PlayerAction):
    '''Action to make an accusation.'''
    
    def execute(self, game, player):
        print(f"\n{player.get_colored_name()} is making an accusation.")
        
        # Get accusation details from the player
        suspect, weapon = player.make_suggestion_choices(game.rules.get_suspects(), game.rules.get_weapons())
        
        # Room must be chosen by the player
        print(f"\nAvailable rooms: {', '.join(game.rules.get_rooms())}")
        room = input("Enter room name: ")
        if room not in game.rules.get_rooms():
            raise InvalidActionException(f"{room} is not a valid room.")
        
        accusation = {
            "suspect": suspect,
            "weapon": weapon,
            "room": room
        }
        
        print(f"\n{player.get_colored_name()} accuses: {suspect} with the {weapon} in the {room}")
        
        # Check if the accusation matches the solution
        if game.check_accusation(accusation):
            print(f"\n{'=' * 80}")
            print("CORRECT ACCUSATION!".center(80))
            print(f"{'=' * 80}")
            print(f"\n{player.get_colored_name()} has won the game!")
            print("\nThe solution was:")
            game.display_solution(game.get_solution())
            return (True, 0)  # End game
        else:
            print(f"\n{'=' * 80}")
            print("INCORRECT ACCUSATION!".center(80))
            print(f"{'=' * 80}")
            print(f"\n{player.get_colored_name()} has been eliminated from the game!")
            input("Press Enter to continue...")
            
            # Replace player with EliminatedPlayer instance
            eliminated_player = game.replace_player_with_eliminated(player)
            
            # Move eliminated player to Ballroom
            eliminated_player.enter_room("Ballroom")
            game.board.place_player_in_room(eliminated_player, "Ballroom")
            return (False, 0)  # Don't end game, but player is eliminated
    
    def get_description(self):
        return "Make an accusation to win the game (eliminates you if wrong)"

class ViewLogAction(PlayerAction):
    '''Action to view the suggestion log.'''
    
    def execute(self, game, player):
        game.display_suggestion_log()
        return (False, 0)
    
    def get_description(self):
        return "View the log of all suggestions and refutations"



class EndTurnAction(PlayerAction):
    '''Action to end the current turn.'''
    
    def execute(self, game, player):
        return (False, 0)  # Signal to break from turn loop
    
    def get_description(self):
        return "End your current turn"



class EndGameAction(PlayerAction):
    '''Action to end the game.'''
    
    def execute(self, game, player):
        return (True, 0)
    
    def get_description(self):
        return "End the game immediately"



class ClearScreenAction(PlayerAction):
    '''Action to clear the screen.'''
    
    def execute(self, game, player):
        game.clear_screen()
        return (False, 0)
    
    def get_description(self):
        return "Clear the terminal screen"



class DisplayPlayersCardsAction(PlayerAction):
    '''Action to display all players cards (dev/testing).'''
    
    def execute(self, game, player):
        game.display_players_cards()
        return (False, 0)
    
    def get_description(self):
        return "[DEV] Display all players' cards"



class DisplaySolutionAction(PlayerAction):
    '''Action to display the solution (dev/testing).'''
    
    def execute(self, game, player):
        game.display_solution(game.get_solution())
        return (False, 0)
    
    def get_description(self):
        return "[DEV] Display the solution to the mystery"


class DisplayAIKnowledgeAction(PlayerAction):
    '''Action to display AI players' knowledge (dev/testing).'''
    
    def execute(self, game, player):
        game.display_ai_knowledge()
        return (False, 0)
    
    def get_description(self):
        return "[DEV] Display AI players' knowledge about the game"
    
class ShowAvailableActionsAction(PlayerAction):
    '''Action to show available actions.'''
    
    def execute(self, game, player):
        game.print_available_actions()
        return (False, 0)
    
    def get_description(self):
        return "Show the list of available actions"
    
class ShowCardsAction(PlayerAction):
    '''Action to show the player's own cards.'''
    
    def execute(self, game, player):
        player.show_cards()
        return (False, 0)
    
    def get_description(self):
        return "Show your own cards"



class SecretPassageAction(PlayerAction):
    '''Action to use a secret passage to travel between connected rooms.'''
    
    def execute(self, game, player):
        # Check if player is currently in a room
        if player.current_room is None:
            raise InvalidActionException("You must be in a room to use a secret passage.")
        
        # Get secret passage connections
        secret_passages = game.rules.get_secret_passages()
        
        # Check if current room has a secret passage
        if player.current_room not in secret_passages:
            raise InvalidActionException(f"The {player.current_room} does not have a secret passage.")
        
        # Get the destination room
        destination_room = secret_passages[player.current_room]
        
        print(f"\n{player.get_colored_name()} is using the secret passage from {player.current_room} to {destination_room}.")
        
        # Move player to the destination room
        player.enter_room(destination_room)
        game.board.place_player_in_room(player, destination_room)
        
        print(f"{player.get_colored_name()} has arrived in the {destination_room}.")
        
        # Run the suggestion + optional-accuse flow using the shared helper
        end_game, moves_used = self.suggestion(game, player)
        return (end_game, moves_used)
    
    def get_description(self):
        return "Use a secret passage to travel between connected rooms"
        
        


class PlayerActionFactory:
    '''Factory for creating player action objects.'''
    
    def __init__(self):
        '''Initialize the factory with action mappings.'''
        self._actions = {}
    
    def register_action(self, action_name, action_class):
        '''Register an action with the factory.
        
        Args:
            action_name: String identifier for the action
            action_class: Class that implements PlayerAction
        '''
        self._actions[action_name] = action_class
    
    def create_action(self, action_name):
        '''Create an action instance.
        
        Args:
            action_name: String identifier for the action
            
        Returns:
            Instance of PlayerAction subclass
            
        Raises:
            InvalidActionException: If action_name not registered
        '''
        action_class = self._actions.get(action_name)
        if action_class is None:
            raise InvalidActionException(f"Unknown action: {action_name}")
        return action_class()
    
    def get_registered_actions(self):
        '''Returns list of registered action names.'''
        return list(self._actions.keys())