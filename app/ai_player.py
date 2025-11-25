import random
from re import M, S
from tracemalloc import start
from typing import List, Optional, Tuple, Dict, Set, Union

from colorama import Style

try:
    from app.player import Player
except ImportError:
    from player import Player


class AIPlayer(Player):
    """Simple suggestion-learning AI player.
    - starts in a room (pass start_position as a room name or initial hallway pos),
    - hops between rooms by using board.place_player_in_room / player.enter_room semantics,
    - builds knowledge from observations of suggestions and refutations.
    """
    MAX_CARDS = 3  
    
    def __init__(self, name: str, color: str, symbol: str, start_position, game) -> None:
        super().__init__(name, color, symbol, (0, 0))  
        self.known_cards: Dict[str, Optional[str]] = {}  # card -> owner name (or None if seen but unknown)
        self.known_count: Dict[str, int] = {}    # owner name -> count of known cards held
        self.suggestions_made = []          # history of suggestions AI made
        self.refutation_history = []        # (suggester, suggestion, refuter, shown_card)
        self.pref_room = None               # room AI prefers / currently "in"
        self.beliefs: Dict[str, Set[str]] = {}  # card -> possible suspects holding it
        self.solution_candidates: Set[str] = set() # cards likely in solution (no suspects remain)
        self.current_room = start_position
        # Note: initialize_beliefs(game) must be called AFTER cards are distributed

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


    
    def pick_card_with_min_holders(self, card_list: List[str]) -> str:
        # Find cards from this list that are in beliefs
        candidates_in_beliefs = []
        for card in card_list:
            if card in self.beliefs:
                candidates_in_beliefs.append(card)
        if candidates_in_beliefs:
            best_candidates = self.get_best_candidates(candidates_in_beliefs)
            return random.choice(best_candidates)
        else:
            return random.choice(card_list)

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
        
    def choose_card_to_show(self, matching_cards: List[str], to_player: 'Player') -> str:
        """When asked to show a card, choose a card to reveal.
           Strategy: show a random matching card, prefer cards already known by many (optional).
        """
        # Prefer to show a card that is least informative: pick one AI already has seen or random
        seen_matches = [c for c in matching_cards if c in self.known_cards]
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

        # Determine whether an actual refutation happened: a card was shown.
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

        if shown_card and suggester is self and final_refuter:
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
            

    def hop_to_room(self, room_name: str, game) -> None:
        """Place AI directly into a room (use board/ player room helpers).
           This does not use normal player movement; it uses board.place_player_in_room.
        """
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
    
    def play_turn(self, game) -> bool:
        """Execute the AI player's turn.
        """
        # Choose target room using the helper that prefers fewest holders
        rooms = game.rules.get_rooms()
        target_room = self.pick_card_with_min_holders(rooms)

        # Move to chosen room
        self.hop_to_room(target_room, game)

        # Make suggestion (suspect/weapon chosen by beliefs; room is current)
        suggestion = self.suggest(game)
        self.observe_suggestion(self, suggestion)

        # Run refutation using game logic
        refuting_players, shown_card = game.refute_suggestion(self, suggestion)
        self.observe_refutation(self, suggestion, refuting_players, shown_card)
        
        # game.notify_ai_observers(self, suggestion, refuting_player, shown_card)
        
        # Log suggestion and refutation
        game.log_suggestion(self, suggestion, refuting_players[-1], shown_card)
        
        # Make accusation if we have exactly 3 solution candidates (one of each type)
        if self.should_accuse(game):
            accusation = self.accuse(game)
            print(f"\n{self.get_colored_name()} is making an accusation: {accusation}")
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
        if self.known_cards:
            known_list = []
            for card, owner in sorted(self.known_cards.items()):
                if owner:
                    known_list.append(f"{card} ({owner})")
                else:
                    known_list.append(f"{card} (seen)")
            print("Known cards:", ", ".join(known_list))
        else:
            print("Known cards: None")

        # Belief map
        print("\nBeliefs (card: possible suspects):")
        if self.beliefs:
            for card in sorted(self.beliefs.keys()):
                suspects = sorted(self.beliefs[card]) if self.beliefs[card] else []
                print(f" - {card}: {', '.join(suspects) if suspects else 'none'}")
        else:
            print(" - (no tracked beliefs)")

        # Solution candidates
        candidates = sorted(self.solution_candidates) if self.solution_candidates else []
        print("\nSolution candidates (no suspects):", ", ".join(candidates) if candidates else "None")

        # Suggestions made
        print("\nSuggestions made:")
        if self.suggestions_made:
            for s in self.suggestions_made:
                print(" -", s)
        else:
            print(" - None")

        # Refutation history
        print("\nRefutation history (observed events):")
        if self.refutation_history:
            for r in self.refutation_history:
                print(" -", r)
        else:
            print(" - None")

        # Current location and hand
        print("\nCurrent room:", self.current_room)
        print("Current position:", self.current_position)
        hand = self.get_cards()
        print("Cards in hand:", ", ".join(hand) if hand else "None")

        print("================================\n")
