# 2015-08-28

# have priority queue operations in-lined

# have exponentiation in-lined

# have dictionary replaced with an array

import heapq

from collections import defaultdict

import multiprocessing
import sys

def haveItemInItemCountMap(item_count_map, item_id):
  result = item_count_map[item_id] > 0
  # print (item_id, result)
  return result
def createItemCountMap(num_primitive_items):
  # assume tree is balanced
  max_item_id = 3 * num_primitive_items
  return [0] * max_item_id
def addItemToItemCountMap(item_count_map, item_id):
  # item_count_map is an array list
  item_count_map[item_id] += 1
def removeItemFromItemCountMap(item_count_map, item_id):
  item_count_map[item_id] -= 1
def removeItemsFromItemCountMap(item_count_map, item_id_list):
  for item_id in item_id_list:
    item_count_map[item_id] -= 1

id_count_map = createItemCountMap(100000)

def getTopicDistance(topic_id, topic_id_to_point_dict, query_point):
  point = topic_id_to_point_dict[topic_id]
  distance = getDistance(point, query_point)
  return distance
def getQuestionDistance(question_id, question_id_to_topic_id_dict, topic_id_to_point_dict, query_point):
  topic_id_list = question_id_to_topic_id_dict[question_id]
  point_list = [topic_id_to_point_dict[x] for x in topic_id_list]
  distance_list = [getDistance(x, query_point) for x in point_list]
  min_distance = min(distance_list)
  return min_distance
def getTopicKey(topic_id, topic_id_to_point_dict, query_point):
  distance = getTopicDistance(topic_id, topic_id_to_point_dict, query_point)
  id_value = topic_id
  result = (-1 * distance, id_value)
  return result
def getQuestionKey(question_id, question_id_to_topic_id_dict, topic_id_to_point_dict, query_point):
  distance = getQuestionDistance(question_id, question_id_to_topic_id_dict, topic_id_to_point_dict, query_point)
  id_value = question_id
  result = (-1 * distance, id_value)
  return result
def compare_items(pair_a, pair_b):
  dist_a = -1 * pair_a[0]
  id_a = pair_a[1]
  dist_b = -1 * pair_b[0]
  id_b = pair_b[1]
  if dist_a < dist_b - 0.001:
    return -1
  elif dist_a > dist_b + 0.001:
    return 1
  else:
    if id_a > id_b:
      return -1
    elif id_a < id_b:
      return 1
    elif id_a == id_b:
      return 0
import math
def getDistance(point1, point2):
  x1, y1 = point1
  x2, y2 = point2
  change_x = x2 - x1
  change_y = y2 - y1
  distance = math.sqrt(change_x * change_x + change_y * change_y)
  return distance
def getDistanceComponent(point1, point2, axis):
  x1, y1 = point1
  x2, y2 = point2
  change_x = x2 - x1
  change_y = y2 - y1
  if axis == 0:
    distance = abs(change_x)
    return distance
  elif axis == 1:
    distance = abs(change_y)
    return distance
class KNearestNeighbor:
  def __init__(self, query_point, heap, topic_id_to_point_dict, k = 100):
    self.query_point = query_point
    # self.close_item_pq = close_item_pq
    self.heap = heap
    self.topic_id_to_point_dict = topic_id_to_point_dict
    self.k = k
  def getCloseItems(self):
    # result = (self.close_item_pq).toList()
    pair_list = self.heap
    items = [x[1] for x in pair_list]
    result = items
    return result
  def getFarthestCloseDistance(self):
    if self.getNumCloseItems() == 0:
      return float("inf")
    else:
      # result = (self.close_item_pq).peek()
      heap = self.heap
      pair = heap[0]
      result = pair
      priority, item = result
      distance = -1 * priority[0]
      id_value = priority[1]
      return distance
  def addCloseItem(self, close_item):
    id_value = close_item
    point_location = self.topic_id_to_point_dict[id_value]
    query_point = self.query_point
    distance = getDistance(query_point, point_location)
    priority = (-1 * distance, id_value)
    # (self.close_item_pq).push(close_item, priority)
    heap = self.heap
    item = close_item
    pair = (priority,item)
    heapq.heappush(heap,pair)
  # return a (priority, item) pair
  def removeCloseItem(self):
    # (self.close_item_pq).pop()
    heap = self.heap
    result = heapq.heappop(heap)
    # (priority,item) = result
    return result
  def getNumCloseItems(self):
    # return (self.close_item_pq).getSize()
    heap = self.heap
    return len(heap)
  def addAndRemoveIfNecessary(self, close_item):
    do_remove = self.isFull() == True and self.passesThresholdForFarthestCloseItem(close_item) == False
    self.addCloseItem(close_item)
    if do_remove == True:
      self.removeCloseItem()
  def isFull(self):
    return self.getNumCloseItems() >= self.k
  def passesThresholdForFarthestCloseItem(self, close_item):
    distance = self.getFarthestCloseDistance()
    query_point = self.query_point
    topic_id_value = close_item
    point_location = (self.topic_id_to_point_dict)[topic_id_value]
    curr_distance = getDistance(query_point, point_location)
    return curr_distance > distance + 0.001
class TopicKNearestNeighbor(KNearestNeighbor):
  def __init__(self, query_point, close_item_pq, topic_id_to_point_dict, k = 100):
    KNearestNeighbor.__init__(self, query_point, close_item_pq, topic_id_to_point_dict, k)
class QuestionKNearestNeighbor(KNearestNeighbor):
  def __init__(self, query_point, close_item_pq, topic_id_to_point_dict, question_id_to_topic_id_dict, k = 100):
    KNearestNeighbor.__init__(self, query_point, close_item_pq, topic_id_to_point_dict, k)
    self.question_id_to_topic_id_dict = question_id_to_topic_id_dict
  def addCloseItem(self, close_item, question_key):
    question_id = close_item
    query_point = self.query_point
    priority = question_key
    # (self.close_item_pq).push(close_item, priority)
    item = close_item
    pair = (priority,item)
    heap = self.heap
    heapq.heappush(heap,pair)
    addItemToItemCountMap(id_count_map, question_id)
  def addMultipleAndRemoveIfNecessary(self, close_items, topic_id):
    question_id_values = close_items
    for question_id_value in question_id_values:
      self.addAndRemoveIfNecessary(question_id_value, topic_id)
  def addAndRemoveIfNecessary(self, question_id_value, topic_id):
    query_location = self.query_point
    question_key = (-1 * getTopicDistance(topic_id, self.topic_id_to_point_dict, query_location), question_id_value)
    # do_add = self.haveItem(question_id_value) == False
    # do_add = True
    do_add = haveItemInItemCountMap(id_count_map, question_id_value) == False
    do_remove = self.isFull() == True and self.passesThresholdForFarthestCloseItem(question_id_value, question_key) == False
    if do_add == True:
      # do_remove = self.isFull() == True
      self.addCloseItem(question_id_value, question_key)
      if do_remove == True:
        self.removeCloseItem()
  def passesThresholdForFarthestCloseItem(self, question_id_value, question_key):
    distance = self.getFarthestCloseDistance()
    query_point = self.query_point
    distance = -1 * question_key[0]
    curr_distance = distance
    return curr_distance > distance + 0.001
  def removeCloseItem(self):
    result = KNearestNeighbor.removeCloseItem(self)
    (priority,item) = result
    # (self.close_item_pq).pop()
    heap = self.heap
    item_id = item
    removeItemFromItemCountMap(id_count_map, item_id)
class RTreeNode:
  def __init__(self, parent, entries, is_leaf):
    self.parent = parent
    self.is_leaf = is_leaf
    self.m = 8
    self.M = 16
    self.child_to_entry_dict = {}
    for entry in entries:
      curr_child = entry.getChild()
      (self.child_to_entry_dict)[curr_child] = entry
  def getParent(self):
    return self.parent
  def getEntries(self):
    return (self.child_to_entry_dict).values()
  def getChildren(self):
    return (self.child_to_entry_dict).keys()
  def getNumEntries(self):
    return len(self.child_to_entry_dict)
  def getNumChildren(self):
    return self.getNumEntries()
  def setParent(self, node):
    self.parent = node
  def isTraditionalLeafNode(self):
    is_traditional_leaf_node = self.getNumEntries() == 0
    return is_traditional_leaf_node
  def isLeafNode(self):
    is_leaf_node = (self.getParent() == None and self.getNumChildren() == 0) or (self.getNumChildren() != 0 and self.getEntries()[0].getChild().getNumEntries() == 0)
    return is_leaf_node
  def setIsLeafNode(self, is_leaf):
    self.is_leaf = is_leaf
  def addEntry(self, entry):
    curr_child = entry.getChild()
    (self.child_to_entry_dict)[curr_child] = entry
  def removeEntry(self, entry):
    curr_child = entry.getChild()
    (self.child_to_entry_dict).pop(curr_child)
  def getMinimumNumEntriesPerNode(self):
    return self.m
  def getMaximumNumEntriesPerNode(self):
    return self.M
  def isFull(self):
    return self.getNumEntries() >= self.getMaximumNumEntriesPerNode()
  def isUnderfull(self):
    return self.getNumEntries() < self.getMinimumNumEntriesPerNode()
  def retrieveEntryForChild(self, node):
    return (self.child_to_entry_dict)[node]
  def toString(self):
    return str(self.getEntries())
class RTreeEntry:
  def __init__(self, mbr, child, id_value):
    self.mbr = mbr
    self.child = child
    self.id_value = id_value
    # print "id value:", id_value
  def getMBR(self):
    return self.mbr
  def setMBR(self, mbr):
    self.mbr = mbr
  def getChild(self):
    return self.child
  def setChild(self, node):
    self.child = node
  def getIDValue(self):
    return self.id_value
class MBR:
  def __init__(self, upper_left, lower_right):
    self.upper_left = upper_left
    self.lower_right = lower_right
  def isRaw(self):
    return False
  def isComposite(self):
    return False
  def getUpperLeft(self):
    return self.upper_left
  def getLowerRight(self):
    return self.lower_right
  def getCenter(self):
    upper_left = self.getUpperLeft()
    lower_right = self.getLowerRight()
    x1, y1 = upper_left
    x2, y2 = lower_right
    x_center = (x1 + x2) / (1.0 * 2)
    y_center = (y1 + y2) / (1.0 * 2)
    center = (x_center, y_center)
    return center
class RawMBR(MBR):
  def __init__(self, upper_left, lower_right, contained_item):
    MBR.__init__(self, upper_left, lower_right)
    self.contained_item = contained_item
  def isRaw(self):
    return True
  @staticmethod
  def makeMBRFromPoint(point):
    upper_left = point
    lower_right = point
    result_mbr = RawMBR(upper_left, lower_right, point)
    return result_mbr
  def getContainedItem(self):
    return self.contained_item
  def getMBRList(self):
    return [self]
class CompositeMBR(MBR):
  def __init__(self, upper_left, lower_right, mbr_list):
    MBR.__init__(self, upper_left, lower_right)
    self.mbr_list = mbr_list
  def getMBRList(self):
    return self.mbr_list
  def isComposite(self):
    return True
  @staticmethod
  def makeMBR(component_mbr_list):
    upper_left_points = [x.getUpperLeft() for x in component_mbr_list]
    lower_right_points = [x.getLowerRight() for x in component_mbr_list]
    points = upper_left_points + lower_right_points
    x_values = [x[0] for x in points]
    y_values = [x[1] for x in points]
    min_x_value = min(x_values)
    max_x_value = max(x_values)
    min_y_value = min(y_values)
    max_y_value = max(y_values)
    overall_upper_left = (min_x_value, min_y_value)
    overall_lower_right = (max_x_value, max_y_value)
    result_mbr = CompositeMBR(overall_upper_left, overall_lower_right, component_mbr_list)
    return result_mbr
class Point:
  def __init__(self, x, y, id_value):
    self.x = x
    self.y = y
    self.id_value = id_value
  @staticmethod
  def toPoint(mbr):
    return mbr.getUpperLeft()
  def getX(self):
    return self.x
  def getY(self):
    return self.y
  def getIDValue(self):
    return self.id_value
  def toLocationTuple(self):
    x = self.getX()
    y = self.getY()
    location = (x, y)
    return location
import string
class RTree:
  @staticmethod
  def construct(points):
    entry_id_value = 0
    tree = RTree(entry_id_value)
    entry_id_value += 1
    m = 8
    M = 16
    r = len(points)
    P = int(math.ceil(r / (1.0 * M)))
    S = int(math.ceil(math.sqrt(math.ceil(r / (1.0 * M)))))
    ordered_axes = None
    x_values = [x.getX() for x in points]
    min_x_value = min(x_values)
    max_x_value = max(x_values)
    x_separation = max_x_value - min_x_value
    y_values = [x.getY() for x in points]
    min_y_value = min(y_values)
    max_y_value = max(y_values)
    y_separation = max_y_value - min_y_value
    if x_separation >= y_separation:
      ordered_axes = [0, 1]
    elif x_separation < y_separation:
      ordered_axes = [1, 0]
    first_axis = ordered_axes[0]
    second_axis = ordered_axes[1]
    curr_overall_primary_run = []
    primary_slice_point_list_list = RTree.createPrimarySlices(points, first_axis, r, P, S, m, M)
    for primary_slice_point_list in primary_slice_point_list_list:
      curr_overall_secondary_run = []
      secondary_slice_point_list_list = RTree.createSecondarySlices(primary_slice_point_list, second_axis, r, P, S, m, M)
      for secondary_slice_point_list in secondary_slice_point_list_list:
        curr_overall_secondary_run = RTree.incorporatePointRun(curr_overall_secondary_run, secondary_slice_point_list, second_axis)
      curr_overall_primary_run = RTree.incorporatePointRun(curr_overall_primary_run, curr_overall_secondary_run, first_axis)
    RTree.constructHelperA(tree, curr_overall_primary_run, r, P, S, m, M, entry_id_value)
    return tree
  @staticmethod
  def createPrimarySlices(points, axis, r, P, S, m, M):
    point_list_list = []
    next_points = sorted(points, key = lambda x: x.getX() if axis == 0 else x.getY())
    count = int(math.ceil(len(next_points) / (1.0 * (S * M))))
    for i in range(count):
      curr_points = next_points[i * (S * M) : (i + 1) * (S * M)]
      point_list_list.append(curr_points)
    return point_list_list
  @staticmethod
  def incorporatePointRun(conglomerate_run, run, axis):
    return conglomerate_run + run
  @staticmethod
  def createSecondarySlices(primary_slice_points, axis, r, P, S, m, M):
    point_list_list = []
    next_points = sorted(primary_slice_points, key = lambda x: x.getX() if axis == 0 else x.getY())
    count = int(math.ceil(len(next_points) / (1.0 * M)))
    for i in range(count):
      curr_points = next_points[i * M : (i + 1) * M]
      point_list_list.append(curr_points)
    return point_list_list
  @staticmethod
  def constructHelperA(tree, ordered_points, r, P, S, m, M, entry_id_value):
    ordered_child_entries = []
    for point in ordered_points:
      x = point.getX()
      y = point.getY()
      location = (x, y)
      node = RTreeNode(None, [], True)
      mbr = RawMBR(location, location, point)
      entry = RTreeEntry(mbr, node, entry_id_value)
      entry_id_value += 1
      ordered_child_entries.append(entry)
    RTree.constructHelperB(tree, ordered_child_entries, r, P, S, m, M, entry_id_value)
  @staticmethod
  def constructHelperB(tree, ordered_child_entries, r, P, S, m, M, entry_id_value):
    if len(ordered_child_entries) == 0:
      return
    next_ordered_child_entries = []
    count = int(math.ceil(len(ordered_child_entries) / (1.0 * M)))
    for i in range(count):
      curr_child_entries = ordered_child_entries[i * M : (i + 1) * M]
      curr_mbr_list = [x.getMBR() for x in curr_child_entries]
      node = RTreeNode(None, curr_child_entries, False)
      mbr = CompositeMBR.makeMBR(curr_mbr_list)
      entry = RTreeEntry(mbr, node, entry_id_value)
      entry_id_value += 1
      for child_entry in curr_child_entries:
        curr_node = child_entry.getChild()
        curr_node.setParent(node)
        node.addEntry(child_entry)
      next_ordered_child_entries.append(entry)
    if len(next_ordered_child_entries) == 1:
      child_entry = next_ordered_child_entries[0]
      node = child_entry.getChild()
      root_entry = tree.getRootEntry()
      root_entry.setChild(node)
      curr_mbr_list = [x.getMBR() for x in ordered_child_entries]
      mbr = CompositeMBR.makeMBR(curr_mbr_list)
      root_entry.setMBR(mbr)
      return
    return RTree.constructHelperB(tree, next_ordered_child_entries, r, P, S, m, M, entry_id_value)
  def __init__(self, base_entry_id_value):
    root_node = RTreeNode(None, [], True)
    root_mbr = CompositeMBR(None, None, None)
    root_entry = RTreeEntry(root_mbr, root_node, base_entry_id_value)
    self.setRootEntry(root_entry)
  def getRootEntry(self):
    return self.root_entry
  def setRootEntry(self, root_entry):
    self.root_entry = root_entry
  def setRoot(self, node):
    self.root = node
  def getRoot(self):
    return self.root
  def TopicKNearestNeighborBestFirstSearch(self, point, TopicKNearest, k, point_to_id_dict):
    root_entry = self.getRootEntry()
    # entry_pq = PriorityQueue()
    heap = []
    distance = RTree.twoDimensionalMinDist(point, root_entry.getMBR())
    priority = distance
    # entry_pq.push(root_entry, priority)
    item = root_entry
    pair = (priority,item)
    heapq.heappush(heap,pair)
    # print entry_pq
    # raise Exception()
    return self.TopicKNearestNeighborBestFirstSearchHelper(heap, point, TopicKNearest, k, point_to_id_dict)
  # @profile
  def TopicKNearestNeighborBestFirstSearchHelper(self, heap, point, TopicKNearest, k, point_to_id_dict):
      # while entry_pq.getSize() != 0:
      while len(heap) != 0:
        # entry = entry_pq.pop()
        (priority,item) = heapq.heappop(heap)
        entry = item
        node = entry.getChild()
        if node.isTraditionalLeafNode():
          mbr = entry.getMBR()
          dist = getDistance(point, Point.toPoint(mbr))
          if dist <= TopicKNearest.getFarthestCloseDistance() + 0.001 or TopicKNearest.isFull() == False:
            close_item = entry.getMBR().getContainedItem()
            id_value = close_item.getIDValue()
            TopicKNearest.addAndRemoveIfNecessary(id_value)
          else:
            break
        elif node.isLeafNode():
          entries = node.getEntries()
          for entry in entries:
            min_dist_value = RTree.twoDimensionalMinDist(point, entry.getMBR())
            priority = min_dist_value
            if not (min_dist_value > TopicKNearest.getFarthestCloseDistance() + 0.001 and TopicKNearest.isFull() == True):
              # entry_pq.push(entry, priority)
              item = entry
              pair = (priority,item)
              heapq.heappush(heap,pair)
        elif node.isLeafNode() == False:
          entries = node.getEntries()
          for entry in entries:
            min_dist_value = RTree.twoDimensionalMinDist(point, entry.getMBR())
            priority = min_dist_value
            if not (min_dist_value > TopicKNearest.getFarthestCloseDistance() + 0.001 and TopicKNearest.isFull() == True):
              # entry_pq.push(entry, priority)
              item = entry
              pair = (priority,item)
              heapq.heappush(heap,pair)
  def QuestionKNearestNeighborBestFirstSearch(self, point, QuestionKNearest, k, topic_id_to_question_id_dict):
    root_entry = self.getRootEntry()
    # entry_pq = PriorityQueue()
    heap = []
    distance = RTree.twoDimensionalMinDist(point, root_entry.getMBR())
    priority = distance
    # entry_pq.push(root_entry, priority)
    item = root_entry
    pair = (priority,item)
    heapq.heappush(heap,pair)
    return self.QuestionKNearestNeighborBestFirstSearchHelper(heap, point, QuestionKNearest, k, topic_id_to_question_id_dict)
  def QuestionKNearestNeighborBestFirstSearchHelper(self, heap, point, QuestionKNearest, k, topic_id_to_question_id_dict):
      # while entry_pq.getSize() != 0:
      while len(heap) != 0:
        # entry = entry_pq.pop()
        (priority,item) = heapq.heappop(heap)
        entry = item
        node = entry.getChild()
        if node.isTraditionalLeafNode():
          mbr = entry.getMBR()
          dist = getDistance(point, Point.toPoint(mbr))
          if dist <= QuestionKNearest.getFarthestCloseDistance() + 0.001 or QuestionKNearest.isFull() == False:
            close_item = entry.getMBR().getContainedItem()
            topic_id = close_item.getIDValue()
            id_values = topic_id_to_question_id_dict[topic_id]
            QuestionKNearest.addMultipleAndRemoveIfNecessary(id_values, topic_id)
          else:
            break
        elif node.isLeafNode():
          entries = node.getEntries()
          for entry in entries:
            min_dist_value = RTree.twoDimensionalMinDist(point, entry.getMBR())
            priority = min_dist_value
            if not (min_dist_value > QuestionKNearest.getFarthestCloseDistance() + 0.001 and QuestionKNearest.isFull() == True):
              # entry_pq.push(entry, priority)
              item = entry
              pair = (priority,item)
              heapq.heappush(heap,pair)
        elif node.isLeafNode() == False:
          entries = node.getEntries()
          for entry in entries:
            min_dist_value = RTree.twoDimensionalMinDist(point, entry.getMBR())
            priority = min_dist_value
            if not (min_dist_value > QuestionKNearest.getFarthestCloseDistance() + 0.001 and QuestionKNearest.isFull() == True):
              # entry_pq.push(entry, priority)
              item = entry
              pair = (priority,item)
              heapq.heappush(heap,pair)
  @staticmethod
  def genBranchList(query_point, entry):
    node = entry.getChild()
    entries = (node.getEntries())[ : ]
    return entries
  @staticmethod
  def sortBranchList(query_point, branchList):
    entries = branchList[ : ]
    entries.sort(key = lambda x: RTree.twoDimensionalMinDist(query_point, x.getMBR()))
    return entries
  @staticmethod
  def kNNPruneBranchList(kNearest, branchList, point):
    if len(branchList) == 0:
      return []
    entries = branchList
    entries_to_keep = []
    farthest_close_dist = kNearest.getFarthestCloseDistance()
    for entry in entries:
      min_dist_value = RTree.twoDimensionalMinDist(point, entry.getMBR())
      do_prune = False
      if min_dist_value > farthest_close_dist + 0.001 and kNearest.isFull() == True:
        do_prune = True
        pass
      if do_prune == False:
        entries_to_keep.append(entry)
    return entries_to_keep
  @staticmethod
  def twoDimensionalMinDist(p, mbr):
    p1, p2 = p
    """
    p1 = p[0]
    p2 = p[1]
    """
    upper_left = mbr.getUpperLeft()
    lower_right = mbr.getLowerRight()
    """
    x1, y1 = upper_left
    x2, y2 = lower_right
    s1, s2 = (x1, y1)
    t1, t2 = (x2, y2)
    """
    s1, s2 = upper_left
    t1, t2 = lower_right
    r1 = None
    r2 = None
    if p1 < s1:
      r1 = s1
    elif p1 > t1:
      r1 = t1
    else:
      r1 = p1
    if p2 < s2:
      r2 = s2
    elif p2 > t2:
      r2 = t2
    else:
      r2 = p2
    term1 = p1 - r1
    term2 = p2 - r2
    min_dist_squared = term1 * term1 + term2 * term2
    min_dist = math.sqrt(min_dist_squared)
    return min_dist
import sys
import string
stream = sys.stdin
# stream = open("../tests/official/test9.in")
line = stream.readline()
line = line.rstrip("\n")
args = line.split(" ")
args = [string.atol(x) for x in args if x != ""]
T = int(args[0])
Q = int(args[1])
N = int(args[2])
topics = []
questions = []
queries = []
for i in range(T):
  line = stream.readline()
  line = line.rstrip("\n")
  args = line.split(" ")
  id_value = int(args[0])
  x = float(args[1])
  y = float(args[2])
  topic = (id_value, x, y)
  topics.append(topic)
for i in range(Q):
  line = stream.readline()
  line = line.rstrip("\n")
  args = line.split(" ")
  args = [string.atol(x) for x in args if x != ""]
  id_value = int(args[0])
  num_topics = int(args[1])
  topic_id_values = None
  if num_topics != 0:
    topic_id_values = [int(x) for x in args[2 : ]]
  question = (id_value, num_topics, topic_id_values)
  questions.append(question)
for i in range(N):
  line = stream.readline()
  line = line.rstrip("\n")
  args = line.split(" ")
  args = [x for x in args if x != ""]
  first_arg = args[0]
  remaining_args = args[1 : ]
  query_char = first_arg
  is_topic_query = query_char == "t"
  is_question_query = query_char == "q"
  num_items = int(remaining_args[0])
  x = float(remaining_args[1])
  y = float(remaining_args[2])
  query = (is_topic_query, num_items, x, y)
  queries.append(query)
from collections import defaultdict
point_to_id_dict = defaultdict(list)
topic_id_to_question_id_dict = defaultdict(list)
question_id_to_topic_id_dict = defaultdict(list)
topic_id_to_point_dict = {}
points = []
for topic in topics:
  id_value, x, y = topic
  location = (x, y)
  do_stop = False
  point = Point(location[0], location[1], id_value)
  points.append(point)
  point_to_id_dict[location].append(id_value)
  topic_id_to_point_dict[id_value] = location
topic_tree = RTree.construct(points)
for question in questions:
  id_value, num_topics, topic_id_values = question
  if num_topics == 0:
    topic_id_values = []
  for topic_id in topic_id_values:
    topic_id_to_question_id_dict[topic_id].append(id_value)
  question_id_to_topic_id_dict[id_value] = topic_id_values
question_associated_points = []
# @profile
def handleQuery(query, topic_id_to_point_dict, question_id_to_topic_id_dict):
  is_topic_query, num_items, x, y = query
  points = None
  if is_topic_query == True:
    location = (x, y)
    k = num_items
    # entry_pq = PriorityQueue()
    heap = []
    k_nearest_result = TopicKNearestNeighbor(location, heap, topic_id_to_point_dict, k)
    topic_tree.TopicKNearestNeighborBestFirstSearch(location, k_nearest_result, k, point_to_id_dict)
    flat_id_values = k_nearest_result.getCloseItems()
    unique_id_values = flat_id_values
    tagged_topic_key_list = [(x, getTopicKey(x, topic_id_to_point_dict, location)) for x in unique_id_values]
    sorted_tagged_topic_key_list = sorted(tagged_topic_key_list, cmp = lambda x, y: compare_items(x[1], y[1]))
    sorted_topic_id_list = [x[0] for x in sorted_tagged_topic_key_list]
    # sorted_topic_id_list = list(reversed(unique_id_values))
    culled_sorted_topic_id_list = sorted_topic_id_list[ : num_items]
    # culled_sorted_topic_id_list = sorted_topic_id_list
    culled_sorted_topic_id_str_list = [str(x) for x in culled_sorted_topic_id_list]
    return string.join(culled_sorted_topic_id_str_list, " ")
  elif is_topic_query == False:
    location = (x, y)
    k = num_items
    # entry_pq = PriorityQueue()
    heap = []
    k_nearest_result = QuestionKNearestNeighbor(location, heap, topic_id_to_point_dict, question_id_to_topic_id_dict, k)
    topic_tree.QuestionKNearestNeighborBestFirstSearch(location, k_nearest_result, k, topic_id_to_question_id_dict)
    flat_question_id_values = k_nearest_result.getCloseItems()
    removeItemsFromItemCountMap(id_count_map, flat_question_id_values)
    unique_id_values = flat_question_id_values
    tagged_question_key_list = [(x, getQuestionKey(x, question_id_to_topic_id_dict, topic_id_to_point_dict, location)) for x in unique_id_values]
    sorted_tagged_question_key_list = sorted(tagged_question_key_list, cmp = lambda x, y: compare_items(x[1], y[1]))
    sorted_question_id_list = [x[0] for x in sorted_tagged_question_key_list]
    # sorted_question_id_list = list(reversed(unique_id_values))
    culled_sorted_question_id_list = sorted_question_id_list[ : num_items]
    # culled_sorted_question_id_list = sorted_question_id_list
    culled_sorted_question_id_str_list = [str(x) for x in culled_sorted_question_id_list]
    return string.join(culled_sorted_question_id_str_list, " ")
# print item_count_map
for query in queries:
  print handleQuery(query, topic_id_to_point_dict, question_id_to_topic_id_dict)
