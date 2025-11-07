class Rules:
    def __init__(self):
        pass
        
    def get_dimensions(self):
        '''Returns the dimensions of the game board as (length, width).'''
        self.length = 22  
        self.width = 22
        return self.length, self.width
    
    def get_rooms(self):
        '''Returns the rooms in the game.'''
        self.rooms = [
            "Kitchen", "Ballroom", "Conservatory", "Dining Room",
            "Lounge", "Hall", "Study", "Library", "Billiard Room"
        ]
        return self.rooms

    def get_weapons(self):
        '''Returns the weapons in the game.'''
        self.weapons = [
            "Candlestick", "Dagger", "Lead Pipe", "Revolver",
            "Rope", "Wrench"
        ]
        return self.weapons

    def get_suspects(self):
        '''Returns the suspects in the game.'''
        self.suspects = [
            "Miss Scarlet", "Colonel Mustard", "Mrs. White",
            "Mr. Green", "Mrs. Peacock", "Professor Plum"
        ]
        return self.suspects
    
    def get_player_symbols(self):
        '''Returns the symbols used to represent each player on the board.'''
        return {
            "Miss Scarlet": "S",
            "Colonel Mustard": "M", 
            "Mrs. White": "W",
            "Mr. Green": "G",
            "Mrs. Peacock": "P",
            "Professor Plum": "L"  
        }
    
    def get_movement_rules(self):
        '''Returns movement restrictions and rules.'''
        return {
            "diagonal_movement": False,
            "can_backtrack": True,
            "must_leave_room": True,  
            "blocked_by_players": True,
            "can_pass_through_players": False
        }

    def get_room_entry_rules(self):
        '''Returns rules for entering and exiting rooms.'''
        return {
            "multiple_entrances": True,
            "exact_movement_to_door": False,  
            "secret_passage_ends_turn": True,
            "room_capacity": "unlimited"
        }

    def get_card_distribution_rules(self):
        '''Returns rules for card distribution.'''
        total_cards = len(self.rooms) + len(self.weapons) + len(self.suspects)
        return {
            "total_cards": total_cards,
            "murder_cards": 3,  # One of each type
            "cards_per_player_min": (total_cards - 3) // 6,
            "deal_remaining_face_up": False
        }

    def get_suggestion_rules(self):
        '''Returns rules for making suggestions.'''
        return {
            "must_be_in_room": True,
            "suggest_current_room": True,
            "can_suggest_self": True,
            "move_suggested_player": True,
            "move_suggested_weapon": True
        }

    def get_accusation_rules(self):
        '''Returns rules for making accusations.'''
        return {
            "can_accuse_anytime": True,
            "must_be_exact_match": True,
            "wrong_accusation_eliminates": True,
            "one_accusation_per_turn": True
        }

    def get_win_conditions(self):
        '''Returns the conditions for winning the game.'''
        return {
            "correct_accusation": True,
            "last_player_standing": True, 
            "reveal_murder_cards": ["room", "weapon", "suspect"]
        }
        
    def get_board_symbols(self):
        '''Returns the symbols used in room layouts.'''
        return {
            '#': 'Wall',
            'D': 'Door/Dining Room Space', 
            'K': 'Kitchen Space',
            'B': 'Ballroom/Billiard Room Space',
            'C': 'Conservatory Space',
            'L': 'Lounge/Library Space',
            'H': 'Hall Space',
            'S': 'Study Space/Secret Passage',
            'P': 'Player Position',
            '.': 'Empty Space/Hallway'
        }
