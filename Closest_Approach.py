import copy
from typing import List, Tuple, Set
from collections import deque

class MiningOptimizer:
    def __init__(self, grid: List[List[int]]):
        self.original_grid = grid
        self.rows = len(grid)
        self.cols = len(grid[0]) if grid else 0
        self.best_solution = None
        self.best_ore_count = 0
        self.best_drill_count = float('inf')
    
    def is_valid_drill_position(self, row: int, col: int, placed_drills: Set[Tuple[int, int]]) -> bool:
        """Check if a 2x2 drill can be placed at position (row, col)"""
        if row + 1 >= self.rows or col + 1 >= self.cols:
            return False
        
        # Check for overlaps with existing drills
        for r in range(row, row + 2):
            for c in range(col, col + 2):
                if (r, c) in placed_drills:
                    return False
        return True
    
    def count_ore_coverage(self, row: int, col: int) -> int:
        """Count how much ore a drill at (row, col) would cover"""
        ore_count = 0
        for r in range(row, row + 2):
            for c in range(col, col + 2):
                if self.original_grid[r][c] == 1:
                    ore_count += 1
        return ore_count
    
    def get_drill_positions(self) -> List[Tuple[int, int, int]]:
        """Get all possible drill positions with their ore coverage"""
        positions = []
        for row in range(self.rows - 1):
            for col in range(self.cols - 1):
                ore_coverage = self.count_ore_coverage(row, col)
                if ore_coverage > 0:  # Only consider positions that cover some ore
                    positions.append((row, col, ore_coverage))
        
        # Sort by ore coverage (descending) to prioritize high-value positions
        positions.sort(key=lambda x: x[2], reverse=True)
        return positions
    
    def find_optimal_drill_placement(self) -> List[Tuple[int, int]]:
        """Find the optimal drill placement using greedy approach"""
        positions = self.get_drill_positions()
        placed_drills = set()
        selected_drills = []
        
        # Greedy selection: pick drills that don't overlap and cover the most ore
        for row, col, ore_coverage in positions:
            if self.is_valid_drill_position(row, col, placed_drills):
                # Add all cells covered by this drill to placed_drills
                for r in range(row, row + 2):
                    for c in range(col, col + 2):
                        placed_drills.add((r, c))
                selected_drills.append((row, col))
        
        return selected_drills
    
    def find_conveyor_path(self, drills: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """Find conveyor belts that are directly adjacent to all drill sides for ore collection"""
        if len(drills) < 1:
            return []
        
        conveyor_cells = set()
        
        # For each drill, add conveyor belts on all four sides where possible
        for drill_row, drill_col in drills:
            # Add conveyors around the 2x2 drill
            
            # Top side of drill (row above)
            if drill_row > 0:
                for c in range(drill_col, drill_col + 2):
                    conveyor_cells.add((drill_row - 1, c))
            
            # Bottom side of drill (row below)
            if drill_row + 2 < self.rows:
                for c in range(drill_col, drill_col + 2):
                    conveyor_cells.add((drill_row + 2, c))
            
            # Left side of drill (column to the left)
            if drill_col > 0:
                for r in range(drill_row, drill_row + 2):
                    conveyor_cells.add((r, drill_col - 1))
            
            # Right side of drill (column to the right)
            if drill_col + 2 < self.cols:
                for r in range(drill_row, drill_row + 2):
                    conveyor_cells.add((r, drill_col + 2))
        
        # Now connect all conveyor segments to form a network
        conveyor_list = list(conveyor_cells)
        
        # Add connecting paths between isolated conveyor segments
        connected_conveyors = self.connect_conveyor_segments(conveyor_list, drills)
        conveyor_cells.update(connected_conveyors)
        
        return list(conveyor_cells)
    
    def connect_conveyor_segments(self, conveyor_cells: List[Tuple[int, int]], drills: List[Tuple[int, int]]) -> Set[Tuple[int, int]]:
        """Connect isolated conveyor segments to form a continuous network"""
        additional_conveyors = set()
        
        if len(drills) < 2:
            return additional_conveyors
        
        # Find the bounding box of all drills
        min_row = min(drill[0] for drill in drills)
        max_row = max(drill[0] + 1 for drill in drills)
        min_col = min(drill[1] for drill in drills)
        max_col = max(drill[1] + 1 for drill in drills)
        
        # Create horizontal connections at regular intervals
        connection_rows = [min_row - 1, max_row + 1]
        for conn_row in connection_rows:
            if 0 <= conn_row < self.rows:
                for col in range(max(0, min_col - 1), min(self.cols, max_col + 2)):
                    # Only add if it doesn't conflict with drills
                    if not self.is_cell_occupied_by_drill(conn_row, col, drills):
                        additional_conveyors.add((conn_row, col))
        
        # Create vertical connections at regular intervals
        connection_cols = [min_col - 1, max_col + 1]
        for conn_col in connection_cols:
            if 0 <= conn_col < self.cols:
                for row in range(max(0, min_row - 1), min(self.rows, max_row + 2)):
                    # Only add if it doesn't conflict with drills
                    if not self.is_cell_occupied_by_drill(row, conn_col, drills):
                        additional_conveyors.add((row, conn_col))
        
        return additional_conveyors
    
    def is_cell_occupied_by_drill(self, row: int, col: int, drills: List[Tuple[int, int]]) -> bool:
        """Check if a cell is occupied by any drill"""
        for drill_row, drill_col in drills:
            if (drill_row <= row < drill_row + 2 and 
                drill_col <= col < drill_col + 2):
                return True
        return False
    
    def validate_drill_conveyor_connection(self, drills: List[Tuple[int, int]], conveyor_cells: List[Tuple[int, int]]) -> bool:
        """Validate that every drill has at least one adjacent conveyor belt"""
        conveyor_set = set(conveyor_cells)
        
        for drill_row, drill_col in drills:
            has_connection = False
            
            # Check all four sides of the 2x2 drill
            # Top side
            for c in range(drill_col, drill_col + 2):
                if (drill_row - 1, c) in conveyor_set:
                    has_connection = True
                    break
            
            if not has_connection:
                # Bottom side
                for c in range(drill_col, drill_col + 2):
                    if (drill_row + 2, c) in conveyor_set:
                        has_connection = True
                        break
            
            if not has_connection:
                # Left side
                for r in range(drill_row, drill_row + 2):
                    if (r, drill_col - 1) in conveyor_set:
                        has_connection = True
                        break
            
            if not has_connection:
                # Right side
                for r in range(drill_row, drill_row + 2):
                    if (r, drill_col + 2) in conveyor_set:
                        has_connection = True
                        break
            
            if not has_connection:
                print(f"WARNING: Drill at ({drill_row}, {drill_col}) has no adjacent conveyor belt!")
                return False
        
        return True
    
    def calculate_collectible_ore(self, drills: List[Tuple[int, int]], conveyor_path: List[Tuple[int, int]]) -> int:
        """Calculate ore that can actually be collected (drills must be adjacent to conveyors)"""
        conveyor_set = set(conveyor_path)
        total_collectible_ore = 0
        
        for drill_row, drill_col in drills:
            # Check if this drill is connected to any conveyor
            drill_connected = False
            
            # Check all four sides of the drill
            adjacent_positions = [
                # Top side
                [(drill_row - 1, c) for c in range(drill_col, drill_col + 2)],
                # Bottom side  
                [(drill_row + 2, c) for c in range(drill_col, drill_col + 2)],
                # Left side
                [(r, drill_col - 1) for r in range(drill_row, drill_row + 2)],
                # Right side
                [(r, drill_col + 2) for r in range(drill_row, drill_row + 2)]
            ]
            
            for side_positions in adjacent_positions:
                if any(pos in conveyor_set for pos in side_positions):
                    drill_connected = True
                    break
            
            # Only count ore from connected drills
            if drill_connected:
                for r in range(drill_row, drill_row + 2):
                    for c in range(drill_col, drill_col + 2):
                        if 0 <= r < self.rows and 0 <= c < self.cols:
                            if self.original_grid[r][c] == 1:
                                total_collectible_ore += 1
            else:
                print(f"WARNING: Drill at ({drill_row}, {drill_col}) is not connected - ore will be wasted!")
        
        return total_collectible_ore
    
    def create_solution_grid(self, drills: List[Tuple[int, int]], conveyor_path: List[Tuple[int, int]]) -> List[List[str]]:
        """Create the final grid with drills and conveyor belts"""
        # Convert original grid to string grid
        solution = [[str(cell) for cell in row] for row in self.original_grid]
        
        # Place conveyor belts first (so drills can overwrite if needed)
        for row, col in conveyor_path:
            if 0 <= row < self.rows and 0 <= col < self.cols:
                solution[row][col] = 'c'
        
        # Place drills (2x2 regions) - drills overwrite conveyors if there's overlap
        for drill_row, drill_col in drills:
            for r in range(drill_row, drill_row + 2):
                for c in range(drill_col, drill_col + 2):
                    if 0 <= r < self.rows and 0 <= c < self.cols:
                        solution[r][c] = 'd'
        
        return solution
    
    def solve(self) -> Tuple[List[List[str]], int, int]:
        """Solve the mining optimization problem"""
        # Find optimal drill placement
        drills = self.find_optimal_drill_placement()
        
        if not drills:
            return [[str(cell) for cell in row] for row in self.original_grid], 0, 0
        
        # Find conveyor path to connect all drills
        conveyor_path = self.find_conveyor_path(drills)
        
        # Validate that all drills are connected to conveyors
        if not self.validate_drill_conveyor_connection(drills, conveyor_path):
            print("ERROR: Not all drills are properly connected to conveyors!")
        
        # Create solution grid
        solution_grid = self.create_solution_grid(drills, conveyor_path)
        
        # Calculate ore coverage (only count ore that can actually be collected)
        total_ore_covered = self.calculate_collectible_ore(drills, conveyor_path)
        
        return solution_grid, len(drills), total_ore_covered

def print_grid(grid: List[List[str]], title: str = "Grid"):
    """Helper function to print a grid nicely"""
    print(f"\n{title}:")
    for row in grid:
        print(' '.join(row))

def solve_mining_problem(grid: List[List[int]]) -> List[List[str]]:
    """Main function to solve the mining problem"""
    optimizer = MiningOptimizer(grid)
    solution, num_drills, ore_covered = optimizer.solve()
    
    print(f"Solution found:")
    print(f"Number of drills: {num_drills}")
    print(f"Collectible ore: {ore_covered}")
    
    # Count total ore in grid for comparison
    total_ore = sum(sum(1 for cell in row if cell == 1) for row in grid)
    efficiency = (ore_covered / total_ore * 100) if total_ore > 0 else 0
    print(f"Total ore in grid: {total_ore}")
    print(f"Collection efficiency: {efficiency:.1f}%")
    
    print_grid([[str(cell) for cell in row] for row in grid], "Original Grid")
    print_grid(solution, "Solution Grid")
    print("Legend: 0=stone, 1=ore, d=drill, c=conveyor")
    
    return solution

def generate_random_ore_grid(size: int = 20, ore_probability: float = 0.3) -> List[List[int]]:
    """Generate a random grid with stone borders and random ore distribution"""
    import random
    
    grid = [[0 for _ in range(size)] for _ in range(size)]
    
    # Fill the inner area (excluding 5-block border) with random ore
    for row in range(5, size - 5):
        for col in range(5, size - 5):
            if random.random() < ore_probability:
                grid[row][col] = 1
    
    return grid

def create_ore_clusters(size: int = 20, num_clusters: int = 5) -> List[List[int]]:
    """Create a grid with clustered ore formations"""
    import random
    
    grid = [[0 for _ in range(size)] for _ in range(size)]
    
    # Create ore clusters
    for _ in range(num_clusters):
        # Random center for cluster (within the inner area)
        center_row = random.randint(6, size - 7)
        center_col = random.randint(6, size - 7)
        cluster_size = random.randint(3, 6)
        
        # Create cluster around center
        for row in range(max(5, center_row - cluster_size), min(size - 5, center_row + cluster_size)):
            for col in range(max(5, center_col - cluster_size), min(size - 5, center_col + cluster_size)):
                distance = abs(row - center_row) + abs(col - center_col)
                if distance <= cluster_size and random.random() < 0.7:
                    grid[row][col] = 1
    
    return grid

def create_ore_veins(size: int = 20) -> List[List[int]]:
    """Create a grid with ore vein patterns"""
    import random
    
    grid = [[0 for _ in range(size)] for _ in range(size)]
    
    # Create horizontal veins
    for i in range(3):
        vein_row = random.randint(7, size - 8)
        vein_start = random.randint(6, 8)
        vein_end = random.randint(size - 8, size - 6)
        vein_thickness = random.randint(2, 4)
        
        for row in range(vein_row, min(size - 5, vein_row + vein_thickness)):
            for col in range(vein_start, vein_end):
                if random.random() < 0.8:
                    grid[row][col] = 1
    
    # Create vertical veins
    for i in range(2):
        vein_col = random.randint(8, size - 9)
        vein_start = random.randint(6, 8)
        vein_end = random.randint(size - 8, size - 6)
        vein_thickness = random.randint(2, 3)
        
        for col in range(vein_col, min(size - 5, vein_col + vein_thickness)):
            for row in range(vein_start, vein_end):
                if random.random() < 0.8:
                    grid[row][col] = 1
    
    return grid

# Example usage and testing
if __name__ == "__main__":
    import random
    random.seed(42)  # For reproducible results
    
    # Test case 1: Random scattered ore in 20x20 grid
    print("=" * 80)
    print("TEST CASE 1: 20x20 Grid with Random Scattered Ore")
    test_grid_1 = generate_random_ore_grid(20, 0.25)
    solution_1 = solve_mining_problem(test_grid_1)
    
    # Test case 2: Clustered ore formations
    print("\n" + "=" * 80)
    print("TEST CASE 2: 20x20 Grid with Clustered Ore Formations")
    test_grid_2 = create_ore_clusters(20, 4)
    solution_2 = solve_mining_problem(test_grid_2)
    
    # Test case 3: Ore vein patterns
    print("\n" + "=" * 80)
    print("TEST CASE 3: 20x20 Grid with Ore Vein Patterns")
    test_grid_3 = create_ore_veins(20)
    solution_3 = solve_mining_problem(test_grid_3)
    
    # Test case 4: Large concentrated ore deposit
    print("\n" + "=" * 80)
    print("TEST CASE 4: 20x20 Grid with Large Concentrated Deposit")
    test_grid_4 = [[0 for _ in range(20)] for _ in range(20)]
    # Create a large ore deposit in the center
    for row in range(8, 15):
        for col in range(7, 16):
            if random.random() < 0.85:
                test_grid_4[row][col] = 1
    solution_4 = solve_mining_problem(test_grid_4)
