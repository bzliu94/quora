# 2016-11-29

import sys
import heapq
from collections import deque
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
    def peek(self):
      heap = self.heap
      pair = heap[0]
      result = pair
      return result
    def toList(self):
      pair_list = self.heap
      items = [x[1] for x in pair_list]
      return items
    def getSize(self):
      return len(self.heap)
import math
def getDistance(point1, point2):
  x1, y1 = point1
  x2, y2 = point2
  change_x = x2 - x1
  change_y = y2 - y1
  distance = math.sqrt(change_x ** 2 + change_y ** 2)
  return distance
class RTreeNode:
  def __init__(self, parent, entries, is_leaf, entry = None, split_history_root_dimension = None, is_supernode = False):
    self.parent = parent
    self.is_leaf = is_leaf
    self.m = 8
    self.M = 16
    self.child_to_entry_dict = {}
    for curr_entry in entries:
      curr_child = curr_entry.getChild()
      (self.child_to_entry_dict)[curr_child] = curr_entry
    self.split_history_root_dimension = split_history_root_dimension
    self.is_supernode = is_supernode
    self.entry = entry
  def getEntry(self):
    return self.entry
  def setEntry(self, entry):
    self.entry = entry
  def isSuperNode(self):
    return self.is_supernode
  def setToSuperNode(self, is_supernode):
    self.is_supernode = is_supernode
  def getSplitHistoryRootDimension(self):
    return self.split_history_root_dimension
  def setSplitHistoryRootDimension(self, dim):
    self.split_history_root_dimension = dim
  def getParent(self):
    return self.parent
  def getEntries(self):
    return (self.child_to_entry_dict).values()
  def getEntryForChild(self, child_node):
    return (self.child_to_entry_dict)[child_node]
  def getChildren(self):
    return (self.child_to_entry_dict).keys()
  def getNumEntries(self):
    return len(self.child_to_entry_dict)
  def getNumChildren(self):
    return self.getNumEntries()
  def setParent(self, node):
    self.parent = node
  def isNonTraditionalLeafNode(self):
    is_non_traditional_leaf_node = (self.getParent() == None and self.getNumChildren() == 0) or (self.getNumChildren() != 0 and False not in [x.getChild().getNumEntries() == 0 for x in self.getEntries()])
    return is_non_traditional_leaf_node
  def isLeafNode(self):
    is_leaf_node = self.getNumChildren() == 0
    return is_leaf_node
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
  def __init__(self, mbr, child):
    self.mbr = mbr
    self.child = child
  def getMBR(self):
    return self.mbr
  def setMBR(self, mbr):
    self.mbr = mbr
  def getChild(self):
    return self.child
  def setChild(self, node):
    self.child = node
  @staticmethod
  def draw(tree, entries, image, depth):
    for entry in entries:
      RTreeEntry.drawHelper(tree, entry, image, depth)
  @staticmethod
  def drawHelper(tree, entry, image, depth):
    node = entry.getChild()
    entries = node.getEntries()
    mbr_list = [entry.getMBR()]
    for mbr in mbr_list:
      upper_left = mbr.getUpperLeft()
      lower_right = mbr.getLowerRight()
      x1, y1 = upper_left
      x2, y2 = lower_right
      multiplier = 1 / (1.0 * 6.5) * 0.8
      offset = (1536 * 0.2) / 2
      next_x1, next_y1 = (multiplier * x1 + offset, multiplier * y1 + offset)
      next_x2, next_y2 = (multiplier * x2 + offset, multiplier * y2 + offset)
      color_choice = depth % 3
      color = None
      if color_choice == 0:
        color = PythonMagick.Color(65535, 0, 0, 32767)
      elif color_choice == 1:
        color = PythonMagick.Color(0, 0, 65535, 32767)
      elif color_choice == 2:
        color = PythonMagick.Color(0, 65535, 0, 32767)
      if upper_left == lower_right:
        image.strokeColor("none")
        image.fillColor(color)
        center_x = next_x1
        center_y = next_y1
        radius = 4
        perimeter_x = next_x1
        perimeter_y = next_y1 + radius
        image.draw(PythonMagick.DrawableCircle(center_x, center_y, perimeter_x, perimeter_y))
      else:
        image.strokeColor(color)
        image.fillColor("none")
        image.strokeWidth(4)
        image.draw(PythonMagick.DrawableRectangle(next_x1, next_y1, next_x2, next_y2))
    if len(entries) == 0:
      parent = entry.getChild().getParent()
      mbr = entry.getMBR()
      location = Point.toPoint(mbr)
      x, y = location
      multiplier = 1 / (1.0 * 6.5) * 0.8
      offset = (1536 * 0.2) / 2
      next_x = multiplier * x
      next_y = multiplier * y
      image.strokeColor("none")
      image.fillColor("black")
      center_x = next_x + offset
      center_y = next_y + offset
      radius = 2
      perimeter_x = next_x + offset
      perimeter_y = next_y + offset + radius
      image.draw(PythonMagick.DrawableCircle(center_x, center_y, perimeter_x, perimeter_y))
    children = [x.getChild() for x in entries]
    entry.draw(tree, entries, image, depth + 1)
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
  def getArea(self):
    upper_left = self.getUpperLeft()
    lower_right = self.getLowerRight()
    sides = []
    for i in xrange(self.getDimension()):
      comp1 = upper_left[i]
      comp2 = lower_right[i]
      side = comp2 - comp1
      sides.append(side)
    area = reduce(lambda x, y: x * y, sides)
    return area
  @staticmethod
  def getEnlargedMBR(base_mbr, mbr):
    mbr_list = [base_mbr, mbr]
    upper_left_points = [x.getUpperLeft() for x in mbr_list]
    lower_right_points = [x.getLowerRight() for x in mbr_list]
    points = upper_left_points + lower_right_points
    min_components = []
    max_components = []
    for i in xrange(base_mbr.getDimension()):
      components = [x[i] for x in points]
      min_comp_value = min(components)
      max_comp_value = max(components)
      min_components.append(min_comp_value)
      max_components.append(max_comp_value)
    upper_left_point = tuple(min_components)
    lower_right_point = tuple(max_components)
    result_mbr_list = base_mbr.getMBRList() + [mbr]
    mbr = CompositeMBR(upper_left_point, lower_right_point, result_mbr_list)
    return mbr
  @staticmethod
  def getAreaEnlargement(base_mbr, mbr):
    base_mbr_area = base_mbr.getArea()
    enlarged_mbr = MBR.getEnlargedMBR(base_mbr, mbr)
    enlarged_mbr_area = enlarged_mbr.getArea()
    area_change = enlarged_mbr_area - base_mbr_area
    return area_change
  @staticmethod
  def doOverlap(mbr_a, mbr_b, without_borders = False):
    upper_left_a = mbr_a.getUpperLeft()
    lower_right_a = mbr_a.getLowerRight()
    upper_left_b = mbr_b.getUpperLeft()
    lower_right_b = mbr_b.getLowerRight()
    do_overlap = True
    for i in xrange(mbr_a.getDimension()):
      comp_a1 = min(upper_left_a[i], lower_right_a[i])
      comp_a2 = max(upper_left_a[i], lower_right_a[i])
      comp_b1 = min(upper_left_b[i], lower_right_b[i])
      comp_b2 = max(upper_left_b[i], lower_right_b[i])
      if without_borders == True:
        do_overlap = do_overlap and comp_a1 < comp_b2 and comp_a2 > comp_b1
      else:
        do_overlap = do_overlap and comp_a1 <= comp_b2 and comp_a2 >= comp_b1
      if do_overlap == False:
        break
    return do_overlap
  @staticmethod
  def findOverlapArea(mbr_a, mbr_b):
    if MBR.doOverlap(mbr_a, mbr_b) == False:
      return 0
    else:
      upper_left_a = mbr_a.getUpperLeft()
      lower_right_a = mbr_a.getLowerRight()
      upper_left_b = mbr_b.getUpperLeft()
      lower_right_b = mbr_b.getLowerRight()
      dimension = mbr_a.getDimension()
      sides = []
      for i in xrange(dimension):
        comp_a1 = upper_left_a[i]
        comp_a2 = lower_right_a[i]
        comp_b1 = upper_left_b[i]
        comp_b2 = lower_right_b[i]
        side = max(0, min(comp_a2, comp_b2) - max(comp_a1, comp_b1))
        sides.append(side)
      intersection_volume = reduce(lambda x, y: x * y, sides)
      return intersection_volume
  def getMarginValue(self):
    upper_left = self.getUpperLeft()
    lower_right = self.getLowerRight()
    if self.getDimension() == 0:
      raise Exception()
    if self.getDimension() == 1:
      x1 = upper_left[0]
      x2 = lower_right[0]
      margin = x2 - x1
      return margin
    if self.getDimension() == 2:
      x1, y1 = upper_left
      x2, y2 = lower_right
      margin = 2 * (x2 - x1) + 2 * (y2 - y1)
      return margin
    surface_area = 0
    for i in xrange(self.getDimension()):
      comp_1a = upper_left[i]
      comp_1b = lower_right[i]
      term1 = comp_1b - comp_1a
      for j in xrange(i + 1, self.getDimension()):
        comp_2a = upper_left[j]
        comp_2b = lower_right[j]
        term2 = comp_2b - comp_2a
        term = 2 * term1 * term2
        surface_area += term
    margin = surface_area
    return margin
  def toString(self):
    upper_left = self.getUpperLeft()
    lower_right = self.getLowerRight()
    result = str(list(upper_left + lower_right) + [self.isRaw()])
    return result
  def getDimension(self):
    return len(self.getUpperLeft())
  def doesEnclose(self, mbr):
    dimension = self.getDimension()
    does_enclose = True
    for i in xrange(dimension):
      left_value1 = self.getUpperLeft()[i]
      left_value2 = mbr.getUpperLeft()[i]
      right_value1 = self.getLowerRight()[i]
      right_value2 = mbr.getLowerRight()[i]
      component_does_enclose = left_value1 <= left_value2 and right_value1 >= right_value2
      if component_does_enclose == False:
        does_enclose = False
        break
    return does_enclose
  def isEqualTo(self, mbr):
    upper_left1 = self.getUpperLeft()
    lower_right1 = self.getLowerRight()
    upper_left2 = mbr.getUpperLeft()
    lower_right2 = mbr.getLowerRight()
    is_equal = upper_left1 == upper_left2 and lower_right1 == lower_right2
    return is_equal
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
  def clone(self):
    upper_left = self.getUpperLeft()
    lower_right = self.getLowerRight()
    contained_item = self.getContainedItem()
    mbr = RawMBR(upper_left, lower_right, contained_item)
    return mbr
  def doesMatch(self, mbr):
    upper_left_matches = self.getUpperLeft() == mbr.getUpperLeft()
    lower_right_matches = self.getLowerRight() == mbr.getLowerRight()
    result = upper_left_matches == True and lower_right_matches == True
    return result
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
    min_components = []
    max_components = []
    for i in xrange(component_mbr_list[0].getDimension()):
      components = [x[i] for x in points]
      min_comp_value = min(components)
      max_comp_value = max(components)
      min_components.append(min_comp_value)
      max_components.append(max_comp_value)
    upper_left_point = tuple(min_components)
    lower_right_point = tuple(max_components)
    result_mbr = CompositeMBR(upper_left_point, lower_right_point, component_mbr_list)
    return result_mbr
class HyperRectangle:
  def __init__(self, upper_left, lower_right, id_value):
    self.upper_left = upper_left
    self.lower_right = lower_right
    self.id_value = id_value
  def getUpperLeft(self):
    return self.upper_left
  def getLowerRight(self):
    return self.lower_right
  def getIDValue(self):
    return self.id_value
class Point:
  def __init__(self, vec, id_value):
    self.vec = vec
    self.id_value = id_value
  @staticmethod
  def toPoint(mbr):
    if mbr.getUpperLeft() != mbr.getLowerRight():
      raise Exception("attempted to turn a non-point mbr to a point")
    return mbr.getUpperLeft()
  def getVec(self):
    return self.vec
  def getComponent(self, d):
    return self.getVec()[d]
  def getIDValue(self):
    return self.id_value
import string
class RTree:
  def __init__(self):
    root_node = RTreeNode(None, [], True)
    root_mbr = CompositeMBR(None, None, None)
    root_entry = RTreeEntry(root_mbr, root_node)
    root_node.setEntry(root_entry)
    self.setRootEntry(root_entry)
  def getRootEntry(self):
    return self.root_entry
  def setRootEntry(self, root_entry):
    self.root_entry = root_entry
  def hasConsistentNonTraditionalLeafDepthValues(self):
    root = self.getRootEntry().getChild()
    curr_node = root
    depth = 0
    while curr_node.isLeafNode() == False:
      curr_node = curr_node.getChildren()[0]
      depth = depth + 1
    return self.hasConsistentNonTraditionalLeafDepthValuesHelper(root, depth, 0)
  def hasConsistentNonTraditionalLeafDepthValuesHelper(self, node, depth, curr_depth):
    if node == None:
      return
    elif node.isLeafNode() == True:
      if depth != curr_depth:
        return False
      else:
        return True
    else:
      for curr_node in node.getChildren():
        result = self.hasConsistentNonTraditionalLeafDepthValuesHelper(curr_node, depth, curr_depth + 1)
        if result == False:
          return False
      return True
  def toNumChildrenString(self):
    root = self.getRootEntry().getChild()
    return self.toNumChildrenStringHelper(root)
  def toNumChildrenStringHelper(self, node):
    if node == None:
      return ""
    entries = node.getEntries()
    children = node.getChildren()
    have_node_str = True
    overall_str_list = None
    if have_node_str == True:
      curr_leaf_status = str(node.getNumChildren())
      overall_str_list = [curr_leaf_status]
    else:
      overall_str_list = []
    for entry in entries:
      child = entry.getChild()
      child_str = self.toNumChildrenStringHelper(child)
      curr_str = child_str
      overall_str_list.append(curr_str)
    overall_str = "(" + string.join(overall_str_list, " ") + ")"
    return overall_str
  def toEntriesArePresentString(self):
    root = self.getRootEntry().getChild()
    return self.toEntriesArePresentStringHelper(root)
  def toEntriesArePresentStringHelper(self, node):
    if node == None:
      return ""
    entries = node.getEntries()
    children = node.getChildren()
    have_node_str = True
    overall_str_list = None
    if have_node_str == True:
      curr_leaf_status = "-" if (node.getParent() == None or (node.getParent() != None and node in node.getParent().getChildren())) == False else "+"
      overall_str_list = [curr_leaf_status]
    else:
      overall_str_list = []
    for entry in entries:
      child = entry.getChild()
      child_str = self.toEntriesArePresentStringHelper(child)
      curr_str = child_str
      overall_str_list.append(curr_str)
    overall_str = "(" + string.join(overall_str_list, " ") + ")"
    return overall_str
  def toLeafStatusString(self):
    root = self.getRootEntry().getChild()
    return self.toLeafStatusStringHelper(root)
  def toLeafStatusStringHelper(self, node):
    if node == None:
      return ""
    entries = node.getEntries()
    children = node.getChildren()
    have_node_str = True
    overall_str_list = None
    if have_node_str == True:
      curr_leaf_status = "-" if node.isLeafNode() == False else "+"
      overall_str_list = [curr_leaf_status]
    else:
      overall_str_list = []
    for entry in entries:
      child = entry.getChild()
      child_str = self.toLeafStatusStringHelper(child)
      curr_str = child_str
      overall_str_list.append(curr_str)
    overall_str = "(" + string.join(overall_str_list, " ") + ")"
    return overall_str
  def toDepthString(self):
    root = self.getRootEntry().getChild()
    return self.toDepthStringHelper(root, 0)
  def toDepthStringHelper(self, node, depth):
    if node == None:
      return ""
    entries = node.getEntries()
    children = node.getChildren()
    have_node_str = True
    overall_str_list = None
    if have_node_str == True:
      curr_depth = "-" if node.getNumEntries() != 0 else str(depth)
      overall_str_list = [curr_depth]
    else:
      overall_str_list = []
    for entry in entries:
      child = entry.getChild()
      child_str = self.toDepthStringHelper(child, depth + 1)
      curr_str = child_str
      overall_str_list.append(curr_str)
    overall_str = "(" + string.join(overall_str_list, " ") + ")"
    return overall_str
  def toString(self):
    root = self.getRootEntry().getChild()
    return self.toStringHelper(root)
  def toStringHelper(self, node):
    if node == None:
      return ""
    entries = node.getEntries()
    children = node.getChildren()
    have_node_str = True
    is_root_node = node == self.getRootEntry().getChild()
    if is_root_node == True:
      have_node_str = True
    overall_str_list = None
    if is_root_node == False:
      overall_str_list = [node.getEntry().getMBR().toString()]
    else:
      overall_str_list = [] if node.getNumChildren() == 0 else [node.getEntry().getMBR().toString()]
    for entry in entries:
      child = entry.getChild()
      child_str = self.toStringHelper(child)
      curr_str = child_str
      overall_str_list.append(curr_str)
    overall_str = "(" + string.join(overall_str_list, " ") + ")"
    return overall_str
  def chooseEntriesWithMinimalOverlapEnlargement(self, entries, entry):
    mbr_to_entry_dict = {}
    for i in range(len(entries)):
      curr_entry = entries[i]
      curr_mbr = curr_entry.getMBR()
      mbr_to_entry_dict[curr_mbr] = curr_entry
    mbr_list = [x.getMBR() for x in entries]
    mbr = entry.getMBR()
    tagged_enlargement_values = [(MBR.findOverlapArea(x, mbr), x) for x in mbr_list]
    enlargement_values = [x[0] for x in tagged_enlargement_values]
    min_enlargement_value = min(enlargement_values)
    candidate_tagged_enlargement_values = [x for x in tagged_enlargement_values if x[0] == min_enlargement_value]
    candidate_entries = [mbr_to_entry_dict[x[1]] for x in candidate_tagged_enlargement_values]
    return candidate_entries
  def chooseEntriesWithMinimalAreaEnlargement(self, entries, entry):
    mbr_to_entry_dict = {}
    for i in range(len(entries)):
      curr_entry = entries[i]
      curr_mbr = curr_entry.getMBR()
      mbr_to_entry_dict[curr_mbr] = curr_entry
    mbr_list = [x.getMBR() for x in entries]
    mbr = entry.getMBR()
    tagged_enlargement_values = [(MBR.getAreaEnlargement(x, mbr), x) for x in mbr_list]
    enlargement_values = [x[0] for x in tagged_enlargement_values]
    min_enlargement_value = min(enlargement_values)
    candidate_tagged_enlargement_values = [x for x in tagged_enlargement_values if x[0] == min_enlargement_value]
    candidate_entries = [mbr_to_entry_dict[x[1]] for x in candidate_tagged_enlargement_values]
    return candidate_entries
  def resolveEnlargementTie(self, entries, entry):
    mbr = entry.getMBR()
    tagged_mbr_list = []
    for curr_entry in entries:
      base_mbr = curr_entry.getMBR()
      curr_mbr = MBR.getEnlargedMBR(base_mbr, mbr)
      tagged_mbr_list.append((curr_mbr, curr_entry))
    tagged_area_values = [(x[0].getArea(), x[1]) for x in tagged_mbr_list]
    area_values = [x[0] for x in tagged_area_values]
    min_area = min(area_values)
    candidate_tagged_area_values = [x for x in tagged_area_values if x[0] == min_area]
    candidate_entries = [x[1] for x in candidate_tagged_area_values]
    return candidate_entries
  @staticmethod
  def rstarGenDistributions(entries, M, m):
    result_list = []
    if len(entries) > (M + 1):
      raise Exception()
    window_left_sizes = [m - 1 + k for k in range(1, M - 2 * m + 2 + 1)]
    window_left_sizes = [x for x in window_left_sizes if x <= M and x >= m and (len(entries) - x) <= M and (len(entries) - x) >= m]
    window_size_pairs = [(window_left_sizes[i], len(entries) - window_left_sizes[i]) for i in range(len(window_left_sizes))]
    window_size_pairs = [x for x in window_size_pairs if x[0] <= M and x[0] >= m and x[1] <= M and x[1] >= m]
    for i in xrange(entries[0].getMBR().getDimension()):
      low_sorted_entries = entries[ : ]
      low_sorted_entries.sort(key = lambda x: x.getMBR().getUpperLeft()[i])
      low_distributions = [(low_sorted_entries[ : window_left_sizes[j]], low_sorted_entries[window_left_sizes[j] : ]) for j in xrange(len(window_left_sizes))]
      upper_sorted_entries = entries[ : ]
      upper_sorted_entries.sort(key = lambda x: x.getMBR().getLowerRight()[i])
      upper_distributions = [(upper_sorted_entries[ : window_left_sizes[j]], upper_sorted_entries[window_left_sizes[j] : ]) for j in xrange(len(window_left_sizes))]
      curr_tuple = (low_distributions, upper_distributions)
      result_list.append(curr_tuple)
    return result_list
  @staticmethod
  def rstarChooseSplitAxis(entries, M, m):
    result = RTree.rstarGenDistributions(entries, M, m)
    S_comp_dict = {}
    for i in xrange(entries[0].getMBR().getDimension()):
      low_comp_distributions, upper_comp_distributions = result[i]
      S_comp_value = 0
      low_constituent_mbr_list_pairs = [([y.getMBR() for y in x[0]], [y.getMBR() for y in x[1]]) for x in low_comp_distributions]
      low_mbr_pairs = [(CompositeMBR.makeMBR(x[0]), CompositeMBR.makeMBR(x[1])) for x in low_constituent_mbr_list_pairs]
      low_margin_values = [x[0].getMarginValue() + x[1].getMarginValue() for x in low_mbr_pairs]
      low_margin_value_sum = sum(low_margin_values)
      S_comp_value += low_margin_value_sum
      upper_constituent_mbr_list_pairs = [([y.getMBR() for y in x[0]], [y.getMBR() for y in x[1]]) for x in upper_comp_distributions]
      upper_mbr_pairs = [(CompositeMBR.makeMBR(x[0]), CompositeMBR.makeMBR(x[1])) for x in upper_constituent_mbr_list_pairs]
      upper_margin_values = [x[0].getMarginValue() + x[1].getMarginValue() for x in upper_mbr_pairs]
      upper_margin_value_sum = sum(upper_margin_values)
      S_comp_value += upper_margin_value_sum
      S_comp_dict[i] = S_comp_value
    d_S_pairs = S_comp_dict.items()
    min_S_value = min([x[1] for x in d_S_pairs])
    min_S_value_d_S_pair_candidates = [x for x in d_S_pairs if x[1] == min_S_value]
    chosen_d_S_pair = min_S_value_d_S_pair_candidates[0]
    chosen_d_value = chosen_d_S_pair[0]
    return chosen_d_value
  @staticmethod
  def rstarChooseSplitIndex(entries, axis, M, m):
    result = RTree.rstarGenDistributions(entries, M, m)
    candidate_distributions = None
    candidate_distributions = result[axis][0] + result[axis][1]
    mbr_list_pair_tagged_candidate_distributions = [(([y.getMBR() for y in x[0]], [y.getMBR() for y in x[1]]), x) for x in candidate_distributions]
    mbr_pair_tagged_candidate_distributions = [((CompositeMBR.makeMBR(x[0][0]), CompositeMBR.makeMBR(x[0][1])), x[1]) for x in mbr_list_pair_tagged_candidate_distributions]
    overlap_value_tagged_candidate_distributions = [(MBR.findOverlapArea(x[0][0], x[0][1]), x[1]) for x in mbr_pair_tagged_candidate_distributions]
    overlap_values = [x[0] for x in overlap_value_tagged_candidate_distributions]
    min_overlap_value = min(overlap_values)
    matching_overlap_value_tagged_candidate_distributions = [x for x in overlap_value_tagged_candidate_distributions if x[0] == min_overlap_value]
    next_next_candidates = [x[1] for x in matching_overlap_value_tagged_candidate_distributions]
    if len(matching_overlap_value_tagged_candidate_distributions) > 1:
      next_candidate_distributions = next_next_candidates
      mbr_list_pair_tagged_candidate_distributions = [(([y.getMBR() for y in x[0]], [y.getMBR() for y in x[1]]), x) for x in next_candidate_distributions]
      mbr_pair_tagged_next_candidate_distributions = [((CompositeMBR.makeMBR(x[0][0]), CompositeMBR.makeMBR(x[0][1])), x[1]) for x in mbr_list_pair_tagged_candidate_distributions]
      combined_area_tagged_next_candidate_distributions = [(x[0][0].getArea() + x[0][1].getArea(), x[1]) for x in mbr_pair_tagged_next_candidate_distributions]
      combined_area_values = [x[0] for x in combined_area_tagged_next_candidate_distributions]
      min_combined_area_value = min(combined_area_values)
      matching_combined_area_tagged_next_candidate_distributions = [x for x in combined_area_tagged_next_candidate_distributions if x[0] == min_combined_area_value]
      next_next_candidates = [x[1] for x in matching_combined_area_tagged_next_candidate_distributions]
    chosen_distribution_pair = next_next_candidates[0]
    return chosen_distribution_pair
  def chooseLeaf(self, entry):
    return self.chooseLeafHelper(entry, self.getRootEntry().getChild())
  def chooseLeafHelper(self, entry, node):
    if node.isLeafNode() == True:
      if node == self.getRootEntry().getChild():
        return node
      else:
        return node.getParent()
    else:
      entries = node.getEntries()
      candidate_entries = self.chooseEntriesWithMinimalAreaEnlargement(entries, entry)
      if len(candidate_entries) != 1:
        candidate_entries = self.resolveEnlargementTie(candidate_entries, entry)
      chosen_entry = candidate_entries[0]
      chosen_child = chosen_entry.getChild()
      return self.chooseLeafHelper(entry, chosen_child)
  def rstarChooseLeaf(self, entry):
    return self.rstarChooseLeafHelper(entry, self.getRootEntry().getChild())
  def rstarChooseLeafHelper(self, entry, node):
    if node.isLeafNode() == True:
      if node == self.getRootEntry().getChild():
        return node
      else:
        return node.getParent()
    else:
      entries = node.getEntries()
      candidate_entries = None
      candidate_entries = self.chooseEntriesWithMinimalOverlapEnlargement(entries, entry)
      if len(candidate_entries) != 1:
        candidate_entries = self.chooseEntriesWithMinimalAreaEnlargement(candidate_entries, entry)
      if len(candidate_entries) != 1:
        candidate_entries = self.resolveEnlargementTie(candidate_entries, entry)
      chosen_entry = candidate_entries[0]
      chosen_child = chosen_entry.getChild()
      return self.rstarChooseLeafHelper(entry, chosen_child)
  def insert(self, entry):
    return self.xtreeInsert(entry)
  def chooseSubtree(self, entry, node):
      entries = node.getEntries()
      candidate_entries = None
      candidate_entries = self.chooseEntriesWithMinimalOverlapEnlargement(entries, entry)
      if len(candidate_entries) != 1:
        candidate_entries = self.chooseEntriesWithMinimalAreaEnlargement(candidate_entries, entry)
      if len(candidate_entries) != 1:
        candidate_entries = self.resolveEnlargementTie(candidate_entries, entry)
      chosen_entry = candidate_entries[0]
      chosen_child = chosen_entry.getChild()
      return chosen_entry
  def xtreeInsert(self, entry):
    return self.xtreeInsertHelper(entry, self.getRootEntry().getChild())
  SPLIT = 0
  SUPERNODE = 1
  NO_SPLIT = 2
  def xtreeInsertHelper(self, entry, node):
    split_status = None
    next_mbr = None
    if True:
      if node.isLeafNode() == True and node == self.getRootEntry().getChild():
        node.addEntry(entry)
        curr_node = entry.getChild()
        curr_node.setParent(node)
        mbr = CompositeMBR.makeMBR([entry.getMBR()])
        node.getEntry().setMBR(mbr)
        return (RTree.NO_SPLIT, [node])
      if node.isLeafNode() == True:
        return (RTree.SPLIT, [node])
      elif node.isNonTraditionalLeafNode() == True:
        node.addEntry(entry)
        entry.getChild().setParent(node)
      follow = self.chooseSubtree(entry, node).getChild()
      result = self.xtreeInsertHelper(entry, follow)
      split_status, added_nodes = result
      curr_entry = node.getEntry()
      curr_mbr = curr_entry.getMBR()
      mbr = entry.getMBR()
      next_mbr = MBR.getEnlargedMBR(curr_mbr, mbr)
      node.getEntry().setMBR(next_mbr)
      for added_node in added_nodes:
        node.addEntry(added_node.getEntry())
        added_node.setParent(node)
    if split_status == RTree.SPLIT:
      if node.getNumChildren() > node.getMaximumNumEntriesPerNode():
        split_result = self.xtreeSplitNode(node, entry)
        was_successful, entry_collection1, entry_collection2, dimension = split_result
        if was_successful == True:
          mbr_collection1 = [x.getMBR() for x in entry_collection1]
          mbr_collection2 = [x.getMBR() for x in entry_collection2]
          parent = node.getParent()
          entry1 = RTreeEntry(CompositeMBR.makeMBR(mbr_collection1), None)
          node1 = RTreeNode(parent, entry_collection1, None, entry1)
          entry1.setChild(node1)
          entry2 = RTreeEntry(CompositeMBR.makeMBR(mbr_collection2), None)
          node2 = RTreeNode(parent, entry_collection2, None, entry2)
          entry2.setChild(node2)
          for curr_entry in entry_collection1:
            curr_entry.getChild().setParent(node1)
          for curr_entry in entry_collection2:
            curr_entry.getChild().setParent(node2)
          node1.setSplitHistoryRootDimension(dimension)
          node2.setSplitHistoryRootDimension(dimension)
          if self.getRootEntry().getChild() == node:
            next_root_entry = RTreeEntry(next_mbr, None)
            next_root = RTreeNode(None, [entry1, entry2], None, next_root_entry)
            next_root_entry.setChild(next_root)
            self.setRootEntry(next_root_entry)
            node1.setParent(next_root)
            node2.setParent(next_root)
          else:
            parent.removeEntry(node.getEntry())
            parent.addEntry(entry1)
            parent.addEntry(entry2)
          return (RTree.SPLIT, [node1, node2])
        else:
          self.xtreeSupernodeInsert(node, [x.getEntry() for x in added_nodes])
          return (RTree.SUPERNODE, [node])
    elif split_status == RTree.SUPERNODE:
      pass
    return (RTree.NO_SPLIT, [node])
  def rstarInsert(self, entry):
    leaf_node = self.rstarChooseLeaf(entry)
    adjust_result = None
    if leaf_node.isFull() == False:
      leaf_node.addEntry(entry)
      entry.getChild().setParent(leaf_node)
      adjust_result = RTree.rstarAdjustTree(self, leaf_node, [entry], False)
    else:
      split_result = self.rstarSplitNode(leaf_node, entry)
      l, ll, e, ee = split_result
      adjust_result = RTree.rstarAdjustTree(self, l, [e, ee], True)
    ended_with_split2, resulting_entries_from_split = adjust_result
    if ended_with_split2 == True:
      e, ee = resulting_entries_from_split
      l = e.getChild()
      ll = ee.getChild()
      if (self.getRootEntry().getChild().getNumEntries() + 1) <= self.getRootEntry().getChild().getMaximumNumEntriesPerNode():
        self.getRootEntry().getChild().addEntry(ee)
        ll.setParent(self.getRootEntry().getChild())
      else:
        split_result = self.rstarSplitNode(self.getRootEntry().getChild(), ee)
        l, ll, e, ee = split_result
        resulting_entries_from_split = [e, ee]
        next_root = RTreeNode(None, resulting_entries_from_split, False, self.getRootEntry())
        l.setParent(next_root)
        ll.setParent(next_root)
        self.getRootEntry().setChild(next_root)
    else:
      pass
  MAX_OVERLAP_RATIO = 0.2
  def xtreeSplitNode(self, node, entry):
    if node.isSuperNode() == True:
      return (False, None, None, None)
    dimension = None
    result1 = self.xtreeTopologicalSplit(node, entry)
    entry_collection1, entry_collection2, dimension = result1
    mbr_collection1 = [x.getMBR() for x in entry_collection1]
    mbr_collection2 = [x.getMBR() for x in entry_collection2]
    mbr1 = CompositeMBR.makeMBR(mbr_collection1)
    mbr2 = CompositeMBR.makeMBR(mbr_collection2)
    overlap_area = MBR.findOverlapArea(mbr1, mbr2)
    area1 = mbr1.getArea()
    area2 = mbr2.getArea()
    union_area = area1 + area2 - overlap_area
    ovelap_ratio = None
    if union_area == 0:
      if mbr1.isEqualTo(mbr2) == True:
        overlap_ratio = 1
      else:
        overlap_ratio = 0
    else:
      overlap_ratio = overlap_area / (1.0 * union_area)
    if overlap_ratio > RTree.MAX_OVERLAP_RATIO:
      result2 = self.xtreeOverlapMinimalSplit(node, entry)
      entry_collection3, entry_collection4, dimension, do_fail = result2
      if do_fail == True or len(entry_collection3) < node.getMinimumNumEntriesPerNode() or len(entry_collection4) < node.getMinimumNumEntriesPerNode():
        return (False, None, None, dimension)
      else:
        return (True, entry_collection3, entry_collection4, dimension)
    else:
      return (True, entry_collection1, entry_collection2, dimension)
  def xtreeTopologicalSplit(self, node, entry):
    m = self.getRootEntry().getChild().getMinimumNumEntriesPerNode()
    M = self.getRootEntry().getChild().getMaximumNumEntriesPerNode()
    E_overall = node.getEntries()
    axis = RTree.rstarChooseSplitAxis(E_overall, M, m)
    result = RTree.rstarChooseSplitIndex(E_overall, axis, M, m)
    entry_group1, entry_group2 = result
    next_result = (entry_group1, entry_group2, axis)
    return next_result
  def xtreeOverlapMinimalSplit(self, node, entry):
    if node.getSplitHistoryRootDimension() == None:
      return (None, None, None, True)
    else:
      m = self.getRootEntry().getChild().getMinimumNumEntriesPerNode()
      M = self.getRootEntry().getChild().getMaximumNumEntriesPerNode()
      E_overall = node.getEntries()
      axis = node.getSplitHistoryRootDimension()
      result = RTree.rstarChooseSplitIndex(E_overall, axis, M, m)
      entry_group1, entry_group2 = result
      next_result = (entry_group1, entry_group2, axis, False)
      return next_result
  def xtreeSupernodeInsert(self, node, entries):
    if node.isSuperNode() == False:
      node.setToSuperNode(True)
    for entry in entries:
      curr_node = entry.getChild()
      node.addEntry(entry)
      curr_node.setParent(node)
  def rstarSplitNode(self, node, entry):
    curr_node = node
    E_overall = list(set(curr_node.getEntries() + [entry]))
    return self.rstarSplitNodeHelper(node, E_overall, entry)
  def rstarSplitNodeHelper(self, node, E_overall, entry):
    prev_leaf_status = None
    curr_node = node
    m = self.getRootEntry().getChild().getMinimumNumEntriesPerNode()
    M = self.getRootEntry().getChild().getMaximumNumEntriesPerNode()
    axis = RTree.rstarChooseSplitAxis(E_overall, M, m)
    result = RTree.rstarChooseSplitIndex(E_overall, axis, M, m)
    entry_group1, entry_group2 = result
    parent = curr_node.getParent()
    node1 = RTreeNode(parent, entry_group1, prev_leaf_status)
    node2 = RTreeNode(parent, entry_group2, prev_leaf_status)
    for curr_entry in entry_group1:
      curr_entry.getChild().setParent(node1)
    for curr_entry in entry_group2:
      curr_entry.getChild().setParent(node2)
    mbr_group1 = [x.getMBR() for x in entry_group1]
    mbr_group2 = [x.getMBR() for x in entry_group2]
    curr_overall_mbr1 = CompositeMBR.makeMBR(mbr_group1)
    curr_overall_mbr2 = CompositeMBR.makeMBR(mbr_group2)
    for curr_entry in entry_group1:
      next_curr_node = curr_entry.getChild()
      if curr_entry != entry:
        curr_node.removeEntry(curr_entry)
      next_curr_node.setParent(node1)
    for curr_entry in entry_group2:
      next_curr_node = curr_entry.getChild()
      if curr_entry != entry:
        curr_node.removeEntry(curr_entry)
      next_curr_node.setParent(node2)
    entry1 = RTreeEntry(curr_overall_mbr1, node1)
    entry2 = RTreeEntry(curr_overall_mbr2, node2)
    node1.setEntry(entry1)
    node2.setEntry(entry2)
    if parent != None:
      original_entry = parent.retrieveEntryForChild(curr_node)
      parent.removeEntry(original_entry)
    if node != self.getRootEntry().getChild():
      parent.addEntry(entry1)
      parent.addEntry(entry2)
      node1.setParent(parent)
      node2.setParent(parent)
    else:
      next_root = RTreeNode(None, [entry1, entry2], False)
      self.getRootEntry().setChild(next_root)
      next_root.setEntry(self.getRootEntry())
      node1.setParent(next_root)
      node2.setParent(next_root)
      pass
    return (node1, node2, entry1, entry2)
  @staticmethod
  def rstarPreadjustTree(self, leaf_node):
    node = leaf_node
    parent = node.getParent()
    if parent != None:
      curr_entries = node.getEntries()
      entry = node.getParent().retrieveEntryForChild(node)
      children = [x.getChild() for x in curr_entries]
      mbr_list = [x.getMBR() for x in curr_entries]
      tight_overall_mbr = CompositeMBR.makeMBR(mbr_list)
      entry.setMBR(tight_overall_mbr)
  @staticmethod
  def rstarAdjustTree(tree, node, resulting_entries_from_split, have_resulting_second_entry_from_split):
    return tree.rstarAdjustTreeHelper(tree, node, resulting_entries_from_split, have_resulting_second_entry_from_split)
  @staticmethod
  def rstarAdjustTreeHelper(tree, node, resulting_entries_from_split, 
have_resulting_second_entry_from_split):
    if node.getParent() == None:
      entry = tree.getRootEntry()
      curr_entries = entry.getChild().getEntries()
      children = [x.getChild() for x in curr_entries]
      mbr_list = [x.getMBR() for x in curr_entries]
      tight_overall_mbr = CompositeMBR.makeMBR(mbr_list)
      entry.setMBR(tight_overall_mbr)
      return (have_resulting_second_entry_from_split, resulting_entries_from_split)
    else:
      parent = node.getParent()
      curr_entries = node.getEntries()
      entry = None
      entry = parent.retrieveEntryForChild(node)
      children = [x.getChild() for x in curr_entries]
      mbr_list = [x.getMBR() for x in curr_entries]
      tight_overall_mbr = CompositeMBR.makeMBR(mbr_list)
      entry.setMBR(tight_overall_mbr)
      partner_entry = None
      if have_resulting_second_entry_from_split == True:
        first_entry, second_entry = resulting_entries_from_split
        partner_entry = second_entry
      if have_resulting_second_entry_from_split == True:
        partner_node = partner_entry.getChild()
        partner_entries = partner_node.getEntries()
        partner_children = [x.getChild() for x in partner_entries]
        partner_mbr_list = [x.getMBR() for x in partner_entries]
        partner_tight_overall_mbr = CompositeMBR.makeMBR(partner_mbr_list)
        partner_entry.setMBR(partner_tight_overall_mbr)
      if node.isLeafNode() == False:
        if have_resulting_second_entry_from_split == True:
          if (parent.getNumChildren() + 1) <= parent.getMaximumNumEntriesPerNode():
            parent.addEntry(partner_entry)
            partner_entry.getChild().setParent(parent)
            return RTree.rstarAdjustTreeHelper(tree, node.getParent(), [entry], False)
          else:
            split_result = tree.rstarSplitNode(parent, partner_entry)
            l, ll, e, ee = split_result
            return RTree.rstarAdjustTreeHelper(tree, node.getParent(), [e, ee], True)
        else:
          return RTree.rstarAdjustTreeHelper(tree, node.getParent(), [entry], False)
      else:
        return RTree.rstarAdjustTreeHelper(tree, node.getParent(), resulting_entries_from_split, 
have_resulting_second_entry_from_split)
  def findLeaf(self, entry):
    return self.findLeafHelper(entry, self.getRootEntry())
  def findLeafHelper(self, entry, curr_entry):
    if curr_entry.getMBR().isRaw() == True:
      if entry == curr_entry:
        return True
      else:
        return False
    else:
      entries = curr_entry.getChild().getEntries()
      for next_entry in entries:
        if MBR.doOverlap(curr_entry.getMBR(), entry.getMBR()) == True:
          result = self.findLeafHelper(entry, next_entry)
          if result == True:
            return result
      return False
  def delete(self, entry):
    did_find_leaf = self.findLeaf(entry)
    child_node = entry.getChild()
    leaf_node = child_node.getParent() if entry != self.getRootEntry() else None
    if leaf_node == None:
      raise Exception("expected a node to be found for a delete")
    leaf_node.removeEntry(entry)
    self.condenseTree(leaf_node)
  def condenseTree(self, leaf_node):
    Q = []
    self.condenseTreeHelper(leaf_node, Q)
    Q.reverse()
    for curr_node in Q:
      curr_entry = curr_node.getEntry()
      self.insert(curr_entry)
  def condenseTreeHelper(self, node, Q):
    if node.isSuperNode() == True and node.getNumChildren() <= node.getMaximumNumEntriesPerNode():
      node.setToSuperNode(False)
    if node.getParent() == None:
      if self.getRootEntry().getChild().getNumChildren() == 0:
        root_node = RTreeNode(None, [], True)
        root_mbr = CompositeMBR(None, None, None)
        root_entry = RTreeEntry(root_mbr, root_node)
        root_node.setEntry(root_entry)
        self.setRootEntry(root_entry)
        return
      else:
        entry = self.getRootEntry()
        curr_entries = entry.getChild().getEntries()
        children = [x.getChild() for x in curr_entries]
        mbr_list = [x.getMBR() for x in curr_entries]
        tight_overall_mbr = CompositeMBR.makeMBR(mbr_list)
        entry.setMBR(tight_overall_mbr)
        return
    else:
      if node.isUnderfull() == True:
        parent = node.getParent()
        parent.removeEntry(parent.retrieveEntryForChild(node))
        keep_nodes = [x for x in self.getNodesForNode(node) if x.getEntry().getMBR().isRaw() == True]
        for keep_node in keep_nodes:
          Q.append(keep_node)
      if node.isUnderfull() == False:
        parent = node.getParent()
        curr_entries = node.getEntries()
        entry = parent.retrieveEntryForChild(node)
        children = [x.getChild() for x in curr_entries]
        mbr_list = [x.getMBR() for x in curr_entries]
        tight_overall_mbr = CompositeMBR.makeMBR(mbr_list)
        entry.setMBR(tight_overall_mbr)
      self.condenseTreeHelper(node.getParent(), Q)
      return
  def doOverlapQuery(self, mbr, without_borders = False):
    partial_result = []
    self.doOverlapQueryHelper(mbr, self.getRootEntry(), partial_result, without_borders)
    return partial_result
  def doOverlapQueryHelper(self, mbr, entry, partial_result, without_borders):
    if entry.getMBR().isRaw() == True:
      if MBR.doOverlap(entry.getMBR(), mbr, without_borders) == True:
        partial_result.append(entry)
    else:
      entries = entry.getChild().getEntries()
      for curr_entry in entries:
        if MBR.doOverlap(curr_entry.getMBR(), mbr) == True:
          self.doOverlapQueryHelper(mbr, curr_entry, partial_result, without_borders)
  def doEnclosureQuery(self, mbr):
    partial_result = []
    self.doEnclosureQueryHelper(mbr, self.getRootEntry(), partial_result)
    return partial_result
  def doEnclosureQueryHelper(self, mbr, entry, partial_result):
    if entry.getMBR().isRaw() == True:
      if entry.getMBR().doesEnclose(mbr) == True:
        partial_result.append(entry)
    else:
      entries = entry.getChild().getEntries()
      for curr_entry in entries:
        if curr_entry.getMBR().doesEnclose(mbr) == True:
          self.doEnclosureQueryHelper(mbr, curr_entry, partial_result)
  def doEnclosureQueryWithEarlyStopping(self, mbr):
    result = self.doEnclosureQueryWithEarlyStoppingHelper(mbr, self.getRootEntry())
    return result
  def doEnclosureQueryWithEarlyStoppingHelper(self, mbr, entry):
    if entry.getMBR().isRaw() == True:
      if entry.getMBR().doesEnclose(mbr) == True:
        return True
    else:
      entries = entry.getChild().getEntries()
      for curr_entry in entries:
        if curr_entry.getMBR().doesEnclose(mbr) == True:
          result = self.doEnclosureQueryWithEarlyStoppingHelper(mbr, curr_entry)
          if result == True:
            return True
    return False
  def doContainmentQuery(self, mbr):
    partial_result = []
    self.doContainmentQueryHelper(mbr, self.getRootEntry(), partial_result)
    return partial_result
  def doContainmentQueryHelper(self, mbr, entry, partial_result):
    if entry.getMBR().isRaw() == True:
      if mbr.doesEnclose(entry.getMBR()) == True:
        partial_result.append(entry)
    else:
      entries = entry.getChild().getEntries()
      for curr_entry in entries:
        if MBR.doOverlap(curr_entry.getMBR(), mbr) == True:
          self.doContainmentQueryHelper(mbr, curr_entry, partial_result)
  def getNodes(self):
    node_list = []
    self.getNodesHelper(self.getRootEntry().getChild(), node_list)
    return node_list
  def getNodesHelper(self, node, partial_result):
    partial_result.append(node)
    for curr_node in node.getChildren():
      self.getNodesHelper(curr_node, partial_result)
  def getNodesForNode(self, node):
    node_list = []
    self.getNodesHelper(node, node_list)
    return node_list
  def getRectangleCloseDescendants(self, reference_entry):
    if self.getRootEntry().getChild().getNumChildren() == 0:
      return []
    reference_mbr = reference_entry.getMBR()
    root_entry = self.getRootEntry()
    root_node = root_entry.getChild()
    root_mbr = root_entry.getMBR()
    root_mbr_is_actual = root_mbr.isRaw()
    root_mbr_is_contained = reference_mbr.doesEnclose(root_mbr)
    root_mbr_area = root_mbr.getArea()
    first_priority_component = 0 if root_mbr_is_contained == True else 1
    second_priority_component = (-1 if root_mbr_is_contained == True else 1) * root_mbr_area
    priority = (first_priority_component, second_priority_component)
    heap = []
    item = root_entry
    pair = (priority,item)
    heapq.heappush(heap,pair)
    result_entry_list = []
    self.getRectangleCloseDescendantsHelper(heap, reference_mbr, result_entry_list, reference_entry)
    return result_entry_list
  def getRectangleCloseDescendantsHelper(self, heap, reference_mbr, result_entry_list, ignore_entry):
    conflict_x_tree = RTree()
    internal_node_stack_deque = deque()
    while len(internal_node_stack_deque) != 0 or len(heap) != 0:
      item = None
      if len(heap) != 0:
        (priority,item) = heapq.heappop(heap)
      elif len(internal_node_stack_deque) != 0:
        item = internal_node_stack_deque.popleft()
      entry = item
      node = entry.getChild()
      mbr = entry.getMBR()
      if mbr.doesEnclose(reference_mbr) == False and reference_mbr.doesEnclose(mbr) == False:
        continue
      if conflict_x_tree.doEnclosureQueryWithEarlyStopping(mbr) == True:
        continue
      if entry == ignore_entry:
        continue
      if node.isLeafNode() == True:
        if reference_mbr.doesEnclose(mbr) == False:
          continue
        matching_entries = conflict_x_tree.doContainmentQuery(mbr)
        for matching_entry in matching_entries:
          conflict_x_tree.delete(matching_entry)
        result_entry_list.append(entry)
        raw_mbr = mbr
        next_mbr = raw_mbr.clone()
        next_node = RTreeNode(None, [], True)
        next_entry = RTreeEntry(next_mbr, next_node)
        next_node.setEntry(next_entry)
        conflict_x_tree.insert(next_entry)
      elif node.isLeafNode() == False:
        entries = node.getEntries()
        priority_tagged_internal_entries = []
        for curr_entry in entries:
          curr_node = curr_entry.getChild()
          curr_mbr = curr_entry.getMBR()
          curr_mbr_is_actual = curr_mbr.isRaw()
          curr_mbr_is_contained = reference_mbr.doesEnclose(curr_mbr)
          curr_mbr_area = curr_mbr.getArea()
          first_priority_component = 0 if curr_mbr_is_contained == True else 1
          second_priority_component = (-1 if curr_mbr_is_contained == True else 1) * curr_mbr_area
          if curr_mbr.isRaw() == True:
            priority = -1 * curr_mbr_area
            item = curr_entry
            pair = (priority,item)
            heapq.heappush(heap,pair)
          elif curr_mbr.isRaw() == False:
            if curr_mbr.doesEnclose(reference_mbr) == False and reference_mbr.doesEnclose(curr_mbr) == False:
              continue
            priority = (first_priority_component, second_priority_component)
            priority_tagged_internal_entry = (priority, curr_entry)
            priority_tagged_internal_entries.append(priority_tagged_internal_entry)
        priority_tagged_internal_entries.sort(key = lambda x: x[0], reverse = True)
        for priority_tagged_internal_entry in priority_tagged_internal_entries:
          priority, internal_entry = priority_tagged_internal_entry
          item = internal_entry
          internal_node_stack_deque.appendleft(item)
  def getAllRectangleCloseAncestors(self):
    start_rectangle_nodes = [x for x in self.getNodes() if x.getEntry().getMBR().isRaw() == True]
    start_rectangle_entries = [x.getEntry() for x in start_rectangle_nodes]
    start_rectangle_to_close_ancestor_entries_dict = {}
    for start_rectangle_entry in start_rectangle_entries:
      start_rectangle_to_close_ancestor_entries_dict[start_rectangle_entry] = []
    for start_rectangle_entry in start_rectangle_entries:
      close_descendant_entries = self.getRectangleCloseDescendants(start_rectangle_entry)
      for close_descendant_entry in close_descendant_entries:
        start_rectangle_to_close_ancestor_entries_dict[close_descendant_entry].append(start_rectangle_entry)
    return start_rectangle_to_close_ancestor_entries_dict
  def draw(self):
    image = PythonMagick.Image(PythonMagick.Geometry("1536x1536"), "white")
    root_entry = self.getRootEntry()
    entries = [root_entry]
    RTreeEntry.draw(self, entries, image, 0)
    image.write("tree.png")
def main():
  point1 = (30, 100, 0)
  point2 = (40, 100, 0)
  point3 = (50, 100, 0)
  point4 = (60, 100, 0)
  point5 = (70, 100, 0)
  point6 = (80, 100, 0)
  point7 = (90, 100, 0)
  point8 = (110, 100, 0)
  curr_mbr1 = RawMBR((100, 100, 0), (100, 100, 0), (100, 100, 0))
  curr_mbr2 = RawMBR((50, 100, 0), (50, 100, 0), point3)
  curr_mbr2b = RawMBR((50, 50, 0), (100, 100, 0), HyperRectangle((50, 50, 0), (100, 100, 0), 1))
  tree = RTree()
  print tree.toString()
  curr_root = tree.getRootEntry().getChild()
  mbr1 = RawMBR(point1, (110, 200, 100), point1)
  node1 = RTreeNode(None, [], True)
  entry1 = RTreeEntry(mbr1, node1)
  node1.setEntry(entry1)
  tree.insert(entry1)
  mbr2 = RawMBR(point2, (110, 200, 100), point2)
  node2 = RTreeNode(None, [], True)
  entry2 = RTreeEntry(mbr2, node2)
  node2.setEntry(entry2)
  tree.insert(entry2)
  mbr3 = RawMBR(point3, (110, 200, 100), point3)
  node3 = RTreeNode(None, [], True)
  entry3 = RTreeEntry(mbr3, node3)
  node3.setEntry(entry3)
  tree.insert(entry3)
  mbr4 = RawMBR(point4, (110, 200, 100), point4)
  node4 = RTreeNode(None, [], True)
  entry4 = RTreeEntry(mbr4, node4)
  node4.setEntry(entry4)
  tree.insert(entry4)
  mbr5 = RawMBR(point5, (110, 200, 100), point5)
  node5 = RTreeNode(None, [], True)
  entry5 = RTreeEntry(mbr5, node5)
  node5.setEntry(entry5)
  tree.insert(entry5)
  mbr6 = RawMBR(point6, (110, 200, 100), point6)
  node6 = RTreeNode(None, [], True)
  entry6 = RTreeEntry(mbr6, node6)
  node6.setEntry(entry6)
  tree.insert(entry6)
  mbr7 = RawMBR(point7, (110, 200, 100), point7)
  node7 = RTreeNode(None, [], True)
  entry7 = RTreeEntry(mbr7, node7)
  node7.setEntry(entry7)
  tree.insert(entry7)
  mbr8 = RawMBR(point8, (110, 200, 100), point8)
  node8 = RTreeNode(None, [], True)
  entry8 = RTreeEntry(mbr8, node8)
  node8.setEntry(entry8)
  tree.insert(entry8)
  print tree.toString()
  print tree.doEnclosureQuery(curr_mbr2)
  curr_mbr3 = RawMBR((50, 100, 0), (110, 200, 100), None)
  print tree.doContainmentQuery(curr_mbr3)
  print tree.doOverlapQuery(curr_mbr2)
  print tree.toString()
  print tree.toString()
  print tree.toString()
  tree2 = RTree()
  import random
  entries = []
  n = 1000
  import math
  for i in xrange(n):
    upper_left = None
    lower_right = None
    denominator = (100 * math.log(100, 2)) ** (1 / 3.0)
    k = 1
    x = random.randint(0, 10000)
    y = random.randint(0, 10000)
    upper_left = (x, y)
    lower_right = (x, y)
    mbr = RawMBR(upper_left, lower_right, None)
    node = RTreeNode(None, [], True)
    entry = RTreeEntry(mbr, node)
    node.setEntry(entry)
    entries.append(entry)
  for entry in entries:
    tree2.insert(entry)
  print len(tree2.getNodes())
  import time
  time1 = time.time()
  result = tree2.getAllRectangleCloseAncestors()
  time2 = time.time()
  time_diff = time2 - time1
  print "time difference:", time_diff, "seconds"
  for entry_to_close_ancestor_entry_list_pair in result.items():
    entry, close_ancestor_entry_list = entry_to_close_ancestor_entry_list_pair
    print "start rectangle:", entry.getMBR().toString()
    for close_ancestor_entry in close_ancestor_entry_list:
      print "close ancestor:", close_ancestor_entry.getMBR().toString()
  result = tree.getRectangleCloseDescendants(entry8)
  print result
  result = tree.getAllRectangleCloseAncestors()
  print result
  print len(result)
  for entry_to_close_ancestor_entry_list_pair in result.items():
    entry, close_ancestor_entry_list = entry_to_close_ancestor_entry_list_pair
    print "start rectangle:", entry.getMBR().toString()
    for close_ancestor_entry in close_ancestor_entry_list:
      print "close ancestor:", close_ancestor_entry.getMBR().toString()
if __name__ == "__main__":
  main()
