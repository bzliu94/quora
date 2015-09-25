# 2015-09-24

# find one correct answer in O(n) time

# "move" node on which we focus by one in O(d) extra time

# total degree is in O(|E|) = O(n)

# "moving" O(n) times takes O(n) time

# there exists a way that is faster 
#   that uses explicit dynamic programming 
#   due to a smaller constant factor

from collections import defaultdict
done = defaultdict(lambda: defaultdict(lambda: float(0)))
memo = defaultdict(float)
class UndirectedGraph:
  def __init__(self):
    self.id_to_vertex_dict = {}
    self.id_pair_to_edge_dict = {}
    self.id_to_edge_id_to_edge_dict_dict = defaultdict(dict)
    self.edge_i = 1
    self.visited1 = defaultdict(lambda: False)
    self.visited2 = defaultdict(lambda: False)
    self.scores = defaultdict(lambda: 0.0)
    self.final_scores = defaultdict(lambda: 0.0)
  def getNode(self, id_value):
    return (self.id_to_vertex_dict)[id_value]
  @staticmethod
  def _getCanonicalEdgeIDPair(node_id1, node_id2):
    if node_id1 < node_id2:
      return (node_id1, node_id2)
    else:
      return (node_id2, node_id1)
  def removeEdge(self, edge):
    node_a = edge.getNodeA()
    node_b = edge.getNodeB()
    node_id_a = node_a.getIDValue()
    node_id_b = node_b.getIDValue()
    id_pair = self._getCanonicalEdgeIDPair(node_id_a, node_id_b)
    edge = (self.id_pair_to_edge_dict)[id_pair]
    (self.id_pair_to_edge_dict).pop(id_pair)
    (self.id_to_edge_id_to_edge_dict_dict)[node_id_a].pop(edge.getIDValue())
    (self.id_to_edge_id_to_edge_dict_dict)[node_id_b].pop(edge.getIDValue())
  def addNode(self, node):
    id_value = node.id_value
    (self.id_to_vertex_dict)[id_value] = node
  def getNode(self, id_value):
    result = (self.id_to_vertex_dict)[id_value]
    return result
  def addEdge(self, node_id1, node_id2):
    node1 = (self.id_to_vertex_dict)[node_id1]
    node2 = (self.id_to_vertex_dict)[node_id2]
    id_pair = UndirectedGraph._getCanonicalEdgeIDPair(node_id1, node_id2)
    edge = UndirectedEdge(self.edge_i, node1, node2)
    (self.id_pair_to_edge_dict)[id_pair] = edge
    (self.id_to_edge_id_to_edge_dict_dict)[node_id1][edge.id_value] = edge
    (self.id_to_edge_id_to_edge_dict_dict)[node_id2][edge.id_value] = edge
    self.edge_i = self.edge_i + 1
  def getNodes(self):
    return (self.id_to_vertex_dict).values()
  def getEdges(self):
    return (self.id_pair_to_edge_dict).values()
  def getEdgesForNode(self, node):
    node_id_value = node.id_value
    edge_id_to_edge_dict = (self.id_to_edge_id_to_edge_dict_dict)[node_id_value]
    edges = edge_id_to_edge_dict.values()
    return edges
  def getDegree(self, node):
    result = (self.id_to_edge_id_to_edge_dict_dict)[node.id_value]
    next_result = len(result)
    return next_result
  def getNeighbors(self, node):
    node_id_value = node.id_value
    edge_id_to_edge_dict = (self.id_to_edge_id_to_edge_dict_dict)[node_id_value]
    edges = edge_id_to_edge_dict.values()
    opposite_nodes = []
    for edge in edges:
      node_a = edge.node1
      opposite_node = node_a if node_a != node else edge.node2
      opposite_nodes.append(opposite_node)
    return opposite_nodes
  def firstPassExplore(self, node, prev_node = None):
    node_pair = (node, prev_node)
    node_pairs_stack_a = [node_pair]
    node_pairs_stack_b = []
    self._firstPassExploreHelper(node_pairs_stack_a, node_pairs_stack_b)
  def _firstPassExploreHelper(self, node_pairs_stack_a, node_pairs_stack_b):
    visited = self.visited1
    dict_dict = self.id_to_edge_id_to_edge_dict_dict
    while len(node_pairs_stack_a) != 0:
      node_pair = node_pairs_stack_a.pop(len(node_pairs_stack_a) - 1)
      node, prev_node = node_pair
      node_pairs_stack_b.append(node_pair)
      visited[node] = True
      node_id_value = node.id_value
      edge_id_to_edge_dict = dict_dict[node_id_value]
      edges = edge_id_to_edge_dict.values()
      for edge in edges:
        node_a = edge.node1
        opposite_node = node_a if node_a != node else edge.node2
        if visited[opposite_node] == False:
          next_num_edges = len(dict_dict[opposite_node.id_value])
          next_num_available_edges = next_num_edges - 1
          next_node_pair = (opposite_node, node)
          node_pairs_stack_a.append(next_node_pair)
    while len(node_pairs_stack_b) != 0:
      node_pair = node_pairs_stack_b.pop(len(node_pairs_stack_b) - 1)
      node, prev_node = node_pair
      self.firstPassPostvisit(node, prev_node)
  """
  def firstPassPrevisit(self, node, prev_node):
    pass
  """
  def firstPassPostvisit(self, node, prev_node):
    scores = self.scores
    dict_dict = self.id_to_edge_id_to_edge_dict_dict
    curr_time_required = node.T_value
    contributing_nodes = []
    node_id_value = node.id_value
    edge_id_to_edge_dict = dict_dict[node_id_value]
    edges = edge_id_to_edge_dict.values()
    for edge in edges:
      node_a = edge.node1
      opposite_node = node_a if node_a != node else edge.node2
      contributing_nodes.append(opposite_node)
    if prev_node != None: 
      contributing_nodes.remove(prev_node)
    contributing_score_values = [scores[x] for x in contributing_nodes]
    factor = None
    degree = len(dict_dict[node.id_value])
    if prev_node == None:
      factor = 1 / (1.0 * degree)
    elif degree == 1:
      factor = 1
    else:
      factor = 1 / (1.0 * degree - 1)
    curr_weighted_time_required = curr_time_required * (1.0 * factor)
    scores[node] = factor * sum(contributing_score_values) + curr_time_required
  def secondPassExplore(self, node, prev_node):
    node_pair = node, prev_node
    node_pairs_stack_a = [node_pair]
    tagged_node_pairs_stack_b = []
    self._secondPassExploreHelper(node_pairs_stack_a, tagged_node_pairs_stack_b)
  def _secondPassExploreHelper(self, node_pairs_stack_a, tagged_node_pairs_stack_b):
    visited = self.visited2
    dict_dict = self.id_to_edge_id_to_edge_dict_dict
    while len(node_pairs_stack_a) != 0:
      node_pair = node_pairs_stack_a.pop(len(node_pairs_stack_a) - 1)
      node, prev_node = node_pair
      visited[node] = True
      result = self.secondPassPrevisit(node, prev_node)
      prev_b_non_individual_score, prev_h_non_individual_score = result
      tagged_node_pair = ((prev_b_non_individual_score, prev_h_non_individual_score), node, prev_node)
      tagged_node_pairs_stack_b.append(tagged_node_pair)
      node_id_value = node.id_value
      edge_id_to_edge_dict = dict_dict[node_id_value]
      edges = edge_id_to_edge_dict.values()
      for edge in edges:
        node_a = edge.node1
        opposite_node = node_a if node_a != node else edge.node2
        if visited[opposite_node] == False:
          next_num_edges = len((dict_dict)[opposite_node.id_value])
          next_num_available_edges = next_num_edges - 1
          next_node_pair = (opposite_node, node)
          node_pairs_stack_a.append(next_node_pair)
    scores = self.scores
    while len(tagged_node_pairs_stack_b) != 0:
      tagged_node_pair = tagged_node_pairs_stack_b.pop(len(tagged_node_pairs_stack_b) - 1)
      (prev_b_non_individual_score, prev_h_non_individual_score), node, prev_node = tagged_node_pair
      if prev_node != None:
        scores[prev_node] = prev_b_non_individual_score
      scores[node] = prev_h_non_individual_score
  def secondPassPrevisit(self, node, prev_node):
    scores = self.scores
    final_scores = self.final_scores
    dict_dict = self.id_to_edge_id_to_edge_dict_dict
    if prev_node == None:
      prev_b_non_individual_score = None
      prev_h_non_individual_score = scores[node]
      final_scores[node] = prev_h_non_individual_score
      return (None, prev_h_non_individual_score)
    prev_done = done[prev_node]
    prev_b_non_individual_score = scores[prev_node]
    prev_h_non_individual_score = scores[node]
    b_degree = len(dict_dict[prev_node.id_value])
    h_degree = len(dict_dict[node.id_value])
    next_b_non_individual_score = None
    next_h_non_individual_score = None
    if b_degree == 1:
      next_b_non_individual_score = prev_node.T_value
    else:
      if len(prev_done) == b_degree:
        next_b_non_individual_score = (memo[prev_node] - prev_done[node]) / (1.0 * (b_degree - 1)) + prev_node.T_value
      else:
        prev_node_id_value = prev_node.id_value
        edge_id_to_edge_dict = dict_dict[prev_node_id_value]
        edges = edge_id_to_edge_dict.values()
        opposite_nodes = []
        for edge in edges:
          node_a = edge.node1
          opposite_node = node_a if node_a != prev_node else edge.node2
          opposite_nodes.append(opposite_node)
        prev_node_neighbors = opposite_nodes
        for curr_node in prev_node_neighbors:
          if curr_node not in done[prev_node]:
            curr_score = scores[curr_node]
            prev_done[curr_node] = curr_score
            memo[prev_node] += curr_score
        next_b_non_individual_score = (memo[prev_node] - prev_done[node]) / (1.0 * (b_degree - 1)) + prev_node.T_value
    scores[prev_node] = next_b_non_individual_score
    node_id_value = node.id_value
    edge_id_to_edge_dict = dict_dict[node_id_value]
    edges = edge_id_to_edge_dict.values()
    opposite_nodes = []
    for edge in edges:
      node_a = edge.node1
      opposite_node = node_a if node_a != node else edge.node2
      opposite_nodes.append(opposite_node)
    node_neighbors = opposite_nodes
    next_h_non_individual_score = sum([scores[x] for x in node_neighbors]) / (1.0 *
 (h_degree)) + node.T_value
    scores[node] = next_h_non_individual_score
    final_scores[node] = next_h_non_individual_score
    return (prev_b_non_individual_score, prev_h_non_individual_score)
  """
  def secondPassPostvisit(self, node, prev_node, prev_b_non_individual_score, prev_h_non_individual_score):
    scores = self.scores
    if prev_node != None:
      scores[prev_node] = prev_b_non_individual_score
    scores[node] = prev_h_non_individual_score
  """
  def toString(self):
    nodes = self.getNodes()
    edges = self.getEdges()
    vertex_str_list = [x.toString() for x in nodes]
    edge_str_list = [x.toString() for x in edges]
    vertex_str = " ".join(vertex_str_list)
    edge_str = " ".join(edge_str_list)
    result = "vertices: " + vertex_str + "; " + "undirected edges: " + edge_str
    return result
class Node:
  def __init__(self, id_value, T_value):
    self.id_value = id_value
    self.T_value = T_value
  def getIDValue(self):
    return self.id_value
  def getTimeRequired(self):
    return self.T_value
  def toString(self):
    id_value = self.getIDValue()
    result = str(id_value)
    return result
class UndirectedEdge:
  def __init__(self, id_value, node1, node2):
    self.id_value = id_value
    self.node1 = node1
    self.node2 = node2
  def getNodeA(self):
    return self.node1
  def getNodeB(self):
    return self.node2
  def getIDValue(self):
    return self.id_value
  def toString(self):
    id_value = str(self.getIDValue())
    node_str1 = self.getNodeA().toString()
    node_str2 = self.getNodeB().toString()
    result_str = "(" + id_value + ": " + node_str1 + ", " + node_str2 + ")"
    return result_str
graph = UndirectedGraph()
nodes = []
edges = []
import sys
import string
stream = sys.stdin
# stream = open("tests/official/input19.txt")
line = stream.readline()
line = line.rstrip("\n")
args = line.split(" ")
args = [string.atol(x) for x in args]
N = int(args[0])
line = stream.readline()
line = line.rstrip("\n")
args = line.split(" ")
args = [string.atol(x) for x in args]
T_list = [int(x) for x in args]
id_to_vertex_dict = graph.id_to_vertex_dict
for i in xrange(N):
  T_value = T_list[i]
  node = Node(i + 1, T_value)
  nodes.append(node)
  id_value = node.id_value
  id_to_vertex_dict[id_value] = node
id_to_vertex_dict = graph.id_to_vertex_dict
id_pair_to_edge_dict = graph.id_pair_to_edge_dict
dict_dict = graph.id_to_edge_id_to_edge_dict_dict
for i in xrange(N - 1):
  line = stream.readline()
  line = line.rstrip("\n")
  args = line.split(" ")
  args = [string.atol(x) for x in args]
  q_list = [int(x) for x in args]
  q1 = q_list[0]
  q2 = q_list[1]
  node1 = id_to_vertex_dict[q1]
  node2 = id_to_vertex_dict[q2]
  id_pair = None
  if q1 < q2:
    id_pair = (q1, q2)
  else:
    id_pair = (q2, q1)
  edge_i = graph.edge_i
  edge = UndirectedEdge(edge_i, node1, node2)
  id_pair_to_edge_dict[id_pair] = edge
  dict_dict[q1][edge.id_value] = edge
  dict_dict[q2][edge.id_value] = edge
  graph.edge_i = edge_i + 1
chosen_root_node = nodes[0]
chosen_root_id_value = chosen_root_node.getIDValue()
end_node = graph.firstPassExplore(chosen_root_node, None)
end_node = graph.secondPassExplore(chosen_root_node, None)
root_score = graph.scores[chosen_root_node]
final_scores = graph.final_scores
score_tagged_nodes = [(final_scores[x], x) for x in nodes]
score_values = [x[0] for x in score_tagged_nodes]
min_score_value = min(score_values)
candidate_tagged_nodes = [x for x in score_tagged_nodes if x[0] == min_score_value]
chosen_tagged_node = candidate_tagged_nodes[0]
chosen_node = chosen_tagged_node[1]
chosen_node_identifier_value = chosen_node.getIDValue()
print chosen_node_identifier_value
