"""Maze graph representation and pathfinding."""

from typing import Dict, List, Tuple
import math


class MazeGraph:
    """
    Represents maze as a graph of ArUco markers.
    
    Each marker is a node, free passages are edges.
    Built manually during reconnaissance.
    """

    def __init__(self):
        self.nodes: Dict[int, Dict] = {}
        self.edges: Dict[int, List[int]] = {}
        
        # Example maze layout (3x3 cells, 0.8m spacing)
        # This would be populated from actual measurements
        self._init_example_maze()

    def _init_example_maze(self):
        """Initialize example maze structure."""
        # 3x3 grid of markers (0 to 8)
        positions = {
            0: (0.0, 0.0),     # start (Cheburashka)
            1: (0.8, 0.0),
            2: (1.6, 0.0),
            3: (0.0, 0.8),
            4: (0.8, 0.8),
            5: (1.6, 0.8),
            6: (0.0, 1.6),
            7: (0.8, 1.6),
            8: (1.6, 1.6),     # finish (Cheburashka with orange)
        }
        
        # Define connectivity (which markers are accessible from which)
        # This would be measured on-site during reconnaissance
        connections = {
            0: [1, 3],        # start connects to 1 and 3
            1: [0, 2, 4],     # 1 connects to 0, 2, 4
            2: [1, 5],
            3: [0, 4, 6],
            4: [1, 3, 5, 7],  # middle: connects to 4 neighbors
            5: [2, 4, 8],
            6: [3, 7],
            7: [4, 6, 8],
            8: [5, 7],        # finish
        }
        
        # Build graph
        for marker_id, pos in positions.items():
            self.nodes[marker_id] = {
                'position': pos,
                'is_start': (marker_id == 0),
                'is_finish': (marker_id == 8),
            }
            self.edges[marker_id] = connections.get(marker_id, [])

    def get_position(self, marker_id: int) -> Tuple[float, float]:
        """Get (x, y) position of marker."""
        if marker_id in self.nodes:
            return self.nodes[marker_id]['position']
        return None

    def get_neighbors(self, marker_id: int) -> List[int]:
        """Get list of accessible neighboring markers."""
        return self.edges.get(marker_id, [])

    def distance(self, from_id: int, to_id: int) -> float:
        """Calculate distance between two markers."""
        pos1 = self.get_position(from_id)
        pos2 = self.get_position(to_id)
        if pos1 and pos2:
            return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
        return float('inf')

    def find_path_astar(self, start_id: int, goal_id: int) -> List[int]:
        """
        A* pathfinding from start to goal marker.
        
        Returns list of marker IDs to follow.
        """
        open_set = [start_id]
        came_from = {}
        g_score = {node: float('inf') for node in self.nodes}
        g_score[start_id] = 0
        f_score = {node: float('inf') for node in self.nodes}
        f_score[start_id] = self._heuristic(start_id, goal_id)
        
        while open_set:
            current = min(open_set, key=lambda x: f_score[x])
            
            if current == goal_id:
                return self._reconstruct_path(came_from, current)
            
            open_set.remove(current)
            
            for neighbor in self.get_neighbors(current):
                tentative_g = g_score[current] + self.distance(current, neighbor)
                
                if tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = g_score[neighbor] + self._heuristic(neighbor, goal_id)
                    
                    if neighbor not in open_set:
                        open_set.append(neighbor)
        
        return []  # No path found

    def _heuristic(self, from_id: int, to_id: int) -> float:
        """Heuristic for A*: straight line distance."""
        return self.distance(from_id, to_id)

    def _reconstruct_path(self, came_from: Dict, current: int) -> List[int]:
        """Reconstruct path from A* search."""
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.insert(0, current)
        return path

    def add_marker(self, marker_id: int, position: Tuple[float, float],
                   neighbors: List[int] = None):
        """Dynamically add marker to graph (for on-site discovery)."""
        self.nodes[marker_id] = {
            'position': position,
            'is_start': False,
            'is_finish': False,
        }
        self.edges[marker_id] = neighbors or []
