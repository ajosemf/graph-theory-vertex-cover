from itertools import chain, combinations
import networkx as nx
import func_timeout
import tracemalloc


class VertexCover(object):
    
    
    def __init__(self, MEMORY_LIMIT=1000000000, TIME_LIMIT=120):
        self._MEMORY_LIMIT = MEMORY_LIMIT
        self._TIME_LIMIT = TIME_LIMIT
        self.nodes = None
        self.edges = None
        self.adjacency_matrix = None
        
        
    def set_graph(self, nodes, edges):
        self.nodes = nodes
        self.edges = edges
        self.adjacency_matrix = self._build_adjacency_matrix()
        self.graph_length = len(self.nodes)
        
        
    def get_cover(self, k, method='brute_force'):
        assert method in ['brute_force', 'greedy'], 'Invalid method'
        strategy = self._brute_force_cover if method == 'brute_force' else self._greedy_cover
        print(f'Running {method} strategy with k={k}...')
        try:
            response = func_timeout.func_timeout(
                self._TIME_LIMIT, strategy, args=[k]
            )
            return response
        except func_timeout.FunctionTimedOut:
            print(f'Exceeded time limit! Time Limit: {self._TIME_LIMIT} seconds')
    
    
    def _build_adjacency_matrix(self):
        size = len(self.nodes)
        adjacency_matrix = [[0]*size for i in range(size)]
        for edge in self.edges:
            adjacency_matrix[edge[0]][edge[1]] += 1
            adjacency_matrix[edge[1]][edge[0]] += 1
        return adjacency_matrix


    def _powerset(self, iterable):
        """Return the powerset of an iterable as a list of lists.
        
        Args:
            iterable (list): list of elements to take the powerset of
            
        Example:
            >>> for x in powerset([1, 2, 3]):
            >>>    print(x)
            ()
            (1,)
            (2,)
            (3,)
            (1, 2)
            (1, 3)
            (2, 3)
            (1, 2, 3)

        Returns:
            iterator: iterator over the powerset of the input list
        """
        s = list(iterable)
        return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))


    def _subsets(self, iterable, lenght=None):
        K = lenght or len(iterable)
        for x in self._powerset(iterable):
            if len(x) > K:
                break
            yield x


    def _brute_force_cover(self, k):
        tracemalloc.start()
        for subset in self._subsets(self.nodes, k):
            if tracemalloc.get_traced_memory()[0] > self._MEMORY_LIMIT:
                print(f'Memory limit of {self._MEMORY_LIMIT} bytes exceeded!')
                tracemalloc.stop()
                return []
            if self._is_cover_brute_force(subset):
                tracemalloc.stop()
                return list(subset)
        tracemalloc.stop()
        return []


    def _is_cover_brute_force(self, cover):
        for u, v in self.edges:
            if u not in cover and v not in cover:
                return False
        return True
    
    
    def _greedy_cover(self, k):
        tracemalloc.start()
        cover = []
        is_valid, vertex_penalties = self._valid_cover(cover)
        while not is_valid:
            if tracemalloc.get_traced_memory()[0] > self._MEMORY_LIMIT:
                print(f'Memory limit of {self._MEMORY_LIMIT} bytes exceeded!')
                tracemalloc.stop()
                return []
            if len(cover) == k:
                tracemalloc.stop()
                return []
            vertex = [v for v in range(0, len(vertex_penalties)) if vertex_penalties[v] == max(vertex_penalties)][0]
            cover.append(vertex)
            is_valid, vertex_penalties = self._valid_cover(cover)
        tracemalloc.stop()
        return cover


    def _valid_cover(self, cover):
        is_valid = True
        vertex_penalties = [0] * self.graph_length
        for u in range(0, self.graph_length):
            for v in range(u, self.graph_length):
                if self.adjacency_matrix[u][v] == 1:
                    if (u not in cover) and (v not in cover):
                        is_valid = False
                        vertex_penalties[u] += 1
                        vertex_penalties[v] += 1
        return is_valid, vertex_penalties


if __name__=='__main__':

    n = 5  # number of vertices
    m = 3  # number of edges for each new vertex in barabasi_albert_graph
    graph = nx.barabasi_albert_graph(n, m, seed=42)

    vertex = VertexCover()
    vertex.set_graph(list(graph.nodes), list(graph.edges))
    
    cover = vertex.get_cover(k=3, method='brute_force')
    print(f'Brute Cover: {cover}')
    
    cover = vertex.get_cover(k=3, method='greedy')
    print(f'Greedy Cover: {cover}')
