
from app import cluedo


try:
    from app.exceptions import InvalidActionException, InvalidMoveException
    from app.config import Config
    from app.board import Board
except ImportError:
    from exceptions import InvalidActionException, InvalidMoveException

class validation:
    
    @staticmethod
    def validate_position(position, board: 'Board') -> bool:
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
        return True
        