import random
from collections import deque
import re
from threading import TIMEOUT_MAX
import time
from typing import List, Optional, Tuple, Dict, Set, Union

from colorama import Style

from app.player import Player
from app.search import BFS


class AIPlayer(Player):
    """Simple suggestion-learning AI player.
    - starts in a room (pass start_position as a room name or initial hallway pos),
    - hops between rooms by using board.place_player_in_room / player.enter_room semantics,
    - builds knowledge from observations of suggestions and refutations.
    """
    MAX_CARDS = 3 
    TIME_BUFFER = 1

    
    def __init__(self, name: str, color: str, symbol: str, start_position, game) -> None:
        super().__init__(name, color, symbol, start_position)  
        self.known_cards: Dict[str, Optional[str]] = {}  # card -> owner name (or None if seen but unknown)
        self.known_count: Dict[str, int] = {}    # owner name -> count of known cards held
        self.suggestions_made = []          # history of suggestions AI made
        self.refutation_history = []        # (suggester, suggestion, refuter, shown_card)
        self.pref_room = None               # room AI prefers / currently "in"
        self.beliefs: Dict[str, Set[str]] = {}  # card -> possible suspects holding it
        self.solution_candidates: Set[str] = set() # cards likely in solution (no suspects remain)
        self.previous_path = []            # last path taken 
        if isinstance(start_position, tuple):
            self.current_room = None
        else:
            self.current_room = start_position

    def suggest(self, game) -> dict:
        """Create a suggestion from beliefs by picking cards with the least amount of possible holders.
        
        For each card type (suspect, weapon, room):
        - Find candidates that are in beliefs (not yet known)
        - If candidates exist, choose from those with minimum number of possible holders
        - If no candidates in beliefs, pick randomly from all cards of that type
        
        Args:
            game: The game instance (provides rules for card lists)
            
        Returns:
            dict: Suggestion with 'suspect', 'weapon', 'room' keys
        """
        # Get all available cards from rules
        all_suspects = game.rules.get_suspects()
        all_weapons = game.rules.get_weapons()

        # Pick suspect and weapon using beliefs; room is the AI's current room
        suspect = self.pick_card_with_min_holders(all_suspects)
        weapon = self.pick_card_with_min_holders(all_weapons) 
        room = self.get_current_room()

        for card in self.solution_candidates:
            if card in game.rules.get_suspects():
                suspect = card
            elif card in game.rules.get_weapons():
                weapon = card
            elif card in game.rules.get_rooms():
                room = card


        # Build suggestion
        suggestion = {
            "suspect": suspect,
            "weapon": weapon,
            "room": room
        }

        # Record suggestion
        self.suggestions_made.append({**suggestion, "room": self.current_room})

        return suggestion

    def pick_card_alphabetically(self, card_list: List[str]) -> str:
        """Pick the alphabetically first card from the given list."""
        return sorted(card_list)[0]

    
    def pick_card_with_min_holders(self, card_list: List[str]) -> str:
        # Find cards from this list that are in beliefs
        candidates_in_beliefs = []
        for card in card_list:
            if card in self.beliefs:
                candidates_in_beliefs.append(card)
        if candidates_in_beliefs:
            best_candidates = self.get_best_candidates(candidates_in_beliefs)
            return self.pick_card_alphabetically(best_candidates)
        else:
            return self.pick_card_alphabetically(card_list)

    def get_best_candidates(self, candidates_in_beliefs: List[str]) -> List[str]:
        """Return the subset of candidates that have the minimum number
        of possible holders according to `self.beliefs`.

        Args:
            candidates_in_beliefs: list of card names present in beliefs

        Returns:
            List[str]: best candidate cards (one or more)
        """
        min_holders = None
        for card in candidates_in_beliefs:
            holder_count = len(self.beliefs.get(card, []))
            if min_holders is None or holder_count < min_holders:
                min_holders = holder_count

        best_candidates = []
        for card in candidates_in_beliefs:
            if len(self.beliefs.get(card, [])) == min_holders:
                best_candidates.append(card)
        return best_candidates
    
    def pick_closest_room_with_min_holders(self, room_list: List[str], game) -> Tuple[Optional[List[str]], str]:
        
        skip = False
        for card in self.solution_candidates:
            if card in game.rules.get_rooms():
                skip = True

        candidates_in_beliefs = []
        for room in room_list:
            if room in self.beliefs:
                candidates_in_beliefs.append(room)
        
        if candidates_in_beliefs and not skip:
            best_candidates = self.get_best_candidates(candidates_in_beliefs)
        else:
            best_candidates = room_list
        
        #if room is already in solution just chose closest room

            
        # If only one candidate, return its path and name
        if len(best_candidates) == 1:
            single = best_candidates[0]
            p = BFS(self.current_room, self.current_position, single, game)
            return (p, single)
        
        closest_room = None
        min_path_length = None
        chosen_path = None
        
        for room in best_candidates:
            path = BFS(self.current_room, self.current_position, room, game)
            if path is not None:
                path_length = len(path)
                if min_path_length is None or path_length < min_path_length:
                    min_path_length = path_length
                    closest_room = room
                    chosen_path = path

        if closest_room is None:
            # No path to any candidate; pick alphabetically and return no path
            return (None, self.pick_card_alphabetically(best_candidates))
        
        return (chosen_path, closest_room)
        
    def choose_card_to_show(self, matching_cards: List[str], to_player: 'Player') -> str:
        """When asked to show a card, choose a card to reveal.
           Strategy: show a random matching card, prefer cards already known by many (optional).
        """
        seen_matches = []
        for card in matching_cards:
            if card in self.known_cards:
                seen_matches.append(card)
        if seen_matches:
            return random.choice(seen_matches)
        return random.choice(matching_cards)

    def observe_suggestion(self, suggester: 'Player', suggestion: dict) -> None:

        self.suggestions_made.append({"suggester": suggester.name, **suggestion})

    def observe_refutation(self, suggester: 'Player', suggestion: dict,
                           refuters: Optional[Union[List['Player'], 'Player']],
                           shown_card: Optional[str] = None) -> None:
        # Normalize refuters into a list. Accept either a single Player, a list
        # of Players (ordered), or None. Note: `refuters` may be the ordered
        # list of players who were asked to refute even when none could refute;
        # therefore we must rely on `shown_card` to determine whether an actual
        # refutation occurred.
        if refuters is None:
            refuters_list: List[Player] = []
        elif isinstance(refuters, list):
            refuters_list = refuters
        else:
            refuters_list = [refuters]

    
        refuter_names: List[str] = []
        for refuter in refuters_list:
            refuter_names.append(refuter.get_name())

     
        refutation_happened = shown_card is not None and len(refuters_list) > 0

        final_refuter = None
        if refutation_happened:
            final_refuter = refuters_list[-1].get_name()

        # Record history (final_refuter is None when no one showed a card)
        self.refutation_history.append({
            "suggester": suggester.name,
            "suggestion": suggestion,
            "refuters": refuter_names,
            "refuter": final_refuter,
        })

      
        if suggester is self and shown_card and final_refuter:
            self.mark_card_seen(shown_card, owner=final_refuter)

        if refutation_happened:
            previous_refuters = refuter_names[:-1]
            if previous_refuters:
                for key in ("suspect", "weapon", "room"):
                    card = suggestion.get(key)
                    if not card or card in self.known_cards:
                        continue

                    if card in self.beliefs:
                        for prev in previous_refuters:
                            self.remove_suspect_from_card(card, prev)

        else:
            current_name = suggester.get_name()
            for key in ("suspect", "weapon", "room"):
                card = suggestion.get(key)
                if not card:
                    continue

                if card in self.known_cards:
                    continue

                if card in self.beliefs:
                    if suggester is self:
                        # AI suggested and no one showed a card -> card in solution
                        self.beliefs[card].clear()
                    else:
                        # Another player suggested and no one refuted -> only the
                        # suggester might have the card (others passed)
                        suspects_to_keep = {current_name}
                        self.beliefs[card].intersection_update(suspects_to_keep)

                    if not self.beliefs[card]:
                        self.solution_candidates.add(card)
                        del self.beliefs[card]
            


    
    def navigate_to_room(self, target_room: str, game, roll_dice, path) -> bool:
        """Execute movement actions to reach target room using BFS pathfinding.
        
        Returns True if successfully reached target room, False otherwise.
        """
        
        # If no precomputed path provided, compute one now
        if path is None:
            path = BFS(self.current_room, self.current_position, target_room, game)
            if path is None:
                print(f"{self.get_colored_name()} cannot find path to {target_room}")
                return False

        print(f"{self.get_colored_name()} navigating to {target_room}")
        
        for action in path:
            if roll_dice <= 0 and not action.startswith('enter '):
                break
            if action == 'secret':
                # Use secret passage
                secret_passages = game.rules.get_secret_passages()
                if self.current_room in secret_passages:
                    dest_room = secret_passages[self.current_room]
                    self.current_room = dest_room
                    self.current_position = None
                    game.board.place_player_in_room(self, dest_room)
                    self.player_print(f"  → Used secret passage to {dest_room}")
                    break
                    
            elif action.startswith('exit '):
                # Parse room name and exit position from action
                parts = action.split()
                room_name = parts[1]
                exit_row = int(parts[2])
                exit_col = int(parts[3])
                exit_pos = (exit_row, exit_col)
                
                # Exit to the specified position
                self.exit_room(exit_pos)
                game.board.move_player_to_hallway(self, exit_pos)
                self.player_print(f"  → Exited {room_name} to hallway position {exit_pos}")
                        
            elif action.startswith('move '):
                # Parse target position from action
                parts = action.split()
                target_row = int(parts[1])
                target_col = int(parts[2])
                target_pos = (target_row, target_col)
                
            
                self.move_to(target_pos)
                game.board.move_player(self)
                self.player_print(f"  → Moved to hallway position {target_pos}")
                roll_dice -= 1

                
            elif action.startswith('enter '):
                # Enter a room
                room_name = action.split(' ', 1)[1]
                self.enter_room(room_name)
                game.board.place_player_in_room(self, room_name)
                self.player_print(f"  → Entered {room_name}")
                break
        
        return self.current_room == target_room
    
    def hop_to_room(self, room_name: str, game) -> None:
        """Navigate to target room using BFS pathfinding.
        Falls back to direct placement if pathfinding fails.
        """
        # Attempt to find a path and navigate using a very large roll allowance
        path = BFS(self.current_room, self.current_position, room_name, game)
        if self.navigate_to_room(room_name, game, 9999, path):
            return
        
        # Fallback: direct placement
        print(f"{self.get_colored_name()} using direct placement to {room_name}")
        game.board.place_player_in_room(self, room_name)
        self.current_room = room_name
    
    def initialize_beliefs(self, game) -> None:
        """Initialize beliefs for all cards in the game's bank.

        - Assign all suspects to each card.
        - Remove cards the AI holds (mark as known).
        """
        all_cards = []
        all_cards = (game.rules.get_suspects() +
                         game.rules.get_weapons() +
                         game.rules.get_rooms())

        # Get all suspect names from the game
        all_opponents = set()
        for player in game.get_players():
            if player.get_name() != self.get_name():
                all_opponents.add(player.get_name())

        for card in all_cards:
            # initialize: all opponents might hold this card
            # (AI doesn't include itself since it knows its own cards)
            self.beliefs[card] = all_opponents.copy()
        
        # Mark cards AI holds as known (owned by self) and remove from beliefs
        for card in self.get_cards():
            self.mark_card_seen(card, owner=self.get_name())

    def mark_card_seen(self, card: str, owner: Optional[str] = None) -> None:
        """Mark a card as seen (known to be held by someone).
        """
        self.known_cards[card] = owner

        if card in self.beliefs:
            del self.beliefs[card]


        if card in self.solution_candidates:
            self.solution_candidates.discard(card)

        if owner:
            self.known_count[owner] = self.known_count.get(owner, 0) + 1
            if self.known_count[owner] >= self.MAX_CARDS:
                self.remove_player_from_all_beliefs(owner)

    def remove_player_from_all_beliefs(self, player_name: str) -> None:
        """Remove `player_name` from all belief sets. If a belief set
        becomes empty, mark the card as a solution candidate and stop
        tracking it.
        """
        for card in list(self.beliefs.keys()):
            if player_name in self.beliefs[card]:
                self.beliefs[card].discard(player_name)
                if not self.beliefs[card]:
                    self.solution_candidates.add(card)
                    del self.beliefs[card]

    def remove_suspect_from_card(self, card: str, suspect_name: str) -> None:
        """Remove a suspect from a card's possible holders.

        If no suspects remain, mark the card as a solution candidate.
        """
        if card not in self.beliefs:
            return
        
        self.beliefs[card].discard(suspect_name)
        
        # If no suspects remain, this card is likely in the solution
        if not self.beliefs[card]:
            self.solution_candidates.add(card)
            del self.beliefs[card]

    def note_confirmed(self, card: str, owner: Optional[str], game=None) -> None:
        """Convenience: mark `card` as confirmed held by `owner` (owner can be None).
        This marks the card as seen and tracks it as known by the AI.
        """
        self.mark_card_seen(card, owner=owner)

    def note_possible_solution(self, card: str) -> None:
        """Mark card as likely part of the solution (no suspects remain)."""
        if card in self.beliefs:
            self.beliefs[card].clear()
            self.solution_candidates.add(card)
            del self.beliefs[card]

    def should_accuse(self, game) -> bool:
        """Return True if AI has exactly three solution candidates forming a valid accusation.
        
        Valid accusation requires exactly one suspect, one weapon, and one room.
        """
        if len(self.solution_candidates) != 3:
            return False
        
        candidate_suspects, candidate_weapons, candidate_rooms = self.get_candidates(game)
        
        return len(candidate_suspects) == 1 and len(candidate_weapons) == 1 and len(candidate_rooms) == 1

    def accuse(self, game) -> dict:
        """Make an accusation using the three solution candidates.
        
        Requires exactly 3 solution candidates (one suspect, one weapon, one room).
        should_accuse() must return True before calling this method.
        
        Args:
            game: The game instance (provides rules for card lists)
            
        Returns:
            dict: Accusation with 'suspect', 'weapon', 'room' keys
        """
        
        candidate_suspects, candidate_weapons, candidate_rooms = self.get_candidates(game)
        
        # Use the exact solution candidates (should be exactly one of each)
        # Convert sets to lists so we can index them
        suspect = list(candidate_suspects)[0] if candidate_suspects else None
        weapon = list(candidate_weapons)[0] if candidate_weapons else None
        room = list(candidate_rooms)[0] if candidate_rooms else None
        
        if not (suspect and weapon and room):
            raise ValueError(f"Invalid solution candidates: must have exactly one suspect, weapon, and room. Got: {self.solution_candidates}")
        
        accusation = {
            "suspect": suspect,
            "weapon": weapon,
            "room": room
        }
        
        return accusation
    def get_candidates(self, game) -> Set[str]:
        """Return the current set of solution candidates."""
        candidate_suspects = set()
        candidate_weapons = set()
        candidate_rooms = set()
        
        for card in self.solution_candidates:
            if card in game.rules.get_suspects():
                candidate_suspects.add(card)
            elif card in game.rules.get_weapons():
                candidate_weapons.add(card)
            elif card in game.rules.get_rooms():
                candidate_rooms.add(card)
        return candidate_suspects, candidate_weapons, candidate_rooms
    
    def player_print(self, print_statement: str) -> None:
        print(print_statement)
        time.sleep(self.TIME_BUFFER)
        return

    def play_turn(self, game) -> bool:
        """Execute the AI player's turn.
        """
        # Choose target room using the helper that prefers fewest holders
        self.player_print(f"\nIt's {self.get_colored_name()}'s turn!")
        roll_dice = self.roll_die()
        self.player_print(f"{self.get_colored_name()} rolled a {roll_dice}.")
        self.player_print(f"{self.get_colored_name()} is deciding on a target room...")
        rooms = game.rules.get_rooms()
        path, target_room = self.pick_closest_room_with_min_holders(rooms, game)


        if not self.should_accuse(game):
            
            if self.current_room != target_room:
                self.navigate_to_room(target_room, game, roll_dice, path)
                self.previous_path = path if path else None
            
            if not self.current_room:
                self.player_print(f"{self.get_colored_name()} ends turn.")
                return False
            target_room = self.current_room if self.current_room else target_room
            # Make suggestion (suspect/weapon chosen by beliefs; room is current)
            
            suggestion = self.suggest(game)
            self.observe_suggestion(self, suggestion)
            self.player_print(f"{self.get_colored_name()} suggests: {suggestion}")
            # Run refutation using game logic
            refuting_players, shown_card = game.refute_suggestion(self, suggestion)
            self.observe_refutation(self, suggestion, refuting_players, shown_card)
            
            # game.notify_ai_observers(self, suggestion, refuting_player, shown_card)
            
            # Log suggestion and refutation
            game.log_suggestion(self,suggestion, refuting_players[-1], shown_card)
            
            # Make accusation if we have exactly 3 solution candidates (one of each type)
        if self.should_accuse(game):
            accusation = self.accuse(game)
            self.player_print(f"\n{self.get_colored_name()} is making an accusation: {accusation}")
            return game.handle_accusation(self, accusation)

        return False

    
    def get_colored_name(self) -> str:
        tag = "[AI]"
        try:
            return f"{self.color}{self.name} {tag}{Style.RESET_ALL}"
        except Exception:
            return f"{self.name} {tag}"

    def display_knowledge(self) -> None:
        """Print a readable dump of the AI player's internal knowledge and state."""
        print(f"\n=== AI Player Knowledge: {self.get_colored_name()} ===")

        # Known cards (cards the AI has privately seen or holds)
        print("\nKnown cards:")
        if self.known_cards:
            for card, owner in sorted(self.known_cards.items()):
                if owner:
                    print(f"  - {card} ({owner})")
                else:
                    print(f"  - {card} (seen)")
        else:
            print("  - None")

        # Belief map
        print("\nBeliefs (card: possible suspects):")
        if self.beliefs:
            for card in sorted(self.beliefs.keys()):
                suspects = sorted(self.beliefs[card]) if self.beliefs[card] else []
                if suspects:
                    print(f"  - {card}: ", end="")
                    for i, suspect in enumerate(suspects):
                        if i > 0:
                            print(", ", end="")
                        print(suspect, end="")
                    print() 
                else:
                    print(f"  - {card}: (none)")
        else:
            print("  - (no tracked beliefs)")

        # Solution candidates
        print("\nSolution candidates (no suspects):")
        if self.solution_candidates:
            print("  - ", end="")
            for i, card in enumerate(sorted(self.solution_candidates)):
                if i > 0:
                    print(", ", end="")
                print(card, end="")
            print()  
        else:
            print("  - None")

        # Suggestions made
        print("\nSuggestions made:")
        if self.suggestions_made:
            for s in self.suggestions_made:
                suggester = s.get('suggester', 'Unknown')
                suspect = s.get('suspect', '?')
                weapon = s.get('weapon', '?')
                room = s.get('room', '?')
                print(f"  - {suggester}: {suspect}, {weapon}, {room}")
        else:
            print("  - None")

        # Refutation history
        print("\nRefutation history (observed events):")
        if self.refutation_history:
            for r in self.refutation_history:
                suggester = r.get('suggester', 'Unknown')
                suggestion = r.get('suggestion', {})
                suspect = suggestion.get('suspect', '?')
                weapon = suggestion.get('weapon', '?')
                room = suggestion.get('room', '?')
                refuter = r.get('refuter', 'None')
                print(f"  - {suggester} suggested ({suspect}, {weapon}, {room}) → refuted by {refuter}")
        else:
            print("  - None")

        print("\nPrevious path taken:")
        if self.previous_path:
            print("  - ", end="")
            for i, action in enumerate(self.previous_path):
                if i > 0:
                    print(" → ", end="")
                print(action, end="")
            print()  
        else:
            print("  - None")

        # Current location and hand
        print("\nCurrent room:", self.current_room if self.current_room else "(in hallway)")
        print("Current position:", self.current_position if self.current_position else "(in room)")
        
        hand = self.get_cards()
        if hand:
            print("Cards in hand: ", end="")
            for i, card in enumerate(hand):
                if i > 0:
                    print(", ", end="")
                print(card, end="")
            print()  
        else:
            print("Cards in hand: None")

        print("\n================================\n")
