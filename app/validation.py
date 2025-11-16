
from app import cluedo
from app.player import Player


try:
    from app.exceptions import InvalidActionException, InvalidMoveException
    from app.config import Config
    from app.board import Board
except ImportError:
    from exceptions import InvalidActionException, InvalidMoveException

class validation:
    
    @staticmethod
    def validate_position(position, board: 'Board', previous_moves: list) -> bool:
        '''Validate if the given position is within the board boundaries.'''
        rows, cols = board.get_dimensions()
        row, col = position
        if not (0 <= row < rows and 0 <= col < cols):
            raise InvalidMoveException(f"Position {position} is out of board boundaries.")
        if board.is_wall(position):
            raise InvalidMoveException(f"Position {position} is a wall and cannot be moved to.")
        if board.is_occupied(position):
            raise InvalidMoveException(f"Position {position} is already occupied by another player.")
        if board.is_door(position):
            raise InvalidMoveException(f"Position {position} is a door and cannot be moved to directly.")
        if position in previous_moves:
            raise InvalidMoveException(f"Position {position} has already been visited in the last move.")
        return True
    
    @staticmethod
    def validate_enter_room(player: 'Player', room_name: str, board: 'Board') -> bool:
        '''Validate if the player can enter the specified room.'''
        room_layouts = board.get_room_layouts()
        room_layout = room_layouts.get(room_name)
        if not room_layout:
            raise InvalidActionException(f"Room {room_name} is not valid.")
        
        # Get player's current position
        player_row, player_col = player.get_previous_position()
        
        # Check if player is next to any door of this room
        for door_pos in room_layout['door_locations']:
            door_row = room_layout['position'][0] + door_pos[0]
            door_col = room_layout['position'][1] + door_pos[1]
            
            # Check if player is adjacent to door (up, down, left, or right)
            if (abs(player_row - door_row) == 1 and player_col == door_col) or \
               (abs(player_col - door_col) == 1 and player_row == door_row):
                return True
        
        raise InvalidActionException(f"Player {player.name} is not next to a door of the {room_name}; they cannot enter.")
        