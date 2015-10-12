# 2015-10-11

# is a max. weight closure problem

# uses borrowed push-relabel max. flow algorithm

# involves picard transform

# contains dfs-augmenting-path-finding for ford-fulkerson
# and contains edmonds-karp

from collections import deque
from collections import defaultdict
class DirectedGraph:
  def __init__(self):
    self.node_pair_to_edge_dict = {}
    self.location_to_node_dict = {}
    self.node_without_location_count_dict = defaultdict(lambda: 0)
    self.node_to_outgoing_edge_list_dict = defaultdict(list)
  def addNode(self, node):
    location = node.getLocation()
    self.location_to_node_dict[location] = node
  def addNodeWithoutLocation(self, node):
    self.node_without_location_count_dict[node] += 1
  def addEdge(self, edge):
    origin = edge.getOrigin()
    destination = edge.getDestination()
    node_pair = (origin, destination)
    self.node_pair_to_edge_dict[node_pair] = edge
    self.node_to_outgoing_edge_list_dict[origin].append(edge)
  def getNodes(self):
    nodes1 = self.location_to_node_dict.values()
    nodes2 = self.node_without_location_count_dict.keys()
    nodes = nodes1 + nodes2
    return nodes
  def getEdges(self):
    return self.node_pair_to_edge_dict.values()
  def getNode(self, location):
    return self.location_to_node_dict[location]
  def getOutgoingEdges(self, node):
    return self.node_to_outgoing_edge_list_dict[node]
  def haveEdge(self, origin, destination):
    node_pair = (origin, destination)
    result = node_pair in self.node_pair_to_edge_dict
    return result
  def haveNode(self, location):
    return location in self.location_to_node_dict
  @staticmethod
  def transformIntoMaxFlowGraph(graph):
    pass
  def _edgeInPath(self, edge, path_set):
    origin = edge.getOrigin()
    destination = edge.getDestination()
    node_pair = (destination, origin)
    reverse_edge = self.node_pair_to_edge_dict[node_pair]
    result = edge in path_set or reverse_edge in path_set
    return result
  def findPathBFS(self, source, sink):
    for node in nodes:
      node.setMarked(False)
    return self.findPathBFSHelper(source, sink)
  def findPathBFSHelper(self, source, sink):
    queue = deque()
    queue.append((source, set([])))
    while len(queue) != 0:
      result = queue.popleft()
      u, associated_set = result
      u.setMarked(True)
      for edge in self.getOutgoingEdges(u):
        destination = edge.getDestination()
        if destination == sink:
          return associated_set
        if destination.getMarked() == False:
          queue.append((destination, associated_set | set([edge])))
    return None
  def findPathDFS(self, source, sink):
    return self.findPathDFSHelper(source, sink, set([]))
  def findPathDFSHelper(self, source, sink, path_set):
    if source == sink:
      return path_set.copy()
    for edge in self.getOutgoingEdges(source):
      origin = edge.getOrigin()
      destination = edge.getDestination()
      node_pair = (origin, destination)
      edge = self.node_pair_to_edge_dict[node_pair]
      residual = edge.getCapacity() - edge.getFlow()
      node_pair = (destination, origin)
      reverse_edge = self.node_pair_to_edge_dict[node_pair]
      edge_in_path = edge in path_set or reverse_edge in path_set
      if residual > 0 and not edge_in_path:
        path_set.add(edge)
        result = self.findPathDFSHelper(edge.getDestination(), sink, path_set)
        path_set.remove(edge)
        if result != None:
          return result
    return None
  def toResidualNetworkReachableNodes(self, start):
    node_set = set([start])
    self.toResidualNetworkReachableNodesHelper(start, node_set)
    node_list = list(node_set)
    return node_list
  def toResidualNetworkReachableNodesHelper(self, start, node_set):
    for edge in self.getOutgoingEdges(start):
      origin = edge.getOrigin()
      destination = edge.getDestination()
      node_pair = (origin, destination)
      edge = self.node_pair_to_edge_dict[node_pair]
      residual = edge.getCapacity() - edge.getFlow()
      if residual > 0 and edge.getDestination() not in node_set:
        node_set.add(edge.getDestination())
        self.toResidualNetworkReachableNodesHelper(edge.getDestination(), node_set)
  def maxFlow(self, source, sink):
    for edge in self.getEdges():
      origin = edge.getOrigin()
      destination = edge.getDestination()
      capacity = edge.getCapacity()
      if self.haveEdge(destination, origin) == False:
        reverse_edge = DirectedEdge(destination, origin, 0, 0, True)
        self.addEdge(reverse_edge)
    path_set = self.findPathBFS(source, sink)
    while path_set != None:
      residuals = []
      for edge in list(path_set):
        origin = edge.getOrigin()
        destination = edge.getDestination()
        node_pair = (origin, destination)
        edge = self.node_pair_to_edge_dict[node_pair]
        residual = edge.getCapacity() - edge.getFlow()
        residuals.append(residual)
      flow = min(residuals)
      for edge in list(path_set):
        origin = edge.getOrigin()
        destination = edge.getDestination()
        node_pair = (destination, origin)
        reverse_edge = self.node_pair_to_edge_dict[node_pair]
        edge.setFlow(edge.getFlow() + flow)
        reverse_edge.setFlow(reverse_edge.getFlow() - flow)
      path_set = self.findPathBFS(source, sink)
    flow_values = [edge.getFlow() for edge in self.getOutgoingEdges(source)]
    result = sum(flow_values)
    return result
  @staticmethod
  def solveMaxFlow(graph, s, t):
    result = graph.maxFlow(s, t)
    return result
  def toString(self):
    node_str_list = [x.toString() for x in self.getNodes()]
    edge_str_list = [x.toString() for x in self.getEdges()]
    node_str = " ".join(node_str_list)
    edge_str = " ".join(edge_str_list)
    result_str = "nodes: " + node_str + "\n" + "edges: " + edge_str
    return result_str
class Node:
  def __init__(self, item, weight, location):
    self.item = item
    self.weight = weight
    self.location = location
    self.marked = False
  def getItem(self):
    return self.item
  def getWeight(self):
    return self.weight
  def getLocation(self):
    return self.location
  def getMarked(self):
    return self.marked
  def setWeight(self, weight):
    self.weight = weight
  def setMarked(self, marked):
    self.marked = marked
  def toString(self):
    return str(self.item)
class DirectedEdge:
  def __init__(self, origin, destination, capacity, flow, is_reverse):
    self.origin = origin
    self.destination = destination
    self.capacity = capacity
    self.flow = flow
    self.is_reverse = is_reverse
  def getOrigin(self):
    return self.origin
  def getDestination(self):
    return self.destination
  def getCapacity(self):
    return self.capacity
  def getFlow(self):
    return self.flow
  def isReverse(self):
    return self.is_reverse
  def setCapacity(self, capacity):
    self.capacity = capacity
  def setFlow(self, flow):
    self.flow = flow
  def toString(self):
    return "(" + str(self.getOrigin().toString()) + ", " +      str(self.getDestination().toString()) + ", " +      str(self.getCapacity()) + ", " +      str(self.getFlow()) + ")"
def relabel_to_front(C, source, sink):
   n = len(C) 
   F = [[0] * n for _ in xrange(n)]
   height = [0] * n 
   excess = [0] * n 
   seen   = [0] * n 
   nodelist = [i for i in xrange(n) if i != source and i != sink]
   def push(u, v):
       send = min(excess[u], C[u][v] - F[u][v])
       F[u][v] += send
       F[v][u] -= send
       excess[u] -= send
       excess[v] += send
   def toResidualNetworkReachableNodes(start_index):
     node_set = set([start_index])
     toResidualNetworkReachableNodesHelper(start_index, node_set)
     node_list = list(node_set)
     return node_list
   def toResidualNetworkReachableNodesHelper(start_index, node_set):
     for destination_index in xrange(n):
       residual = C[start_index][destination_index] - F[start_index][destination_index]
       if residual > 0 and destination_index not in node_set:
         node_set.add(destination_index)
         toResidualNetworkReachableNodesHelper(destination_index, node_set)
   height[source] = n   
   excess[source] = float("+inf") 
   for v in xrange(n):
       push(source, v)
   p = 0
   while p < len(nodelist):
       u = nodelist[p]
       old_height = height[u]
       row_C = C[u]
       row_F = F[u]
       while excess[u] > 0:
           if seen[u] < n: 
               v = seen[u]
               if row_C[v] - row_F[v] > 0 and height[u] > height[v]:
                   push(u, v)
               else:
                   seen[u] += 1
           else: 
               min_height = float("+inf")
               for v in xrange(n):
                   if row_C[v] - row_F[v] > 0:
                       min_height = min(min_height, height[v])
                       height[u] = min_height + 1
               seen[u] = 0
       if height[u] > old_height:
           nodelist.insert(0, nodelist.pop(p)) 
           p = 0 
       else:
           p += 1
   return toResidualNetworkReachableNodes(source)
import sys
import string
stream = sys.stdin
# stream = open("tests/official/input11.txt")
# stream = open("tests/official/input99.txt")
# stream = open("tests/official/input99_modified.txt")
line = stream.readline()
line = line.rstrip("\n")
args = line.split(" ")
args = [string.atol(x) for x in args]
level_row_list_list = []
N = int(args[0])
for level in xrange(N):
  rows = []
  for i in xrange(level + 1):
    line = stream.readline()
    line = line.rstrip("\n")
    args = line.split(" ")
    args = [string.atoi(x) for x in args]
    row = args
    rows.append(row)
  level_row_list_list.append(rows)
graph = DirectedGraph()
for i in xrange(len(level_row_list_list)):
  level = level_row_list_list[i]
  for j in xrange(len(level)):
    row = level[j]
    for k in xrange(len(row)):
      location = (j, k, i)
      value = row[k]
      item = value
      node = Node(item, value, location)
      graph.addNode(node)
for node in graph.getNodes():
  location = node.getLocation()
  a, b, c = location
  candidate_prerequisite_locations = [(a - 1, b, c - 1), (a, b - 1, c - 1), (a, b, c - 1)]
  candidate_dest_locations = [x for x in candidate_prerequisite_locations if graph.haveNode(x)]
  nodes = [graph.getNode(x) for x in candidate_dest_locations]
  edges = [DirectedEdge(node, x, 0, 0, False) for x in nodes]
  for edge in edges:
    graph.addEdge(edge)
edges = graph.getEdges()
for edge in edges:
  edge.setCapacity(float("+inf"))
s = Node(None, None, None)
t = Node(None, None, None)
nodes = graph.getNodes()
graph.addNodeWithoutLocation(s)
graph.addNodeWithoutLocation(t)
positive_weight_nodes = [x for x in nodes if x.getWeight() > 0]
negative_weight_nodes = [x for x in nodes if x.getWeight() < 0]
for node in positive_weight_nodes:
  weight = node.getWeight()
  capacity = weight
  edge = DirectedEdge(s, node, capacity, 0, False)
  graph.addEdge(edge)
  node.setWeight(0)
for node in negative_weight_nodes:
  weight = node.getWeight()
  capacity = -1 * weight
  edge = DirectedEdge(node, t, capacity, 0, False)
  graph.addEdge(edge)
  node.setWeight(0)
nodes = graph.getNodes()
edges = graph.getEdges()
id_to_node_dict = {}
node_to_id_dict = {}
for i in xrange(len(nodes)):
  id_value = i
  node = nodes[i]
  id_to_node_dict[id_value] = node
  node_to_id_dict[node] = id_value
C = []
for i in xrange(len(nodes)):
  row = []
  for j in xrange(len(nodes)):
    value = 0
    row.append(value)
  C.append(row)
for edge in edges:
  u = edge.getOrigin()
  v = edge.getDestination()
  u_index = node_to_id_dict[u]
  v_index = node_to_id_dict[v]
  capacity = edge.getCapacity()
  C[u_index][v_index] = capacity
s_index = node_to_id_dict[s]
t_index = node_to_id_dict[t]
node_indices = relabel_to_front(C, s_index, t_index)
node_list = [id_to_node_dict[x] for x in node_indices]
culled_node_list = [x for x in node_list if x != s and x != t]
items = [x.getItem() for x in culled_node_list]
weight_sum = sum(items)
print weight_sum
