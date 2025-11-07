import random
try:
    from app.rules import Rules
    from app.board import Board
except ImportError:
    from rules import Rules
    from board import Board

class Cluedo:
    '''Main class to run the Cluedo game.'''
    def __init__(self):
        self.rules = Rules()
        self.board = Board()

    
    def generate_solution(self):
        '''Generates a random solution by selecting one suspect, one weapon, and one room.'''
        suspects = self.rules.get_suspects()
        weapons = self.rules.get_weapons()
        rooms = self.rules.get_rooms()
        
        # Randomly select one from each category
        solution_suspect = random.choice(suspects)
        solution_weapon = random.choice(weapons)
        solution_room = random.choice(rooms)
        
        solution = {
            "suspect": solution_suspect,
            "weapon": solution_weapon,
            "room": solution_room
        }
        
        return solution
    
    def display_solution(self, solution):
        '''Displays the solution in a formatted way.'''
        print("\n=== CLUEDO SOLUTION ===")
        print(f"Suspect: {solution['suspect']}")
        print(f"Weapon: {solution['weapon']}")
        print(f"Room: {solution['room']}")
        print("=======================\n")
        
    def get_solution_summary(self, solution):
        '''Returns a formatted string summary of the solution.'''
        return f"{solution['suspect']} with the {solution['weapon']} in the {solution['room']}"


if __name__ == "__main__":
    # Test the solution generation
    game = Cluedo()
    game.board.display_legend()
    game.board.display_board()
    


    print("\nGenerating random Cluedo solutions:")
    print("-" * 40)
    
    # Generate and display multiple solutions to show randomness
    for i in range(3):
        solution = game.generate_solution()
        print(f"Solution {i+1}: {game.get_solution_summary(solution)}")
    
    # Display one solution in detail
    print()
    final_solution = game.generate_solution()
    game.display_solution(final_solution)