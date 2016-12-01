# 2016-05-16

# basic incognito with suppression budget

# see tests/README.md for input details

import string
from collections import defaultdict
import sys
import csv
from collections import deque
import heapq
class QIDPreSet:
  def __init__(self, nodes, directed_edges, attribute):
    self.nodes = nodes
    self.directed_edges = directed_edges
    self.attribute = attribute
  def getNodes(self):
    return self.nodes
  def getDirectedEdges(self):
    return self.directed_edges
  def maskAttributeValue(self, value, distance):
    pass
  def getWeightedInformationLoss(self, distance):
    pass
class TypeAPreSet(QIDPreSet):
  def __init__(self, attribute, num_parts, avg_value_length):
    self.num_parts = num_parts
    self.avg_value_length = avg_value_length
    nodes = []
    for i in xrange(num_parts + 2):
      node = Node(None, {attribute: i}, False, False)
      attribute_index_1a_node_pair_set = {(attribute._getIndex(), node)}
      node._setAttributeIndex1ANodePairSet(attribute_index_1a_node_pair_set)
      nodes.append(node)
    edges = []
    for i in xrange(num_parts + 1):
      node1 = nodes[i]
      node2 = nodes[i + 1]
      edge = DirectedEdge(node1, node2)
      edges.append(edge)
    QIDPreSet.__init__(self, nodes, edges, attribute)
  def _getNumParts(self):
    return self.num_parts
  def _getAvgValueLength(self):
    return self.avg_value_length
  def maskAttributeValue(self, value, distance):
    num_parts = self._getNumParts()
    parts = value.split("-")
    if distance >= 0 and distance <= num_parts - 1:
      num_keep_parts = num_parts - distance
      next_parts = []
      for i in xrange(num_keep_parts):
        curr_part = parts[i]
        next_parts.append(curr_part)
      for i in xrange(distance):
        curr_part = "*"
        next_parts.append(curr_part)
      next_value = string.join(next_parts, "-")
      return next_value
    elif distance == num_parts:
      next_value = (value[0] + "*") if len(value) != 0 else "*"
      return next_value
    elif distance == num_parts + 1:
      next_value = "*"
      return next_value
  def getWeightedInformationLoss(self, distance):
    return distance
class TypeBPreSet(QIDPreSet):
  def __init__(self, attribute, have_expensive_suppression, avg_value_length, max_prefix_size):
    self.have_expensive_suppression = have_expensive_suppression
    self.avg_value_length = avg_value_length
    self.max_prefix_size = max_prefix_size
    nodes = []
    for i in xrange(max_prefix_size + 2):
      node = Node(None, {attribute: i}, False, False)
      attribute_index_1a_node_pair_set = {(attribute._getIndex(), node)}
      node._setAttributeIndex1ANodePairSet(attribute_index_1a_node_pair_set)
      nodes.append(node)
    edges = []
    for i in xrange(max_prefix_size + 1):
      node1 = nodes[i]
      node2 = nodes[i + 1]
      edge = DirectedEdge(node1, node2)
      edges.append(edge)
    QIDPreSet.__init__(self, nodes, edges, attribute)
  def _haveExpensiveSuppression(self):
    return self.have_expensive_suppression
  def _getAvgValueLength(self):
    return self.avg_value_length
  def _getMaxPrefixSize(self):
    return self.max_prefix_size
  def maskAttributeValue(self, value, distance):
    next_value = None
    if distance == 0:
      next_value = value
    elif distance >= 1 and distance <= self._getMaxPrefixSize():
      next_value = (value[0 : self._getMaxPrefixSize() - distance + 1] + "*") if len(value) != 0 else "*"
    elif distance == self._getMaxPrefixSize() + 1:
      next_value = "*"
    return next_value
  def getWeightedInformationLoss(self, distance):
    return distance * (2 if self._haveExpensiveSuppression() == True else 1)
class TypeCPreSet(QIDPreSet):
  def __init__(self, attribute):
    node1 = Node(None, {attribute: 0}, False, False)
    attribute_index_1a_node_pair_set1 = {(attribute._getIndex(), node1)}
    node1._setAttributeIndex1ANodePairSet(attribute_index_1a_node_pair_set1)
    node2 = Node(None, {attribute: 1}, False, False)
    attribute_index_1a_node_pair_set2 = {(attribute._getIndex(), node2)}
    node2._setAttributeIndex1ANodePairSet(attribute_index_1a_node_pair_set2)
    edge12 = DirectedEdge(node1, node2)
    nodes = [node1, node2]
    edges = [edge12]
    QIDPreSet.__init__(self, nodes, edges, attribute)
  def maskAttributeValue(self, value, distance):
    next_value = None
    if distance == 0:
      next_value = value
    elif distance == 1:
      next_value = "*"
    return next_value
  def getWeightedInformationLoss(self, distance):
    return distance
class TypeDPreSet(QIDPreSet):
  def __init__(self, attribute, num_chars):
    self.num_chars = num_chars
    nodes = []
    for i in xrange(num_chars + 1):
      node = Node(None, {attribute: i}, False, False)
      attribute_index_1a_node_pair_set = {(attribute._getIndex(), node)}
      node._setAttributeIndex1ANodePairSet(attribute_index_1a_node_pair_set)
      nodes.append(node)
    edges = []
    for i in xrange(num_chars):
      node1 = nodes[i]
      node2 = nodes[i + 1]
      edge = DirectedEdge(node1, node2)
      edges.append(edge)
    QIDPreSet.__init__(self, nodes, edges, attribute)
  def _getNumChars(self):
    return self.num_chars
  def _getMaxNumChars(self):
    return self.max_num_chars
  @staticmethod
  def leftPadValueWithZeroes(value, goal_length):
    value_length = len(value)
    if goal_length < value_length:
      result = value[ : goal_length] + "*" * (value_length - goal_length)
      return result
    else:
      zero_length = goal_length - value_length
      result = "0" * zero_length + value
      return result
  def maskAttributeValue(self, value, distance):
    next_value = TypeDPreSet.leftPadValueWithZeroes(value, self._getNumChars() - distance)
    if self._getNumChars() < len(value):
      return next_value
    else:
      num_keep_chars = self._getNumChars() - distance
      num_stars = distance
      result = next_value[0 : num_keep_chars + 1] + "*" * num_stars
      return result
  def getWeightedInformationLoss(self, distance):
    return distance
class TypeGPreSet(QIDPreSet):
  def __init__(self, attribute):
    node1 = Node(None, {attribute: 0}, False, False)
    attribute_index_1a_node_pair_set1 = {(attribute._getIndex(), node1)}
    node1._setAttributeIndex1ANodePairSet(attribute_index_1a_node_pair_set1)
    nodes = [node1]
    edges = []
    QIDPreSet.__init__(self, nodes, edges, attribute)
  def maskAttributeValue(self, value, distance):
    return "*"
  def getWeightedInformationLoss(self, distance):
    return 0
class DirectedGraph:
  def __init__(self, nodes, directed_edges, num_qid_attributes):
    self.node_set = set([])
    self.node_origin_to_directed_edge_set_dict = defaultdict(lambda: set([]))
    self.node_destination_to_directed_edge_set_dict = defaultdict(lambda: set([]))
    self.node_origin_to_partner_set_dict = defaultdict(lambda: set([]))
    for node in nodes:
      self.addNode(node)
    for directed_edge in directed_edges:
      self.addDirectedEdge(directed_edge)
    self.num_qid_attributes = num_qid_attributes
  def getNumQIDAttributes(self):
    return self.num_qid_attributes
  def getNodes(self):
    node_set = self.node_set
    result = list(node_set)
    return result
  def getDirectedEdges(self):
    edge_dict = self.node_origin_to_directed_edge_set_dict
    edge_set_list = edge_dict.values()
    edge_set = reduce(lambda x, y: x | y, edge_set_list, set([]))
    edge_list = list(edge_set)
    return edge_list
  def addNode(self, node):
    self.node_set |= set([node])
  def addDirectedEdge(self, directed_edge):
    origin_node = directed_edge.getOriginNode()
    destination_node = directed_edge.getDestinationNode()
    self.node_origin_to_directed_edge_set_dict[origin_node] |= set([directed_edge])
    self.node_destination_to_directed_edge_set_dict[destination_node] |= set([directed_edge])
    self.node_origin_to_partner_set_dict[origin_node] |= set([destination_node])
  def _getNodeOriginToPartnerSetDict(self):
    return self.node_origin_to_partner_set_dict
  def getOutgoingEdgePartnersFast(self, node):
    origin_node = node
    nopsd = self._getNodeOriginToPartnerSetDict()
    return nopsd
  def getOutgoingEdgePartners(self, node):
    origin_node = node
    directed_edge_set = self.node_origin_to_directed_edge_set_dict[origin_node]
    directed_edge_list = list(directed_edge_set)
    partner_nodes = [x.getDestinationNode() for x in directed_edge_list]
    return partner_nodes
  def getOutgoingDegree(self, node):
    partner_nodes = self.getOutgoingEdgePartners(node)
    degree = len(partner_nodes)
    return degree
  def getIngoingEdgePartners(self, node):
    destination_node = node
    directed_edge_set = self.node_destination_to_directed_edge_set_dict[destination_node]
    directed_edge_list = list(directed_edge_set)
    partner_nodes = [x.getOriginNode() for x in directed_edge_list]
    return partner_nodes
  def getIngoingDegree(self, node):
    partner_nodes = self.getIngoingEdgePartners(node)
    degree = len(partner_nodes)
    return degree
  def getVisitedNeighbors(self, node):
    partners1 = self.getOutgoingEdgePartners(node)
    partners2 = self.getIngoingEdgePartners(node)
    partners = partners1 + partners2
    visited_partners = [x for x in partners if x.isVisited() == True]
    return visited_partners
  def removeNodeAndAssociatedDirectedEdges(self, node):
    self.node_set -= set([node])
    if node in self.node_origin_to_directed_edge_set_dict:
      self.node_origin_to_directed_edge_set_dict.pop(node)
    if node in self.node_destination_to_directed_edge_set_dict:
      self.node_destination_to_directed_edge_set_dict.pop(node)
    if node in self.node_origin_to_partner_set_dict:
      self.node_origin_to_partner_set_dict.pop(node)
  def haveOutgoingEdgePartner(self, node, query_node):
    nops = self.getOutgoingEdgePartnersFast(node)
    have_partner = query_node in nops
    return have_partner
  def copy(self):
    nodes = self.getNodes()
    edges = self.getDirectedEdges()
    num_qid_attributes = self.getNumQIDAttributes()
    graph = DirectedGraph(nodes, edges, num_qid_attributes)
    return graph
class Attribute:
  def __init__(self, name_str, index, pre_set = None):
    self.name_str = name_str
    self.index = index
    self.pre_set = pre_set
  def getNameStr(self):
    return self.name_str
  def _getIndex(self):
    return self.index
  def getValueGivenRow(self, row):
    index = self._getIndex()
    value = row[index]
    return value
  def getPreSet(self):
    return self.pre_set
  def setPreSet(self, pre_set):
    self.pre_set = pre_set
class Node:
  def __init__(self, attribute_index_1a_node_pair_set, distance_dict, is_marked, is_visited, parent1 = None, parent2 = None):
    self.attribute_index_1a_node_pair_set = attribute_index_1a_node_pair_set
    self.distance_dict = distance_dict
    self.is_marked = is_marked
    self.is_visited = is_visited
    self.parent1 = parent1
    self.parent2 = parent2
  def getNumAttributes(self):
    return len(self.attribute_index_1a_node_pair_set)
  def getParent1(self):
    return self.parent1
  def getParent2(self):
    return self.parent2
  def _getAttributeIndex1ANodePairSet(self):
    return self.attribute_index_1a_node_pair_set
  def _getAttributeIndexSet(self):
    pair_set = self._getAttributeIndex1ANodePairSet()
    pair_list = list(pair_set)
    indices = [x[0] for x in pair_list]
    index_set = set(indices)
    return index_set
  def _setAttributeIndex1ANodePairSet(self, pair_set):
    self.attribute_index_1a_node_pair_set = pair_set
  def getAttributeIndexTo1ANodeDict(self):
    ai1and = {}
    sai1anpl = self.getSortedAttributeIndex1ANodePairList()
    for pair in sai1anpl:
      index, one_attribute_node = pair
      ai1and[index] = one_attribute_node
    return ai1and
  def getSortedAttributeIndex1ANodePairList(self):
    attribute_index_1a_node_pair_set = self._getAttributeIndex1ANodePairSet()
    attribute_index_1a_node_pair_list = list(attribute_index_1a_node_pair_set)
    sorted_attribute_index_1a_node_pair_list = sorted(attribute_index_1a_node_pair_list)
    result = sorted_attribute_index_1a_node_pair_list
    return result
  def getDistanceDict(self):
    return self.distance_dict
  def getHeight(self):
    distance_dict = self.getDistanceDict()
    distance_values = distance_dict.values()
    height = sum(distance_values)
    return height
  def toString(self):
    distance_dict = self.getDistanceDict().copy()
    next_distance_dict = {}
    for item in distance_dict.items():
      key, value = item
      index = key._getIndex()
      next_distance_dict[index] = value
    wil = self.getTotalWeightedInformationLoss()
    result = (next_distance_dict, self.getHeight(), wil, self.isMarked())
    return result
  def isMarked(self):
    return self.is_marked
  def setMarked(self, is_marked):
    self.is_marked = is_marked
  def copy(self):
    attribute_index_1a_node_pair_set = self._getAttributeIndex1ANodePairSet().copy()
    distance_dict = self.getDistanceDict().copy()
    is_marked = self.isMarked()
    node = Node(attribute_index_1a_node_pair_set, distance_dict, is_marked)
    return node
  def isVisited(self):
    return self.is_visited
  def setIsVisited(self, is_visited):
    self.is_visited = is_visited
  @staticmethod
  def getPrevSortedAttributeIndex1ANodePairList(sai1anpl, i_leave_out):
    curr_sai1anpl = sai1anpl[ : ]
    next_sai1anpl = []
    for i in xrange(len(curr_sai1anpl)):
      curr_sai1anp = curr_sai1anpl[i]
      curr_index, node = curr_sai1anp
      if i != i_leave_out:
        next_sai1anpl.append(curr_sai1anp)
    return next_sai1anpl
  def getTypeOneKey(self):
    i = self.getNumAttributes()
    sai1anp = self.getSortedAttributeIndex1ANodePairList()
    sai1anp_tuple = tuple(sai1anp)
    sai1anp_prefix_tuple = sai1anp_tuple[0 : i - 2]
    sai1anp_suffix1 = sai1anp[i - 2]
    type_one_key = sai1anp_prefix_tuple + (sai1anp_suffix1, )
    return type_one_key
  def getTypeTwoKey(self):
    i = self.getNumAttributes()
    sai1anp = self.getSortedAttributeIndex1ANodePairList()
    sai1anp_tuple = tuple(sai1anp)
    sai1anp_prefix_tuple = sai1anp_tuple[0 : i - 2]
    sai1anp_suffix2 = sai1anp[i - 1]
    type_two_key = sai1anp_prefix_tuple + (sai1anp_suffix2, )
    return type_two_key
  def getTypeThreeKey(self):
    i = self.getNumAttributes()
    sai1anp = self.getSortedAttributeIndex1ANodePairList()
    sai1anp_tuple = tuple(sai1anp)
    sai1anp_prefix_tuple = sai1anp_tuple[0 : i - 2]
    type_three_key = sai1anp_prefix_tuple
    return type_three_key
  def getTypeFourKey(self):
    i = self.getNumAttributes()
    sai1anp = self.getSortedAttributeIndex1ANodePairList()
    sai1anp_tuple = tuple(sai1anp)
    sai1anp_prefix_tuple = sai1anp_tuple[0 : i - 1]
    type_four_key = sai1anp_prefix_tuple
    return type_four_key
  def getTypeFiveKey(self):
    i = self.getNumAttributes()
    sai1anp = self.getSortedAttributeIndex1ANodePairList()
    sai1anp_tuple = tuple(sai1anp)
    sai1anp_suffix = sai1anp_tuple[i - 1]
    index = sai1anp_suffix[0]
    type_five_key = index
    return type_five_key
  @staticmethod
  def formKey(type_one_key, type_two_key):
    num_components = len(type_one_key)
    suffix = type_two_key[num_components - 1]
    key = type_one_key + (suffix, )
    return key
  def getTotalWeightedInformationLoss(self):
    distance_dict = self.getDistanceDict()
    total_weighted_information_loss = 0
    for attribute, distance in distance_dict.items():
      pre_set = attribute.getPreSet()
      weighted_information_loss = pre_set.getWeightedInformationLoss(distance)
      total_weighted_information_loss += weighted_information_loss
    return total_weighted_information_loss
class DirectedEdge:
  def __init__(self, origin_node, destination_node):
    self.origin_node = origin_node
    self.destination_node = destination_node
  def getOriginNode(self):
    return self.origin_node
  def getDestinationNode(self):
    return self.destination_node
class FrequencySet:
  def __init__(self, masked_row_qid_tuple_to_count_dict):
    self.masked_row_qid_tuple_to_count_dict = masked_row_qid_tuple_to_count_dict
  def getMaskedRowQIDTupleToCountDict(self):
    return self.masked_row_qid_tuple_to_count_dict
  @staticmethod
  def maskedRowQIDDictToTuple(masked_row_qid_dict, qid_index_set):
    sorted_qid_index_list = sorted(list(qid_index_set))
    component_list = []
    for i in sorted_qid_index_list:
      component = masked_row_qid_dict[i]
      component_list.append(component)
    component_tuple = tuple(component_list)
    return component_tuple
  @staticmethod
  def getMaskedQIDRowDictList(rows, node, num_attributes, index_to_qid_attribute_dict, qid_index_set):
    distance_dict = node.getDistanceDict()
    next_qid_row_dict_list = []
    sorted_qid_index_list = sorted(list(qid_index_set))
    for row in rows:
      next_qid_row_dict = {}
      i = 0
      for index in sorted_qid_index_list:
        original_value = row[i]
        attribute_value = None
        attribute = index_to_qid_attribute_dict[index]
        pre_set = attribute.getPreSet()
        value = row[i]
        distance = None
        if attribute in distance_dict.keys():
          distance = distance_dict[attribute]
        else:
          distance = 0
        attribute_value = pre_set.maskAttributeValue(original_value, distance)
        next_qid_row_dict[index] = attribute_value
        i += 1
      next_qid_row_dict_list.append(next_qid_row_dict)
    return next_qid_row_dict_list
  @staticmethod
  def getQIDOnlyRows(rows, node, num_attributes, index_to_qid_attribute_dict, qid_index_set):
    sorted_qid_index_list = sorted(list(qid_index_set))
    row_qid_tuples = []
    for row in rows:
      row_qid_list = []
      for index in sorted_qid_index_list:
        component = row[index]
        row_qid_list.append(component)
      row_qid_tuple = tuple(row_qid_list)
      row_qid_tuples.append(row_qid_tuple)
    return row_qid_tuples
  @staticmethod
  def determineFrequencySetFromScratch(rows, node, num_attributes, index_to_qid_attribute_dict, qid_index_set):
    unmasked_row_qid_tuple_to_count_dict = defaultdict(lambda: 0)
    sorted_qid_index_list = sorted(list(qid_index_set))
    row_qid_tuples = FrequencySet.getQIDOnlyRows(rows, node, num_attributes, index_to_qid_attribute_dict, qid_index_set)
    for row_qid_tuple in row_qid_tuples:
      unmasked_row_qid_tuple_to_count_dict[row_qid_tuple] += 1
    unmasked_row_qid_list_list = [list(x) for x in unmasked_row_qid_tuple_to_count_dict.keys()]
    unmasked_rows = unmasked_row_qid_list_list
    masked_qid_row_dict_list = FrequencySet.getMaskedQIDRowDictList(unmasked_rows, node, num_attributes, index_to_qid_attribute_dict, qid_index_set)
    masked_row_qid_tuple_to_count_dict = defaultdict(lambda: 0)
    num_rows = len(masked_qid_row_dict_list)
    for i in xrange(num_rows):
      masked_qid_row_dict = masked_qid_row_dict_list[i]
      masked_qid_row_tuple = FrequencySet.maskedRowQIDDictToTuple(masked_qid_row_dict, qid_index_set)
      unmasked_qid_row_tuple = tuple(unmasked_row_qid_list_list[i])
      partial_count = unmasked_row_qid_tuple_to_count_dict[unmasked_qid_row_tuple]
      masked_row_qid_tuple_to_count_dict[masked_qid_row_tuple] += partial_count
    frequency_set = FrequencySet(masked_row_qid_tuple_to_count_dict)
    return frequency_set
  @staticmethod
  def determineFrequencySetUsingParent(rows, node, parent_frequency_set, num_attributes, index_to_qid_attribute_dict, qid_index_set):
    masked_row_qid_tuple_to_count_dict = parent_frequency_set.getMaskedRowQIDTupleToCountDict()
    masked_row_qid_list_list = [list(x) for x in masked_row_qid_tuple_to_count_dict.keys()]
    masked_rows = masked_row_qid_list_list
    next_masked_qid_row_dict_list = FrequencySet.getMaskedQIDRowDictList(masked_rows, node, num_attributes, index_to_qid_attribute_dict, qid_index_set)
    next_masked_row_qid_tuple_to_count_dict = defaultdict(lambda: 0)
    sorted_qid_index_list = sorted(list(qid_index_set))
    num_rows = len(next_masked_qid_row_dict_list)
    for i in xrange(num_rows):
      next_masked_qid_row_dict = next_masked_qid_row_dict_list[i]
      component_list = [next_masked_qid_row_dict[x] for x in sorted_qid_index_list]
      component_tuple = tuple(component_list)
      masked_qid_row_tuple = tuple(masked_row_qid_list_list[i])
      partial_count = masked_row_qid_tuple_to_count_dict[masked_qid_row_tuple]
      next_masked_row_qid_tuple_to_count_dict[component_tuple] += partial_count
    frequency_set = FrequencySet(next_masked_row_qid_tuple_to_count_dict)
    return frequency_set
  def getK(self):
    counts = []
    masked_row_qid_tuple_to_count_dict = self.getMaskedRowQIDTupleToCountDict()
    for masked_row_qid_tuple in masked_row_qid_tuple_to_count_dict.keys():
      count = masked_row_qid_tuple_to_count_dict[masked_row_qid_tuple]
      counts.append(count)
    min_count = min(counts)
    return min_count, masked_row_qid_tuple_to_count_dict
  def satisfiesKAnonymityGivenSuppressionBudget(self, k, suppression_budget):
    suppression_cost = 0
    actual_k, masked_row_qid_tuple_to_count_dict = self.getK()
    for masked_row_qid_tuple in masked_row_qid_tuple_to_count_dict.keys():
      count = masked_row_qid_tuple_to_count_dict[masked_row_qid_tuple]
      if count < k:
        suppression_cost += count
    does_satisfy = suppression_cost <= suppression_budget
    return does_satisfy, suppression_cost
  def satisfiesKAnonymity(self, k):
    actual_k, masked_row_qid_tuple_to_count_dict = self.getK()
    does_satisfy = actual_k >= k
    return does_satisfy
def combineDistanceDicts(distance_dict1, distance_dict2):
  next_distance_dict = distance_dict1.copy()
  next_distance_dict.update(distance_dict2)
  return next_distance_dict
def graphGeneration(prev_G):
  prev_C = prev_G.getNodes()
  prev_E = prev_G.getDirectedEdges()
  sai1anp_type_four_key_to_node_list_dict = defaultdict(lambda: [])
  sai1anp_type_four_key_type_five_key_tuple_to_node_list_dict = defaultdict(lambda: [])
  prev_i = prev_G.getNumQIDAttributes()
  for node in prev_C:
    type_four_key = node.getTypeFourKey()
    type_five_key = node.getTypeFiveKey()
    sai1anp_type_four_key_to_node_list_dict[type_four_key].append(node)
    sai1anp_type_four_key_type_five_key_tuple_to_node_list_dict[(type_four_key, type_five_key)].append(node)
  curr_C = []
  for node in prev_C:
    type_four_key = node.getTypeFourKey()
    sai1anp_suffix = node.getSortedAttributeIndex1ANodePairList()[prev_i - 1]
    suffix_index = sai1anp_suffix[0]
    matches = []
    for i in xrange(0, suffix_index):
      for partner_node in sai1anp_type_four_key_type_five_key_tuple_to_node_list_dict[(type_four_key, i)]:
        if node != partner_node and node._getAttributeIndexSet() != partner_node._getAttributeIndexSet():
          matches.append(partner_node)
    next_matches = matches
    parent1_list = next_matches
    parent2 = node
    for parent1 in parent1_list:
      attribute_index_1a_node_pair_set1 = parent1._getAttributeIndex1ANodePairSet()
      attribute_index_1a_node_pair_set2 = parent2._getAttributeIndex1ANodePairSet()
      next_attribute_index_1a_node_pair_set = attribute_index_1a_node_pair_set1 | attribute_index_1a_node_pair_set2
      distance_dict1 = parent1.getDistanceDict()
      distance_dict2 = parent2.getDistanceDict()
      next_distance_dict = combineDistanceDicts(distance_dict1, distance_dict2)
      next_node = Node(next_attribute_index_1a_node_pair_set, next_distance_dict, False, False, parent1, parent2)
      curr_C.append(next_node)
  next_curr_C = []
  sai1anpl_tuple_to_count_dict = defaultdict(lambda: 0)
  for node in prev_C:
    sai1anpl = node.getSortedAttributeIndex1ANodePairList()
    sai1anpl_tuple = tuple(sai1anpl)
    sai1anpl_tuple_to_count_dict[sai1anpl_tuple] += 1
  for node in curr_C:
    sai1anpl = node.getSortedAttributeIndex1ANodePairList()
    no_matches = False
    num_components = len(sai1anpl)
    for i in xrange(num_components):
      prev_sai1anpl = Node.getPrevSortedAttributeIndex1ANodePairList(sai1anpl, i)
      prev_sai1anpl_tuple = tuple(prev_sai1anpl)
      if sai1anpl_tuple_to_count_dict[prev_sai1anpl_tuple] == 0:
        no_matches = True
        break
    if no_matches == False:
      next_curr_C.append(node)
  curr_E = []
  type_four_key_to_prev_node_list_dict = defaultdict(lambda: [])
  for node in prev_C:
    type_four_key = node.getTypeFourKey()
    type_four_key_to_prev_node_list_dict[type_four_key].append(node)
  key_to_curr_node_dict = {}
  for node in next_curr_C:
    sai1anpl = node.getSortedAttributeIndex1ANodePairList()
    sai1anpl_tuple = tuple(sai1anpl)
    key_to_curr_node_dict[sai1anpl_tuple] = node
  for directed_edge in prev_E:
    p = directed_edge.getOriginNode()
    q = directed_edge.getDestinationNode()
    p_type_one_key = p.getTypeOneKey()
    q_type_one_key = q.getTypeOneKey()
    r_type_four_key = p.getTypeFourKey()
    candidate_r_list = type_four_key_to_prev_node_list_dict[r_type_four_key]
    for candidate_r in candidate_r_list:
      r_type_two_key = candidate_r.getTypeTwoKey()
      a1_key = Node.formKey(p_type_one_key, r_type_two_key)
      b1_key = Node.formKey(q_type_one_key, r_type_two_key)
      if a1_key not in key_to_curr_node_dict:
        continue
      if b1_key not in key_to_curr_node_dict:
        continue
      a1 = key_to_curr_node_dict[a1_key]
      b1 = key_to_curr_node_dict[b1_key]
      edge = DirectedEdge(a1, b1)
      curr_E.append(edge)
    p_type_two_key = p.getTypeTwoKey()
    q_type_two_key = q.getTypeTwoKey()
    for candidate_r in candidate_r_list:
      r_type_one_key = candidate_r.getTypeOneKey()
      a1_key = Node.formKey(r_type_one_key, p_type_two_key)
      b1_key = Node.formKey(r_type_one_key, q_type_two_key)
      if a1_key not in key_to_curr_node_dict:
        continue
      if b1_key not in key_to_curr_node_dict:
        continue
      a1 = key_to_curr_node_dict[a1_key]
      b1 = key_to_curr_node_dict[b1_key]
      edge = DirectedEdge(a1, b1)
      curr_E.append(edge)
  pass
  curr_G = DirectedGraph(next_curr_C, curr_E, prev_i + 1)
  next_curr_E = []
  for edge in curr_E:
    node_start = edge.getOriginNode()
    node_end = edge.getDestinationNode()
    nops = curr_G.getOutgoingEdgePartnersFast(node_start)
    nop_list = list(nops)
    keep_edge = True
    for nop in nop_list:
      have_matching_partner = curr_G.haveOutgoingEdgePartner(nop, node_end)
      if have_matching_partner == True:
        keep_edge = False
        break
    if keep_edge == True:
      next_curr_E.append(edge)
  next_curr_G = DirectedGraph(next_curr_C, next_curr_E, prev_i + 1)
  return next_curr_G
def getAvgValueLength(rows, qid_index):
  num_rows = len(rows)
  length_list = []
  for row in rows:
    value = row[qid_index]
    curr_length = len(value)
    length_list.append(curr_length)
  result = sum(length_list) / (1.0 * num_rows)
  return result
stream = sys.stdin
# stream = open("tests/test01.in")
# stream = open("tests/test00.in")
# stream = open("tests/whitehouse.in")
# stream = open("tests/hospital.in")
# stream = open("tests/airsampling.in")
line = stream.readline()
line = line.rstrip("\n")
args = line.split()
csv_file_path = args[0]
csv_stream1 = open(csv_file_path, "rb")
csv_stream2 = open(csv_file_path, "rb")
line = stream.readline()
line = line.rstrip("\n")
args = line.split()
args = [string.atoi(x) for x in args]
show_suppression_info = int(args[0])
line = stream.readline()
line = line.rstrip("\n")
args = line.split()
args = [string.atoi(x) for x in args]
carry_over_num_lines = int(args[0])
line = stream.readline()
line = line.rstrip("\n")
args = line.split()
args = [string.atoi(x) for x in args]
k = int(args[0])
line = stream.readline()
line = line.rstrip("\n")
args = line.split()
args = [string.atoi(x) for x in args]
suppression_budget = int(args[0])
line = stream.readline()
line = line.rstrip("\n")
args = line.split()
args = [string.atoi(x) for x in args]
num_attributes = int(args[0])
line = stream.readline()
line = line.rstrip("\n")
args = line.split()
args = [string.atoi(x) for x in args]
num_qid_attributes = int(args[0])
qid_index_list = []
qid_tuple_list = []
for i in xrange(num_qid_attributes):
  line = stream.readline()
  line = line.rstrip("\n")
  args = line.split()
  qid_index = int(args[0])
  pre_set_type_letter = args[1]
  optional_pre_set_parameter1 = None
  optional_pre_set_parameter2 = None
  if len(args) >= 3:
    optional_pre_set_parameter1 = args[2]
  if len(args) == 4:
    optional_pre_set_parameter2 = args[3]
  qid_index_list.append(qid_index)
  qid_tuple = (qid_index, pre_set_type_letter, optional_pre_set_parameter1, optional_pre_set_parameter2)
  qid_tuple_list.append(qid_tuple)
qid_index_set = set(qid_index_list)
csv_reader = csv.reader(csv_stream2, delimiter = ",", quotechar = "|")
carry_over_row_str_list = []
for i in xrange(carry_over_num_lines):
  line = csv_stream1.readline()
  line = line.rstrip("\n")
  row_str = line
  carry_over_row_str_list.append(row_str)
  csv_reader.next()
rows = []
for row in csv_reader:
  rows.append(row)
pre_sets = []
index_to_qid_attribute_dict = {}
for qid_tuple in qid_tuple_list:
  qid_index, pre_set_type_letter, optional_pre_set_parameter1, optional_pre_set_parameter2 = qid_tuple
  attribute = Attribute(str(qid_index), qid_index)
  pre_set = None
  if pre_set_type_letter == "A":
    opsp = int(optional_pre_set_parameter1)
    avg_value_length = getAvgValueLength(rows, qid_index)
    pre_set = TypeAPreSet(attribute, opsp, avg_value_length)
  elif pre_set_type_letter == "B":
    opsp1 = None
    opsp2 = None
    if optional_pre_set_parameter1 == "True":
      opsp1 = True
    elif optional_pre_set_parameter1 == "False":
      opsp1 = False
    opsp2 = int(optional_pre_set_parameter2) if optional_pre_set_parameter2 != None else 1
    avg_value_length = getAvgValueLength(rows, qid_index)
    pre_set = TypeBPreSet(attribute, opsp1, avg_value_length, opsp2)
  elif pre_set_type_letter == "C":
    pre_set = TypeCPreSet(attribute)
  elif pre_set_type_letter == "D":
    opsp = int(optional_pre_set_parameter1)
    pre_set = TypeDPreSet(attribute, opsp)
  elif pre_set_type_letter == "E":
    raise Exception()
  elif pre_set_type_letter == "F":
    raise Exception()
  elif pre_set_type_letter == "G":
    pre_set = TypeGPreSet(attribute)
  else:
    raise Exception()
  attribute.setPreSet(pre_set)
  pre_sets.append(pre_set)
  index_to_qid_attribute_dict[qid_index] = attribute
nodes = []
edges = []
for pre_set in pre_sets:
  curr_nodes = pre_set.getNodes()
  curr_edges = pre_set.getDirectedEdges()
  nodes += curr_nodes
  edges += curr_edges
directed_graph = DirectedGraph(nodes, edges, 1)
class PriorityQueue:
    def  __init__(self):
        self.heap = []
    def push(self, item, priority):
        pair = (priority,item)
        heapq.heappush(self.heap,pair)
    def pop(self):
        (priority,item) = heapq.heappop(self.heap)
        return item
    def isEmpty(self):
        return len(self.heap) == 0
def kAnonymize(rows, k, suppression_budget, num_quasi_identifiers, num_attributes, index_to_qid_attribute_dict, G1, qid_index_set):
  if len(rows) < k:
    raise Exception()
  C1 = G1.getNodes()
  E1 = G1.getDirectedEdges()
  pq = PriorityQueue()
  n = num_quasi_identifiers
  curr_G = G1.copy()
  curr_C = curr_G.getNodes()
  curr_E = curr_G.getDirectedEdges()
  for i in xrange(n):
    node_to_frequency_set_dict = {}
    roots = [x for x in curr_C if curr_G.getIngoingDegree(x) == 0]
    for node in roots:
      pq.push(node, node.getHeight())
    while pq.isEmpty() == False:
      node = pq.pop()
      if node.isMarked() == False:
        frequency_set = None
        curr_qid_index_set = node._getAttributeIndexSet()
        if curr_G.getIngoingDegree(node) == 0:
          frequency_set = FrequencySet.determineFrequencySetFromScratch(rows, node, num_attributes, index_to_qid_attribute_dict, curr_qid_index_set)
          node_to_frequency_set_dict[node] = frequency_set
        else:
          parent = curr_G.getVisitedNeighbors(node)[0]
          parent_frequency_set = node_to_frequency_set_dict[parent]
          frequency_set = FrequencySet.determineFrequencySetUsingParent(rows, node, parent_frequency_set, num_attributes, index_to_qid_attribute_dict, curr_qid_index_set)
          node_to_frequency_set_dict[node] = frequency_set
        is_k_anonymous, suppression_cost = frequency_set.satisfiesKAnonymityGivenSuppressionBudget(k, suppression_budget)
        if is_k_anonymous == True:
          direct_neighbors = curr_G.getOutgoingEdgePartners(node)
          for neighbor in direct_neighbors:
            neighbor.setMarked(True)
        else:
          direct_neighbors = curr_G.getOutgoingEdgePartners(node)
          curr_G.removeNodeAndAssociatedDirectedEdges(node)
          for neighbor in direct_neighbors:
            pq.push(neighbor, neighbor.getHeight())
      node.setIsVisited(True)
    if i != n - 1:
      curr_G = graphGeneration(curr_G)
      curr_C = curr_G.getNodes()
      curr_E = curr_G.getDirectedEdges()
  return curr_G
G = kAnonymize(rows, k, suppression_budget, num_qid_attributes, num_attributes, index_to_qid_attribute_dict, directed_graph, qid_index_set)
nodes = G.getNodes()
if len(nodes) == 0:
  raise Exception()
wil_node_pairs = [(x.getTotalWeightedInformationLoss(), x) for x in nodes]
wil_values = [x[0] for x in wil_node_pairs]
min_wil_value = min(wil_values)
candidate_nodes = [x[1] for x in wil_node_pairs if x[0] == min_wil_value]
chosen_node = candidate_nodes[0]
def projectOntoRows(rows, generalization_node, index_to_qid_attribute_dict, num_attributes):
  distance_dict = generalization_node.getDistanceDict()
  masked_rows = []
  for row in rows:
    value_list = []
    for i in xrange(num_attributes):
      original_value = row[i]
      value = None
      if i in index_to_qid_attribute_dict:
        attribute = index_to_qid_attribute_dict[i]
        pre_set = attribute.getPreSet()
        distance = distance_dict[attribute]
        value = pre_set.maskAttributeValue(original_value, distance)
      else:
        value = original_value
      value_list.append(value)
    masked_rows.append(value_list)
  return masked_rows
def suppressRowsAndGetOneIndexedIndices(rows, node, num_atributes, index_to_qid_attribute_dict, qid_index_set, k, suppression_budget):
  frequency_set = FrequencySet.determineFrequencySetFromScratch(rows, node, num_attributes, index_to_qid_attribute_dict, qid_index_set)
  is_k_anonymous, suppression_cost = frequency_set.satisfiesKAnonymityGivenSuppressionBudget(k, suppression_budget)
  masked_row_qid_tuple_to_count_dict = frequency_set.getMaskedRowQIDTupleToCountDict()
  masked_rows = FrequencySet.getQIDOnlyRows(rows, node, num_attributes, index_to_qid_attribute_dict, qid_index_set)
  masked_qid_row_dict_list = FrequencySet.getMaskedQIDRowDictList(masked_rows, node, num_attributes, index_to_qid_attribute_dict, qid_index_set)
  suppressed_row_zero_indexed_indices = []
  for i in xrange(len(rows)):
    masked_row_qid_dict = masked_qid_row_dict_list[i]
    masked_row_qid_tuple = FrequencySet.maskedRowQIDDictToTuple(masked_row_qid_dict, qid_index_set)
    if masked_row_qid_tuple_to_count_dict[masked_row_qid_tuple] < k:
      suppressed_row_zero_indexed_indices.append(i)
  suppressed_row_one_indexed_indices = [x + 1 for x in suppressed_row_zero_indexed_indices]
  sorted_suppressed_row_one_indexed_indices = sorted(suppressed_row_one_indexed_indices)
  row_index_set = set(suppressed_row_zero_indexed_indices)
  next_rows = []
  for i in xrange(len(rows)):
    row = rows[i]
    if i not in row_index_set:
      next_rows.append(row)
  result = next_rows, sorted_suppressed_row_one_indexed_indices
  return result
result = suppressRowsAndGetOneIndexedIndices(rows, chosen_node, num_attributes, index_to_qid_attribute_dict, qid_index_set, k, suppression_budget)
next_rows, suppressed_row_one_indexed_indices = result
result = projectOntoRows(next_rows, chosen_node, index_to_qid_attribute_dict, num_attributes)
for row_str in carry_over_row_str_list:
  print row_str
components_list = []
for masked_row in result:
  components = ",".join(masked_row)
  components_list.append(components)
components_list_str = string.join(components_list, "\r\n")
print components_list_str,
if show_suppression_info == 1:
  print "\r\n",
  print len(suppressed_row_one_indexed_indices)
  index_str_list = [str(x) for x in suppressed_row_one_indexed_indices]
  suppressed_row_index_str = string.join(index_str_list, " ")
  print suppressed_row_index_str,
elif show_suppression_info == 0:
  pass
else:
  raise Exception()
