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
    
    def get_board_symbols(self):
        '''Returns the symbols used in room layouts.'''
        return {
            '#': 'Wall',
            'd': 'Door',
            'K': 'Kitchen',
            'B': 'Ballroom',
            'C': 'Conservatory',
            'D': 'Dining Room',
            'O': 'Lounge',
            'H': 'Hall',
            'S': 'Study',
            'L': 'Library',
            'I': 'Billiard Room',
            '.': 'Empty Space/Hallway'
        }
    
    def get_secret_passages(self):
        '''Returns the secret passage connections between rooms.'''
        return {
            "Kitchen": "Study",
            "Study": "Kitchen",
            "Lounge": "Conservatory",
            "Conservatory": "Lounge"
        }
