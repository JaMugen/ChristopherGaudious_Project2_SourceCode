from colorama import init, Fore

class Config:
    def __init__(self):
        # Initialize colorama for cross-platform colored output
        init(autoreset=True)
    
    def get_player_colors(self):
        '''Returns colorama color codes for each player.'''
        return {
            "Miss Scarlet": Fore.RED,
            "Colonel Mustard": Fore.YELLOW,
            "Mrs. White": Fore.WHITE,
            "Mr. Green": Fore.GREEN,
            "Mrs. Peacock": Fore.BLUE,
            "Professor Plum": Fore.MAGENTA
        }
    
    def get_player_start_positions(self):
        '''Returns starting positions for each player.'''
        return {
            "Miss Scarlet": (0, 9),
            "Colonel Mustard": (5, 0),
            "Mrs. White": (3, 21),
            "Mr. Green": (14, 0),
            "Mrs. Peacock": (21, 7),
            "Professor Plum": (18, 21)
        }