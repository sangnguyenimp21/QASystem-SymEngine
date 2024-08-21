class GraphNode:
    def __init__(self, label=None, state=None, current=None, neighbor=None, type=None, key=None):
        self.label = label
        self.state = state
        self.current_node = current
        self.neighbor_node = neighbor
        self.type = type
        self.key = key

    def __repr__(self):
        return f"Element(label={self.label}, state={self.state}, current_node={self.current_node}, neighbor_node={self.neighbor_node}, type={self.type}, key={self.key})"
