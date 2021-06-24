class myObject(tuple):
    def __init__(self, info):
        super.__init__(info)
        self.name = self[0]
        self.parent = self[1]
        self.children = self[2]

class MyList(dict):
    """
    keep track of parents
    be able to iterate by dfs
    
    """
    def __init__(self, node):
        super().__init__()
        self.root_node = node
        self[node] = (None, None, [])
        self.node = node
        self.queue = [node]
    
    def append(self, name, parent, position):
        """name -> name of block
           parent -> name of parent block
           position -> euclidean coordinates of block
        """
        self[parent][2].append(name)
        self[name] = (parent, position, [])
        return None
    
    def branch(self, node):
        """Returns the branch of the tree beginning at node.
        """
        self.queue = [node]
        return [x for x in self]
    
    def section(self, node):
        """Deprecated for readability
        """
        return self.branch(node)
    
    def __delitem__(self, item):
        parent = self[item][0]
        self[parent][2].remove(item)
        super().__delitem__(item)        
    
    def __iter__(self):
        return self
    
    def __next__(self):
        """Iterates through as a breadth first search.
        """
        if self.queue and self.queue[0] == self.node:
            current_object = self.queue.pop(0)
            self.queue.extend(self[current_object][2])
        if not self.queue:
            self.queue = [self.node]
            raise StopIteration
        else:
            current_object = self.queue.pop(0)
            try:
                self.queue.extend(self[current_object][2])
            except KeyError as err:
                print(err)
                [print(x) for x in self.items()]
                print(self.queue)
                raise KeyError
            return current_object, self[current_object][0], self[current_object][1]


def main():
    node = 'base_node'
    a = MyList(node)
    a.append('node1', 'base_node', (0, 1))
    a.append('node2', 'base_node', (1, 1))
    a.append('node3', 'node1', (2, 1))
    for item in a:
        print(item)
    print()
    for item in a.section('node1'):
        print(item)
    print()
    for item in a.section('node2'):
        print(item)
                


if __name__ == "__main__":
    main()