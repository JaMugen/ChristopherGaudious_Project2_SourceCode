try:
    from app.rules import Rules
    from app.config import Config
except ImportError:
    from rules import Rules
    from config import Config
from colorama import init, Fore, Back, Style

# Initialize colorama for cross-platform colored output
init(autoreset=True)

class Board:
    '''Represents the game board.
    Board uses these symbols:
    - '.' = hallway (walkable)
    - '#' = wall (not walkable)
    - 'd' = doorway (entry point to room)
    - Letters = room spaces (K=Kitchen, B=Ballroom, etc.)
    - Player symbols = S, M, W, G, P, L (colored)
    '''
    def __init__(self):
        rules = Rules()
        config = Config()
        self.board_length, self.board_width = rules.get_dimensions()
        self.rooms = {}
        for room in rules.get_rooms():
            self.rooms[room] = room[0]
        self.weapons = rules.get_weapons()
        self.suspects = rules.get_suspects()
        self.player_colors = config.get_player_colors()
        self.player_symbols = rules.get_player_symbols()
        self.player_start_positions = config.get_player_start_positions()
        self.rules = rules
        
        # Initialize board with empty spaces
        self.board = []
        for i in range(self.board_length):
            row = []
            for j in range(self.board_width):
                row.append('.')
            self.board.append(row)

        room_layout = self.get_room_layouts()

        for room_name, room_info in room_layout.items():
            pos_x, pos_y = room_info["position"]
            layout = room_info["layout"]
            for i, row in enumerate(layout):
                for j, cell in enumerate(row):
                    if pos_x + i < self.board_length and pos_y + j < self.board_width:
                        self.board[pos_x + i][pos_y + j] = cell
        self.place_players_on_board()
        
    def apply_color_to_text(self, text, color):
        '''Apply colorama color to text with auto-reset.'''
        return f"{color}{text}{Style.RESET_ALL}"
        
    def place_players_on_board(self):
        '''Places player tokens at their starting positions on the board.'''
        # Track actual player positions
        self.current_player_positions = {}
        
        for player, position in self.player_start_positions.items():
            x, y = position
            if 0 <= x < self.board_length and 0 <= y < self.board_width:
                symbol = self.player_symbols[player]
                self.board[x][y] = symbol
                # Store the actual position for this player
                self.current_player_positions[(x, y)] = player
        
    def get_room_layouts(self):
        '''Returns 2D layouts for each room with halls (.), walls (#), doors (d), room spaces (R).'''
        return {
            "Kitchen": {
                "position": (0, 0),  # Top-left corner position on board
                "size": (5, 6),      # Length x Width
                "layout": [
                    ['#', '#', '#', '#', '#', '#'],
                    ['#', 'K', 'K', 'K', 'K', '#'],
                    ['#', 'K', 'K', 'K', 'K', '#'],
                    ['#', 'K', 'K', 'K', 'K', '#'],
                    ['#', '#', '#', '#', 'd', '#']  # S = Secret passage to Study
                ]
            },
            "Ballroom": {
                "position": (0, 8),
                "size": (6, 7),
                "layout": [
                    ['.', '.', '#', '#', '#', '.', '.'],
                    ['#', 'B', 'B', 'B', 'B', 'B', '#'],
                    ['#', 'B', 'B', 'B', 'B', 'B', '#'],
                    ['#', 'B', 'B', 'B', 'B', 'B', '#'],
                    ['#', 'B', 'B', 'B', 'B', 'B', '#'],
                    ['d', 'B', 'B', 'B', 'B', 'B', 'd'],
                    ['#', 'd', '#', '#', 'd', '#', '#']
                ]
            },
            "Conservatory": {
                "position": (0, 16),
                "size": (4, 5),
                "layout": [
                    ['#', '#', '#', '#', '#', '#'], 
                    ['#', 'C', 'C', 'C', 'C', '#'],
                    ['d', 'C', 'C', 'C', 'C', '#'],
                    ['.', '#', '#', '#', '#', '.'],
                ]
            },
            "Dining Room": {
                "position": (7, 0),
                "size": (7, 8),
                "layout": [
                    ['#', '#', '#', '#', '#', '.', '.', '.'],
                    ['#','D', 'D', 'D', 'D', '#', '#', '#'],
                    ['#', 'D', 'D', 'D', 'D', 'D', 'D', '#'],
                    ['#', 'D', 'D', 'D', 'D', 'D', 'D', '#'],
                    ['#', 'D', 'D', 'D', 'D', 'D', 'D', 'd'],
                    ['#', 'D', 'D', 'D', 'D', 'D', 'D', '#'],
                    ['#', '#', '#', '#', 'd', '#', '#', '#']
                ]
            },
            "Lounge": {
                "position": (17, 0),
                "size": (5, 7),
                "layout": [
                    ['#','#','#', '#', '#', '#', 'd'],
                    ['#', 'O', 'O', 'O', 'O', 'O', '#'],
                    ['#','O', 'O', 'O', 'O', 'O', '#'],
                    ['#', 'O','O', 'O', 'O', 'O', '#'],
                    ['#','#', '#', '#', '#', '#', '#']
                ]
            },
            "Hall": {
                "position": (16, 9),
                "size": (6, 6),
                "layout": [
                    ['#','#','d', 'd','#','#'],
                    ['#', 'H', 'H', 'H','H', '#'],
                    ['#', 'H', 'H', 'H','H', '#'],
                    ['#', 'H', 'H', 'H','H', 'd'],
                    ['#', 'H', 'H', 'H','H', '#'],
                    ['#', '#', '#', '#','#', '#']

                ]
            },
            "Study": {
                "position": (19, 16),
                "size": (3, 6),
                "layout": [
                    ['#', 'D', '#', '#', '#', '#'],  
                    ['#', 'S', 'S', 'S', 'S', '#'],
                    ['#', '#', '#', '#', '#', '#']
                ]
            },
            "Library": {
                "position": (12, 16),
                "size": (5, 6),
                "layout": [
                    ['.', '#', '#', '#', 'd', '#'],
                    ['#', 'L', 'L', 'L', 'L', '#'],
                    ['d', 'L', 'L', 'L', 'L', '#'],
                    ['#', 'L', 'L', 'L', 'L', '#'],
                    ['.', '#', '#', '#', '#', '#']
                ]
            },
            "Billiard Room": {
                "position": (6, 17),
                "size": (5, 5),
                "layout": [
                    ['#', '#', '#', 'd', '#'],
                    ['d', 'R', 'R', 'R', '#'],
                    ['#', 'R', 'R', 'R', '#'],
                    ['#', 'R', 'R', 'R', '#'],
                    ['#', '#', '#', '#', '#']
                ]
            }
        }
        
    def display_board(self):
        '''Displays the board in the console with colored player tokens.'''
        for row_idx, row in enumerate(self.board):
            colored_row = []
            for col_idx, cell in enumerate(row):
                if (row_idx, col_idx) in self.current_player_positions:
                    player = self.current_player_positions[(row_idx, col_idx)]
                    color = self.player_colors[player]
                    colored_cell = self.apply_color_to_text(cell, color)
                    colored_row.append(colored_cell)
                else:
                    colored_row.append(cell)
            
            print(' '.join(colored_row))
    
    def display_legend(self):
        '''Displays a legend showing player colors and symbols.'''
        print("\n=== PLAYER LEGEND ===")
        for player in self.suspects:
            color = self.player_colors[player]
            symbol = self.player_symbols[player]
            colored_symbol = self.apply_color_to_text(symbol, color)
            print(f"{colored_symbol} - {player}")
        print("=====================\n")

    def get_secret_passages(self):
        '''Returns the secret passages in the game.'''
        return {
            "Kitchen": "Study",
            "Study": "Kitchen",
            "Conservatory": "Lounge",
            "Lounge": "Conservatory"
        }

            
if __name__ == "__main__":
    board = Board()
    board.display_legend()
    board.display_board()
    
    