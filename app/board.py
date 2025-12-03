from app.rules import Rules
from app.config import Config
from colorama import init, Style

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
    BAR_LENGTH = 50

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
        self.weapons_rooms = config.get_weapon_rooms()
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

    def display_room_layout(self, room_name):
        '''Displays the room layout with numbered doors.
        
        Args:
            room_name: Name of the room to display
        '''
        room_layouts = self.get_room_layouts()
        room_layout = room_layouts.get(room_name)
        
        if not room_layout:
            return
        
        print(f"\n{room_name} Layout:")
        door_locations = room_layout['door_locations']
        layout = room_layout['layout']
        
        # Create a copy of the layout with numbered doors
        for row_idx, row in enumerate(layout):
            row_str = ""
            for col_idx, cell in enumerate(row):
                # Check if this position is a door
                door_number = None
                for idx, door_pos in enumerate(door_locations):
                    if (row_idx, col_idx) == door_pos:
                        door_number = idx + 1
                        break
                
                if door_number:
                    row_str += str(door_number) + " "
                else:
                    row_str += cell + " "
            print(row_str)
    
    def get_door_locations(self, room_name):
        '''Returns the door locations for a given room.
        
        Args:
            room_name: Name of the room
            
        Returns:
            list: List of door location tuples, or empty list if room not found
        '''
        room_layouts = self.get_room_layouts()
        room_layout = room_layouts.get(room_name)
        
        if room_layout:
            return room_layout['door_locations']
        return []
    
    def get_room_layout(self, room_name):
        '''Returns the layout information for a given room.
        
        Args:
            room_name: Name of the room
            
        Returns:
            dict: Room layout dictionary with position, size, door_locations, exit_offsets, and layout keys
                  Returns None if room not found
        '''
        room_layouts = self.get_room_layouts()
        return room_layouts.get(room_name)

    def get_exit_positions(self, room_name):
        '''Returns the absolute board positions where a player exits when leaving a room.
        
        Args:
            room_name: Name of the room
            
        Returns:
            list: List of (row, col) tuples representing exit positions on the board.
                  Returns empty list if room not found.
        '''
        room_layout = self.get_room_layout(room_name)
        if not room_layout:
            return []
        
        exit_offsets = room_layout.get('exit_offsets', [])
        room_pos = room_layout['position']
        
        exit_positions = []
        for offset in exit_offsets:
            exit_row = room_pos[0] + offset[0]
            exit_col = room_pos[1] + offset[1]
            exit_positions.append((exit_row, exit_col))
        
        return exit_positions
    
    def get_door_locations(self, room_name):
        '''Returns the door locations for a given room.'''
        room_layout = self.get_room_layout(room_name)
        if room_layout:
            door_offsets = room_layout['door_locations']
            room_pos = room_layout['position']
            door_positions = []
            for offset in door_offsets:
                door_row = room_pos[0] + offset[0]
                door_col = room_pos[1] + offset[1]
                door_positions.append((door_row, door_col))
            return door_positions
        return []

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
        Billiard_Room_Symbol = self.get_room_symbol("Billiard Room")
        Hall = self.get_room_symbol("Hall")
        Kitchen = self.get_room_symbol("Kitchen")
        Ballroom = self.get_room_symbol("Ballroom")
        Conservatory = self.get_room_symbol("Conservatory")
        Dining_Room = self.get_room_symbol("Dining Room")
        Lounge = self.get_room_symbol("Lounge")
        Study = self.get_room_symbol("Study")
        Library = self.get_room_symbol("Library")

        return {
            "Kitchen": {
                "position": (0, 0),  # Top-left corner position on board
                "size": (5, 6),
                "door_locations": [(4, 4)],      # Length x Width
                "exit_offsets": [(5, 4)],  # Where player ends up when exiting through each door
                "layout": [
                    ['#', '#', '#', '#', '#', '#'],
                    ['#', Kitchen, Kitchen, Kitchen, Kitchen, '#'],
                    ['#', Kitchen, Kitchen, Kitchen, Kitchen, '#'],
                    ['#', Kitchen, Kitchen, Kitchen, Kitchen, '#'],
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
                    ['#', '#', Ballroom, Ballroom, Ballroom, '#', '#'],
                    ['#', Ballroom, Ballroom, Ballroom, Ballroom, Ballroom, '#'],
                    ['#', Ballroom, Ballroom, Ballroom, Ballroom, Ballroom, '#'],
                    ['#', Ballroom, Ballroom, Ballroom, Ballroom, Ballroom, '#'],
                    ['d', Ballroom, Ballroom, Ballroom, Ballroom, Ballroom, 'd'],
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
                    ['#', Conservatory, Conservatory, Conservatory, Conservatory, '#'],
                    ['d', Conservatory, Conservatory, Conservatory, Conservatory, '#'],
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
                    ['#',Dining_Room, Dining_Room, Dining_Room, Dining_Room, '#', '#', '#'],
                    ['#', Dining_Room, Dining_Room, Dining_Room, Dining_Room, Dining_Room, Dining_Room, '#'],
                    ['#', Dining_Room, Dining_Room, Dining_Room, Dining_Room, Dining_Room, Dining_Room, '#'],
                    ['#', Dining_Room, Dining_Room, Dining_Room, Dining_Room, Dining_Room, Dining_Room, 'd'],
                    ['#', Dining_Room, Dining_Room, Dining_Room, Dining_Room, Dining_Room, Dining_Room, '#'],
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
                    ['#', Lounge, Lounge, Lounge, Lounge, Lounge, '#'],
                    ['#', Lounge, Lounge, Lounge, Lounge, Lounge, '#'],
                    ['#', Lounge, Lounge, Lounge, Lounge, Lounge, '#'],
                    ['#','#', '#', '#', '#', '#', '#']
                ]
            },
            "Hall": {
                "position": (16, 9),
                "size": (6, 6),
                "door_locations": [(0, 2), (0, 3), (3, 5)],
                "exit_offsets": [(-1, 2), (-1, 3), (3, 6)],  
                "layout": [
                    ['#','#','d', 'd','#','#'],
                    ['#', Hall, Hall, Hall, Hall, '#'],
                    ['#', Hall, Hall, Hall, Hall, '#'],
                    ['#', Hall, Hall, Hall, Hall, 'd'],
                    ['#', Hall, Hall, Hall, Hall, '#'],
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
                    ['#', Study, Study, Study, Study, '#'],
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
                    ['#', Library, Library, Library, Library, '#'],
                    ['d', Library, Library, Library, Library, '#'],
                    ['#', Library, Library, Library, Library, '#'],
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
                    ['d', Billiard_Room_Symbol, Billiard_Room_Symbol, Billiard_Room_Symbol, '#'],
                    ['#', Billiard_Room_Symbol, Billiard_Room_Symbol, Billiard_Room_Symbol, '#'],
                    ['#', Billiard_Room_Symbol, Billiard_Room_Symbol, Billiard_Room_Symbol, '#'],
                    ['#', '#', '#', '#', '#']
                ]
            }
        }


    def display_board(self, players):
        '''Displays the board with player tokens only for players in hallways.
        Players in rooms are not shown on the board.
        
        Args:
            players: List of Player objects
        '''
        # Display weapons in rooms
        self.display_weapons_in_rooms()

        # Build position map only for players NOT in rooms
        position_to_player = {}
        for player in players:
            if player.get_current_room() is None:  # Only show players in hallways
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
        players_in_rooms = []
        for p in players:
            if p.get_current_room() is not None:
                players_in_rooms.append(p)
        
        if players_in_rooms:
            print("\n" + "=" * self.BAR_LENGTH)
            print("PLAYERS IN ROOMS:".center(self.BAR_LENGTH))
            print("=" * self.BAR_LENGTH)
            
            # Group players by room
            rooms_dict = {}
            for player in players_in_rooms:
                room = player.get_current_room()
                if room not in rooms_dict:
                    rooms_dict[room] = []
                rooms_dict[room].append(player)
            
            # Display each room and its occupants
            for room_name in sorted(rooms_dict.keys()):
                print(f"\n{room_name}:")
                for player in rooms_dict[room_name]:
                    print(f"  {player.get_colored_symbol()} - {player.get_colored_name()}")
            
            print("=" * self.BAR_LENGTH)
    
    def display_weapons_in_rooms(self):
        '''Displays which weapons are currently in rooms.'''
        print("\n" + "=" * self.BAR_LENGTH)
        print("WEAPONS IN ROOMS:".center(self.BAR_LENGTH))
        print("=" * self.BAR_LENGTH)
        
        # Group weapons by room
        rooms_dict = {}
        for weapon, room in self.weapons_rooms.items():
            if room not in rooms_dict:
                rooms_dict[room] = []
            rooms_dict[room].append(weapon)
        
        # Display each room and its weapons
        for room_name in sorted(rooms_dict.keys()):
            print(f"\n{room_name}:")
            for weapon in rooms_dict[room_name]:
                print(f"  {weapon}")
        
        print("=" * self.BAR_LENGTH)
    
    def place_weapon_in_room(self, weapon, room_name):
        '''Places a weapon in a specified room.
        
        Args:
            weapon: Name of the weapon (e.g., "Candlestick")
            room_name: Name of the room (e.g., "Kitchen")
        '''
        self.weapons_rooms[weapon] = room_name

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
            # Use previous_position since current_position is already set to None by enter_room()
            old_pos = player.get_previous_position()
            if old_pos is not None and old_pos in self.current_player_positions:
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
    
    