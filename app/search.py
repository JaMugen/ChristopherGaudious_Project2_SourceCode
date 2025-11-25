import queue
from typing import List, Optional, Tuple
from app.validation import validation
from app.exceptions import InvalidMoveException


class Node:
    def __init__(self, state, parent=None, action=None):
        self.state = state
        self.parent = parent
        self.action = action  # Action taken to reach this state


def get_possible_actions(state: Tuple[Optional[str], Optional[Tuple[int, int]]], 
                        game) -> List[Tuple[Tuple[Optional[str], Optional[Tuple[int, int]]], str]]:
    """Generate all possible (next_state, action) pairs from current state.
    
    Args:
        state: Current state as (current_room, current_position)
        game: Game instance with board and rules
    
    Returns:
        List of tuples: [(next_state, action_string), ...]
    """
    current_room, current_pos = state
    possible_actions = []
    
    secret_passages = game.rules.get_secret_passages()
    room_layouts = game.board.get_room_layouts()
    
    # 1. If in a room with secret passage, can use it
    if current_room and current_room in secret_passages:
        dest_room = secret_passages[current_room]
        next_state = (dest_room, None)
        possible_actions.append((next_state, 'secret'))
    
    # 2. If in a room, can exit to hallway
    if current_room:
        exit_positions = game.board.get_exit_positions(current_room)
        for exit_pos in exit_positions:
            next_state = (None, exit_pos)
            # Include room name and exit position in action
            possible_actions.append((next_state, f'exit {current_room} {exit_pos[0]} {exit_pos[1]}'))
    
    # 3. If in hallway, can move to adjacent cells or enter rooms
    if current_room is None and current_pos is not None:
        row, col = current_pos
        
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            new_row, new_col = row + dr, col + dc
            new_pos = (new_row, new_col)


            try:
                validation.validate_position(new_pos, game.board, [], allow_doors=True, allow_occupied=False)
            except InvalidMoveException:
             
                continue
            
            cell = game.board.board[new_row][new_col]

            if cell == '.':
                next_state = (None, new_pos)
       
                possible_actions.append((next_state, f'move {new_row} {new_col}'))
            
            # Can enter room through door
            elif cell == 'd':
                # Find which room this door belongs to
                for room_name in room_layouts.keys():
                    door_positions = game.board.get_door_locations(room_name)
                    if new_pos in door_positions:
                        next_state = (room_name, None)
                        possible_actions.append((next_state, f'enter {room_name}'))
                        break
                
    
    return possible_actions


def expand_state(current_node: Node, visited: set, q: queue.Queue, game) -> None:
    """Expand current state by adding all unvisited successor states to queue.
    """
    possible_actions = get_possible_actions(current_node.state, game)
    
    for next_state, action in possible_actions:
        if next_state not in visited:
            visited.add(next_state)
            q.put(Node(next_state, current_node, action))


def BFS(start_room: Optional[str], start_position: Optional[Tuple[int, int]], 
                      target_room: str, game) -> Optional[List[str]]:
    """Breadth-First Search to find path of actions to reach target room.
    
    Args:
        start_room: Current room name (None if in hallway)
        start_position: Current (row, col) position (None if in room)
        target_room: Target room name to reach
        game: Game instance with board and rules
    
    Returns:
        List of action strings: ['exit', 'move', 'move', 'enter Kitchen'].
    """
    visited = set()
    q = queue.Queue()
    
    # State: (current_room, current_position)
    start_state = (start_room, start_position)
    q.put(Node(start_state, action=None))
    visited.add(start_state)
    
    while not q.empty():
        current_node = q.get()
        current_room, current_pos = current_node.state
        

        if current_room == target_room:
            temp_actions = []
            node = current_node
            while node.parent is not None:
                if node.action:
                    temp_actions.append(node.action)
                node = node.parent
            actions = []
            while temp_actions:
                actions.append(temp_actions.pop())
            return actions
   
        expand_state(current_node, visited, q, game)
    

    return None 