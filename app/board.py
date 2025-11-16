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
        self.current_player_positions = {}  # (row, col) -> player name
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


        
    def apply_color_to_text(self, text, color):
        '''Apply colorama color to text with auto-reset.'''
        return f"{color}{text}{Style.RESET_ALL}"

    def move_player_on_board(self):
        "''Moves a player on the board.'''"

    def get_room_symbol(self, room_name):
        '''Returns the symbol for a given room from the board symbols mapping.'''
        # Get the symbol to room name mapping from rules
        board_symbols = self.rules.get_board_symbols()
        # Reverse lookup: find symbol where value equals room_name
        for symbol, name in board_symbols.items():
            if name == room_name:
                return symbol
        return None
        
    def get_room_layouts(self):
        '''Returns 2D layouts for each room with halls (.), walls (#), doors (d), room spaces (R).'''
        return {
            "Kitchen": {
                "position": (0, 0),  # Top-left corner position on board
                "size": (5, 6),
                "door_locations": [(4, 4)],      # Length x Width
                "exit_offsets": [(5, 4)],  # Where player ends up when exiting through each door
                "layout": [
                    ['#', '#', '#', '#', '#', '#'],
                    ['#', 'K', 'K', 'K', 'K', '#'],
                    ['#', 'K', 'K', 'K', 'K', '#'],
                    ['#', 'K', 'K', 'K', 'K', '#'],
                    ['#', '#', '#', '#', 'd', '#']  
                ]
            },
            "Ballroom": {
                "position": (0, 8),
                "size": (6, 7),
                "door_locations": [(5, 0), (6, 1),(6,4), (5, 6)],
                "exit_offsets": [(5, -1), (7, 1), (7, 4), (5, 7)], 
                "layout": [
                    ['.', '.', '#', '#', '#', '.', '.'],
                    ['#', '#', 'B', 'B', 'B', '#', '#'],
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
                "door_locations": [(2, 0)],
                "exit_offsets": [(2, -1)],
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
                    "door_locations": [(4,7), (6, 4)],
                "exit_offsets": [(4, 8), (7, 4)],  
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
                "door_locations": [(0, 6)],
                "exit_offsets": [(0, 7)],  # Right door
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
                "door_locations": [(0, 2), (0, 3), (5, 5)],
                "exit_offsets": [(-1, 2), (-1, 3), (5, 6)],  
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
                "door_locations": [(0, 1)],
                "exit_offsets": [(-1, 1)],  # Top door
                "layout": [
                    ['#', 'd', '#', '#', '#', '#'],  
                    ['#', 'S', 'S', 'S', 'S', '#'],
                    ['#', '#', '#', '#', '#', '#']
                ]
            },
            "Library": {
                "position": (12, 16),
                "size": (5, 6),
                "door_locations": [(2, 0), (0, 4)],
                "exit_offsets": [(2, -1), (-1, 4)], 
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
                "door_locations": [(1, 0),(0,3)],
                "exit_offsets": [(1, -1), (-1, 3)],  
                "layout": [
                    ['#', '#', '#', 'd', '#'],
                    ['d', 'R', 'R', 'R', '#'],
                    ['#', 'R', 'R', 'R', '#'],
                    ['#', 'R', 'R', 'R', '#'],
                    ['#', '#', '#', '#', '#']
                ]
            }
        }


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
    

    def display_board(self, players):
        '''Displays the board with player tokens only for players in hallways.
        Players in rooms are not shown on the board.
        
        Args:
            players: List of Player objects
        '''
        # Build position map only for players NOT in rooms
        position_to_player = {}
        for player in players:
            if player.current_room is None:  # Only show players in hallways
                pos = player.current_position
                position_to_player[pos] = player
        
        # Display the board
        for row_idx, row in enumerate(self.board):
            colored_row = []
            for col_idx, cell in enumerate(row):
                if (row_idx, col_idx) in position_to_player:
                    player = position_to_player[(row_idx, col_idx)]
                    colored_cell = self.apply_color_to_text(player.symbol, player.color)
                    colored_row.append(colored_cell)
                else:
                    colored_row.append(cell)
            
            print(' '.join(colored_row))
        
        # Display players in rooms at the bottom
        self.display_players_in_rooms(players)
    
    def display_players_in_rooms(self, players):
        '''Displays which players are currently in rooms.
        
        Args:
            players: List of Player objects
        '''
        players_in_rooms = [p for p in players if p.current_room is not None]
        
        if players_in_rooms:
            print("\n" + "=" * 50)
            print("PLAYERS IN ROOMS:")
            print("=" * 50)
            
            # Group players by room
            rooms_dict = {}
            for player in players_in_rooms:
                room = player.current_room
                if room not in rooms_dict:
                    rooms_dict[room] = []
                rooms_dict[room].append(player)
            
            # Display each room and its occupants
            for room_name in sorted(rooms_dict.keys()):
                print(f"\n{room_name}:")
                for player in rooms_dict[room_name]:
                    colored_symbol = self.apply_color_to_text(player.symbol, player.color)
                    print(f"  {colored_symbol} - {player.get_colored_name()}")
            
            print("=" * 50)
    
    def place_player_in_room(self, player, room_name):
        '''Places a player in a room.
        
        Args:
            player: Player object
            room_name: Name of the room (e.g., "Kitchen")
            
        Returns:
            bool: True if successfully placed
        '''
        if room_name in self.rooms:
            # Restore old position to "." if player was in hallway
            old_pos = player.current_position
            if old_pos in self.current_player_positions:
                x, y = old_pos
                self.board[x][y] = '.'
                del self.current_player_positions[old_pos]
            
            player.current_room = room_name
            return True
        return False
    
    def move_player_to_hallway(self, player, position):
        '''Moves a player from a room to a hallway position.
        
        Args:
            player: Player object
            position: (row, col) tuple for new hallway position
        '''
        # If player was in a hallway before, restore that position to "."
        old_pos = player.current_position
        if player.current_room is None and old_pos in self.current_player_positions:
            x, y = old_pos
            self.board[x][y] = '.'
            del self.current_player_positions[old_pos]
        
        # Remove from room
        player.current_room = None
        
        # Update position and place symbol on board
        x, y = position
        player.current_position = position
        self.board[x][y] = player.symbol
        self.current_player_positions[position] = player.name
    
    def move_player(self, player):
        x, y = player.get_player_position()
        
        # Restore old position to "."
        old_pos = player.get_previous_position()
        if player.current_room is None and old_pos is not None and old_pos in self.current_player_positions:
            old_x, old_y = old_pos
            self.board[old_x][old_y] = '.'
            del self.current_player_positions[old_pos]
        
        # Clear room status if they were in one
        player.current_room = None
        
        # Place player at new position
        self.board[x][y] = player.symbol
        self.current_player_positions[player.get_player_position()] = player.name
        
        return True
    
    def get_dimensions(self):
        '''Returns the dimensions of the board as (rows, cols).'''
        return self.board_length, self.board_width
    
    def is_wall(self, position):
        '''Check if the given position is a wall.'''
        row, col = position
        return self.board[row][col] == '#'
    
    def is_occupied(self, position):
        '''Check if the given position is occupied by a player.'''
        return position in self.current_player_positions
    
    def is_door(self, position):
        '''Check if the given position is a door.'''
        row, col = position
        return self.board[row][col] == 'd'
    
    def get_door_positions(self, room_name):
        '''Returns the door positions for a given room.'''
        room_layout = self.get_room_layouts()
        if room_name in room_layout:
            door_offsets = room_layout[room_name]['door_locations']
            room_pos = room_layout[room_name]['position']
            door_positions = [(room_pos[0] + offset[0], room_pos[1] + offset[1]) for offset in door_offsets]
            return door_positions
        return []
            
if __name__ == "__main__":
    board = Board()
    board.display_legend()
    board.display_board()
    
    