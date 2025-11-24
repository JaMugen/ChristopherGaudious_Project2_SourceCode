import random
from typing import List, Optional, Tuple, Dict, Set, Union
from webbrowser import get

from colorama import Style
try:
    from app.exceptions import InvalidMoveException, InvalidActionException
except ImportError:
    from exceptions import InvalidMoveException, InvalidActionException


class Player:
    '''Base class representing a player in the Cluedo game.'''
    
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
    def show_cards(self):
        '''Display the player's cards.'''
        if not self.get_cards():
            print(f"{self.get_colored_name()} has no cards.")
        else:
            print(f"{self.get_colored_name()}'s cards: {', '.join(self.get_cards())}")
            
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
    
    def get_name(self):
        '''Return the player's name.'''
        return self.name
    
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
    
    def can_take_turn(self):
        '''Returns whether this player can take turns.'''
        return True
    
    def can_refute(self):
        '''Returns whether this player can refute suggestions.'''
        return True
    
    @classmethod
    def _copy_state_from(cls, src, dst):
        '''Copy runtime state from src player to dst player.'''
        dst.current_position = src.current_position
        dst.previous_position = src.previous_position
        dst.current_room = src.current_room
        dst.cards = list(src.cards)
        dst.roll = src.roll
        dst.is_active = src.is_active
        dst.is_eliminated = src.is_eliminated


class ActivePlayer(Player):
    '''Represents an active player who takes turns and can refute.'''
    
    def __init__(self, name, color, symbol, start_position):
        super().__init__(name, color, symbol, start_position)
        self.is_active = True
        self.is_eliminated = False
    
    def get_colored_name(self):
        '''Returns the player name with color formatting (active).'''
        return f"{self.color}{self.name}{Style.RESET_ALL}"


class InactivePlayer(Player):
    '''Represents an inactive player who cannot take turns but can refute.'''
    
    def __init__(self, name, color, symbol, start_position):
        super().__init__(name, color, symbol, start_position)
        self.is_active = False
        self.is_eliminated = False
    
    def can_take_turn(self):
        '''Inactive players do not take turns.'''
        return False
    
    def can_refute(self):
        '''Inactive players can still refute suggestions.'''
        return True
    
    def get_colored_name(self):
        '''Returns the player name with color formatting and [INACTIVE] tag.'''
        return f"{self.color}{self.name} [INACTIVE]{Style.RESET_ALL}"


class EliminatedPlayer(Player):
    '''Represents an eliminated player who cannot take turns but can refute.'''
    
    def __init__(self, name, color, symbol, start_position):
        super().__init__(name, color, symbol, start_position)
        self.is_active = False
        self.is_eliminated = True
    
    def can_take_turn(self):
        '''Eliminated players do not take turns.'''
        return False
    
    def can_refute(self):
        '''Eliminated players can still refute suggestions.'''
        return True
    
    def get_colored_name(self):
        '''Returns the player name with color formatting and [ELIMINATED] tag.'''
        return f"{self.color}{self.name} [ELIMINATED]{Style.RESET_ALL}"
    
    @classmethod
    def from_player(cls, src):
        '''Create an EliminatedPlayer from an existing player, preserving state.'''
        dest = cls(src.name, src.color, src.symbol, src.start_position)
        Player._copy_state_from(src, dest)
        dest.is_eliminated = True
        dest.is_active = False
        return dest


class AIPlayer(Player):
    """Simple suggestion-learning AI player.
    - starts in a room (pass start_position as a room name or initial hallway pos),
    - hops between rooms by using board.place_player_in_room / player.enter_room semantics,
    - builds knowledge from observations of suggestions and refutations.
    """
    
    def __init__(self, name: str, color: str, symbol: str, start_position):
        super().__init__(name, color, symbol, start_position)
        # known_cards maps card -> owner name (who has the card)
        self.known_cards: Dict[str, Optional[str]] = {}
        self.suggestions_made = []          # history of suggestions AI made
        self.refutation_history = []        # (suggester, suggestion, refuter, shown_card)
        self.pref_room = None               # room AI prefers / currently "in"
        self.beliefs: Dict[str, Set[str]] = {}  # card -> possible suspects holding it
        self.solution_candidates: Set[str] = set() # cards likely in solution (no suspects remain)
        self.known
        if isinstance(start_position, str) and start_position in getattr(self, "current_room", {}) or start_position is None:
            self.current_room = start_position

    def make_suggestion_choices(self, available_suspects: List[str], available_weapons: List[str]) -> Tuple[str, str]:
        """Return (suspect, weapon). Strategy:
           - Prefer suspects/weapons the AI has NOT seen.
           - Pick randomly among unknowns, otherwise random among all.
        """
        unknown_suspects = [s for s in available_suspects if s not in self.known_cards]
        unknown_weapons = [w for w in available_weapons if w not in self.known_cards]

        suspect = random.choice(unknown_suspects) if unknown_suspects else random.choice(available_suspects)
        weapon  = random.choice(unknown_weapons)  if unknown_weapons else random.choice(available_weapons)

        # record suggestion for KB
        self.suggestions_made.append({"suspect": suspect, "weapon": weapon, "room": self.current_room})
        return suspect, weapon

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
                           refuters: Optional[Union[List['Player'], 'Player']]) -> None:

        # Normalize refuters into a list. Accept either a single Player, a list
        # of Players (ordered), or None. Record the list of refuter names in
        # history and treat the final element as the successful refuter.
        refuters_list = []
        if refuters is None:
            refuters_list = []
        elif isinstance(refuters, list):
            refuters_list = refuters
        else:
            # Single refuter provided
            refuters_list = [refuters]

        # Build a list of refuter names using Player.get_name() when available
        refuter_names = []
        for r in refuters_list:
            refuter_names.append(r.get_name())
        final_refuter = None
        if refuter_names:
            final_refuter = refuter_names[-1]
        else:
            final_refuter = None

        self.refutation_history.append({
            "suggester": suggester.name,
            "suggestion": suggestion,
            "refuters": refuter_names,
            "refuter": final_refuter,
        })

        if refuter_names:
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
                    # Remove all suspects except the current suggester
                    suspects_to_remove = self.beliefs[card] - {current_name}
                    for suspect in suspects_to_remove:
                        self.beliefs[card].discard(suspect)

                    # If no suspects remain, add to solution candidates
                    if not self.beliefs[card]:
                        self.solution_candidates.add(card)
                        del self.beliefs[card]
            

    def hop_to_room(self, room_name: str, game) -> None:
        """Place AI directly into a room (use board/ player room helpers).
           This does not use normal player movement; it uses board.place_player_in_room.
        """

        prev = self.current_position
        if prev is not None:
            # update board to clear previous position
            try:
                game.board.move_player_to_hallway(self, prev)  
            except Exception:
                # fallback: clear board cell directly if needed
                x, y = prev
                try:
                    game.board.board[x][y] = '.'
                except Exception:
                    pass

        # Use existing enter-room semantics so player state is consistent:
        self.current_room = room_name
        self.current_position = None
        # Place on board via game.board so board's internal state is updated
        try:
            game.board.place_player_in_room(self, room_name)
        except Exception:
            # best-effort: still update local state
            pass

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
            # initialize: all suspects might hold this card
            self.beliefs[card] = all_opponents.copy()
        # Remove cards AI holds from tracking (mark as held by self)
        for card in self.get_cards():
            self.mark_card_seen(card, owner=self.get_name())

    def mark_card_seen(self, card: str, owner: Optional[str] = None) -> None:
        """Mark a card as seen (known to be held by someone).

        Side effects:
        - Move the card to the AI's known set and stop tracking it in beliefs.
        - Remove from solution candidates if present.
        """
        # Record owner (who holds the card). If owner not provided, keep
        # existing owner value or set to None to indicate seen but unknown owner.
        self.known_cards[card] = owner
        if card in self.beliefs:
            del self.beliefs[card]
    
        if card in self.solution_candidates:
            self.solution_candidates.discard(card)

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

    def should_accuse(self) -> bool:
        """Return True if AI has confirmed three solution candidates (no suspects remain).

        Caller is responsible for verifying the three cards form a valid accusation set.
        """
        return len(self.solution_candidates) >= 3

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