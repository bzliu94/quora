# 2016-11-29

import string
import datetime
import x_tree
from collections import deque
import math
import sys
import csv
from collections import defaultdict

epoch = datetime.datetime.fromtimestamp(0)

class UTCOffset(datetime.tzinfo):
  def __init__(self, second_offset):
    self._offset = datetime.timedelta(seconds = second_offset)
    self._dst = datetime.timedelta(0)
    self._name = str(self._offset)
  def utcoffset(self, dt):
    return self._offset
  def tzname(self, dt):
    return self._name
  def dst(self, dt):
    return self._dst
def getUnixTimeSec(dt):
  return (dt - epoch).total_seconds()
def dateTimeParse(t, get_UTC = False):
  dt = datetime.datetime.strptime(t[0 : 19], "%m/%d/%Y %I:%M %p")
  tz_offset = datetime.timedelta(0)
  if t[20] == "+":
    tz_offset = datetime.timedelta(hours = int(t[21 : 23]), minutes = int(t[23 : 25]))
  elif t[20] == "-":
    tz_offset = datetime.timedelta(hours = int(t[21 : 23]), minutes = int(t[23 : 25]))
  if get_UTC == True:
    dt -= tz_offset
  return (dt, tz_offset)

class Attribute:
  def __init__(self, column_num, name):
    self.column_num = column_num
    self.name = name
    self.min_numeric_value = float("+inf")
    self.max_numeric_value = float("-inf")
  def getColumnNum(self):
    return self.column_num
  def getName(self):
    return self.name
  def toString(self):
    return str((self.getColumnNum(), self.getName()))
  def __repr__(self):
    return self.toString()
  def comesBefore(self, attribute):
    column_num1 = self.getColumnNum()
    column_num2 = attribute.getColumnNum()
    return column_num1 < column_num2
  def isCategorical(self):
    return False
  def isQuantitative(self):
    return False
  def getKey(self):
    return self.getColumnNum()
  def updateExtremeNumericValues(self, numeric_value):
    self.min_numeric_value = min(self.min_numeric_value, numeric_value)
    self.max_numeric_value = max(self.max_numeric_value, numeric_value)
  def getMinNumericValue(self):
    return self.min_numeric_value
  def getMaxNumericValue(self):
    return self.max_numeric_value
  def getFullExtent(self):
    return (self.getMinNumericValue(), self.getMaxNumericValue())
  def toTypeString(self):
    pass
class QuantitativeAttribute(Attribute):
  def __init__(self, column_num, name):
    Attribute.__init__(self, column_num, name)
  def isQuantitative(self):
    return True
  def toTypeString(self):
    return "Q"
  def isDateQuantitative(self):
    return False
  def isPercentQuantitative(self):
    return False
class DateQuantitativeAttribute(QuantitativeAttribute):
  def __init__(self, column_num, name):
    QuantitativeAttribute.__init__(self, column_num, name)
  def toTypeString(self):
    return "DQ"
  def isDateQuantitative(self):
    return True
class PercentQuantitativeAttribute(QuantitativeAttribute):
  def __init__(self, column_num, name):
    QuantitativeAttribute.__init__(self, column_num, name)
  def toTypeString(self):
    return "PQ"
  def isPercentQuantitative(self):
    return True
class CategoricalAttribute(Attribute):
  def __init__(self, column_num, name):
    Attribute.__init__(self, column_num, name)
    self.value_to_int_dict = {}
  def hasValue(self, value):
    return value in self.value_to_int_dict
  def getNumValues(self):
    return len(self.value_to_int_dict)
  def addValue(self, value):
    if self.hasValue(value) == False:
      self.value_to_int_dict[value] = self.getNumValues()
  def getNumericValue(self, value):
    return self.value_to_int_dict[value]
  def isCategorical(self):
    return True
  def toTypeString(self):
    return "C"
class Item:
  def __init__(self, attribute, value, count = 1):
    self.attribute = attribute
    self.value = value
    self.count = count
  def getAttribute(self):
    return self.attribute
  def getValue(self):
    return self.value
  def toString(self):
    return str((self.getAttribute(), self.getValue(), self.getCount()))
  def __repr__(self):
    return self.toString()
  def getCount(self):
    return self.count
  def setCount(self, count):
    self.count = count
  @staticmethod
  def isDegenerateValue(value):
    return value == ""
  def hasDegenerateValue(self):
    return self.getValue() == ""
  def comesBefore(self, item):
    value1 = self.getValue()
    value2 = item.getValue()
    return value1 < value2
  def isCategorical(self):
    return False
  def isQuantitative(self):
    return False
  def getKey(self):
    return self.getValue()
  def getRectangleKey(self):
    return (self.getValue(), self.getValue())
  def toVisString(self):
    pass
class CategoricalItem(Item):
  def __init__(self, categorical_attribute, value, count = 1):
    categorical_attribute.addValue(value)
    numeric_value = categorical_attribute.getNumericValue(value)
    Item.__init__(self, categorical_attribute, numeric_value, count)
    self.non_numeric_value = value
    categorical_attribute.updateExtremeNumericValues(numeric_value)
  def toString(self):
    return str((self.getAttribute(), self.getNonNumericValue(), self.getCount()))
  def getNonNumericValue(self):
    return self.non_numeric_value
  def isCategorical(self):
    return True
  def toVisString(self):
    return self.getNonNumericValue()
class IntervalItem(Item):
  def __init__(self, attribute, left_value, right_value, count = 1, is_date = False):
    Item.__init__(self, attribute, None, count)
    self.left_value = left_value
    self.right_value = right_value
    attribute.updateExtremeNumericValues(left_value)
    attribute.updateExtremeNumericValues(right_value)
    self.is_date = is_date
  def isDate(self):
    return self.is_date
  def getValue(self):
    return (self.getLeftValue(), self.getRightValue())
  def getLeftValue(self):
    return self.left_value
  def getRightValue(self):
    return self.right_value
  def isQuantitative(self):
    return True
  def getRectangleKey(self):
    return self.getValue()
  def toVisString(self):
    left_value = None
    right_value = None
    attribute = self.getAttribute()
    result_str = None
    if attribute.isDateQuantitative() == True:
      left_value = IntervalItem.getStrUsingUTCDateInteger(self.getLeftValue())
      right_value = IntervalItem.getStrUsingUTCDateInteger(self.getRightValue())
      result_str = left_value + "..." + right_value
    elif attribute.isPercentQuantitative() == True or attribute.isDateQuantitative() == False:
      left_value = self.getLeftValue()
      right_value = self.getRightValue()
      result_str = str(left_value) + "..." + str(right_value)
    return result_str
  @staticmethod
  def getUTCDateInteger(item_value):
    date_obj, td_offset = dateTimeParse(item_value, True)
    epoch_based_time = getUnixTimeSec(date_obj)
    return epoch_based_time
  @staticmethod
  def getStrUsingUTCDateInteger(val):
    epoch_based_time = val
    date_obj = datetime.datetime.fromtimestamp(epoch_based_time)
    result_str = date_obj.strftime("%m/%d/%Y %I:%M %p +0000")
    return result_str
class CompositeIntervalItem(IntervalItem):
  def __init__(self, attribute, left_value, right_value, count = 1):
    IntervalItem.__init__(self, attribute, left_value, right_value, count)
class ItemSet:
  def __init__(self, ordered_items, count = 0):
    self.ordered_items = ordered_items
    self.count = count
    attributes = [x.getAttribute() for x in ordered_items]
    attribute_set = set(attributes)
    self.attribute_set = attribute_set
  def getOrderedItems(self):
    return self.ordered_items
  def getCount(self):
    return self.count
  def setCount(self, count):
    self.count = count
  def getNumOrderedItems(self):
    return len(self.getOrderedItems())
  def toString(self):
    ordered_items = self.getOrderedItems()
    ordered_item_str_list = [x.toString() for x in ordered_items] + [str(self.getCount())]
    result_str = "{" + string.join(ordered_item_str_list, ", ") + "}"
    return result_str
  def __repr__(self):
    return self.toString()
  def getFirstKOrderedItems(self, k):
    ordered_items = self.getOrderedItems()
    first_k_ordered_items = ordered_items[ : k]
    return first_k_ordered_items
  def getLastKOrderedItems(self, k):
    ordered_items = self.getOrderedItems()
    num_ordered_items = self.getNumOrderedItems()
    last_k_ordered_items = ordered_items[num_ordered_items - k : ]
    return last_k_ordered_items
  def comesBeforeItemSet(self, item_set):
    final_attribute1 = self.getFinalAttribute()
    final_attribute2 = item_set.getFinalAttribute()
    return final_attribute1.comesBefore(final_attribute)
  def hasAttribute(self, attribute):
    return attribute in self.attribute_set
  def getFinalAttribute(self):
    ordered_items = self.getOrderedItems()
    num_items = self.getNumOrderedItems()
    attribute = ordered_items[num_items - 1].getAttribute()
    return attribute
  def canMergeWithItemSet(self, item_set):
    final_attribute1 = self.getFinalAttribute()
    final_attribute2 = item_set.getFinalAttribute()
    pred1 = final_attribute1 != final_attribute2
    pred2 = self.hasAttribute(final_attribute2) == False
    pred3 = item_set.hasAttribute(final_attribute1) == False
    pred4 = final_attribute1.comesBefore(final_attribute2) == True
    result = pred1 == True and pred2 == True and pred3 == True and pred4 == True
    return result
  def mergeWithItemSet(self, item_set):
    left_ordered_items = self.getOrderedItems()
    right_ordered_items = item_set.getOrderedItems()
    curr_size = self.getNumOrderedItems()
    next_size = curr_size + 1
    shared_items = left_ordered_items[ : curr_size - 1]
    next_item = left_ordered_items[curr_size - 1]
    next_next_item = right_ordered_items[curr_size - 1]
    ordered_items = shared_items + [next_item] + [next_next_item]
    count = 0
    item_set = ItemSet(ordered_items, count)
    return item_set
  def clone(self):
    item_set = ItemSet(self.getOrderedItems()[ : ], self.getCount())
    return item_set
  def removeItem(self, i):
    self.ordered_items.pop(i)
    self.count = 0
  def getKey(self):
    result = [[x.getAttribute().getKey(), x.getKey()] for x in self.getOrderedItems()]
    next_result = reduce(lambda x, y: x + y, result)
    next_next_result = tuple(next_result)
    return next_next_result
  def getRectangleKey(self):
    ordered_items = self.getOrderedItems()
    ordered_interval_tuples = []
    for ordered_item in ordered_items:
      interval_tuple = None
      interval_tuple = ordered_item.getRectangleKey()
      ordered_interval_tuples.append(interval_tuple)
    rectangle_keys = ordered_interval_tuples
    upper_left = tuple([x[0] for x in rectangle_keys])
    lower_right = tuple([x[1] for x in rectangle_keys])
    result = (upper_left, lower_right)
    return result
  def getAttributeTuple(self):
    ordered_items = self.getOrderedItems()
    attributes = [x.getAttribute() for x in ordered_items]
    result = tuple(attributes)
    return result
  def spawnItemSets(self, size):
    ordered_items = self.getOrderedItems()
    num_ordered_items = self.getNumOrderedItems()
    result_item_list_list = ItemSet._spawnItemSetsHelperA(ordered_items, num_ordered_items, size)
    item_sets = [ItemSet(x, 0) for x in result_item_list_list]
    return item_sets
  @staticmethod
  def _spawnItemSetsHelperA(items, n, m):
    result_item_deque_list = ItemSet._spawnItemSetsHelperB(items, n, m, 0)
    result_item_list_list = [list(x) for x in result_item_deque_list]
    return result_item_list_list
  @staticmethod
  def _spawnItemSetsHelperB(items, n, m, a):
    if a == n and m != 0:
      return []
    elif a == n and m == 0:
      return [deque()]
    curr_item = items[a]
    suffix_deques = []
    suffix_exclude_deques = ItemSet._spawnItemSetsHelperB(items, n, m, a + 1)
    suffix_include_deques = []
    if m != 0:
      suffix_include_deques = ItemSet._spawnItemSetsHelperB(items, n, m - 1, a + 1)
    for suffix_include_deque in suffix_include_deques:
      suffix_include_deque.appendleft(curr_item)
    suffix_deques.extend(suffix_exclude_deques)
    suffix_deques.extend(suffix_include_deques)
    return suffix_deques
  @staticmethod
  def getExpectedValueRatio(item_set_reference, item_set, total_count, difference_item_sets = []):
    have_difference_item_set = len(difference_item_sets) != 0
    difference_item_list_list = None
    if have_difference_item_set == True:
      difference_item_list_list = [x.getOrderedItems() for x in difference_item_sets]
    reference_items = item_set_reference.getOrderedItems()
    items = item_set.getOrderedItems()
    num_items = len(reference_items)
    product = 1.0
    for i in xrange(num_items):
      reference_item = reference_items[i]
      item = items[i]
      term = None
      if item.isCategorical() == True:
        term = 1
      elif have_difference_item_set == False:
        term = item.getCount() / (1.0 * reference_item.getCount())
      elif have_difference_item_set == True:
        difference_sum = sum([x[i].getCount() for x in difference_item_list_list])
        term = (item.getCount() - difference_sum) / (1.0 * reference_item.getCount())
      product = product * term
    return product
  @staticmethod
  def getExpectedSupport(item_set_reference, item_set, total_count, difference_item_sets = []):
    support = item_set_reference.getCount() / (1.0 * total_count)
    ratio = ItemSet.getExpectedValueRatio(item_set_reference, item_set, total_count, difference_item_sets)
    expected_support = support * ratio
    return expected_support
  def getItemSetDifference(self, sub_item_set):
    item_set_a = self
    item_set_b = sub_item_set
    ordered_items_a = item_set_a.getOrderedItems()
    ordered_items_b = item_set_b.getOrderedItems()
    ordered_item_set_a = set(ordered_items_a)
    ordered_item_set_b = set(ordered_items_b)
    difference_item_set = ordered_item_set_a.difference(ordered_item_set_b)
    difference_items = list(difference_item_set)
    ordered_difference_items = sorted(difference_items, key = lambda x: x.getAttribute().getColumnNum())
    count = None
    item_set = ItemSet(ordered_difference_items, count)
    return item_set
  @staticmethod
  def isRInteresting(X_item_set, pre_r_interesting_x_tree, item_set_to_close_ancestor_entries_dict, total_count, R, difference_item_sets = [], overriding_close_ancestor_item_set = None):
    close_ancestor_item_sets = []
    have_overriding_close_ancestor_item_set = overriding_close_ancestor_item_set != None
    if have_overriding_close_ancestor_item_set == True:
      close_ancestor_item_sets = [overriding_close_ancestor_item_set]
    else:
      close_ancestor_entries = item_set_to_close_ancestor_entries_dict[X_item_set]
      close_ancestor_item_sets = [x.getMBR().getContainedItem() for x in close_ancestor_entries]
    rectangle_key = X_item_set.getRectangleKey()
    curr_left, curr_right = rectangle_key
    mbr = x_tree.RawMBR(curr_left, curr_right, X_item_set)
    curr_x_tree = pre_r_interesting_x_tree
    contained_entries = curr_x_tree.doContainmentQuery(mbr)
    contained_item_sets = [x.getMBR().getContainedItem() for x in contained_entries]
    contained_item_sets = [x for x in contained_item_sets if x != X_item_set]
    return ItemSet.isRInterestingHelper(X_item_set, pre_r_interesting_x_tree, total_count, close_ancestor_item_sets, difference_item_sets, True, contained_item_sets, R)
  @staticmethod
  def isRInterestingHelper(X_item_set, pre_r_interesting_x_tree, total_count, close_ancestor_item_sets, difference_item_sets, is_base_level, curr_contained_item_sets, R):
    have_difference_item_sets = len(difference_item_sets) != 0
    num_close_ancestor_item_sets = len(close_ancestor_item_sets)
    if num_close_ancestor_item_sets == 0:
      return True
    else:
      is_r_interesting = True
      for close_ancestor_item_set in close_ancestor_item_sets:
        if is_base_level == True:
          expected_support = ItemSet.getExpectedSupport(close_ancestor_item_set, X_item_set, total_count)
          support_a = X_item_set.getCount() / (1.0 * total_count)
          support_b = R * expected_support
          if not (support_a >= support_b):
            is_r_interesting = False
            break
      for specialization_item_set in curr_contained_item_sets:
        difference_item_set_list = difference_item_sets + [specialization_item_set]
        difference_expected_support = ItemSet.getExpectedSupport(close_ancestor_item_set, X_item_set, total_count, difference_item_set_list)
        difference_sum = sum([x.getCount() for x in difference_item_set_list])
        difference_support_a = (X_item_set.getCount() - difference_sum) / (1.0 * total_count)
        difference_support_b = R * difference_expected_support
        if not (difference_support_a >= difference_support_b):
          if True:
            is_r_interesting = False
            break
        curr_x_tree = pre_r_interesting_x_tree
        next_rectangle_key = specialization_item_set.getRectangleKey()
        next_left, next_right = next_rectangle_key
        next_mbr = x_tree.RawMBR(next_left, next_right, specialization_item_set)
        intersection_entries = curr_x_tree.doOverlapQuery(next_mbr)
        intersection_item_sets = [x.getMBR().getContainedItem() for x in intersection_entries]
        item_set_set_difference = list(set(curr_contained_item_sets).difference(set(intersection_item_sets)))
        next_curr_contained_item_sets = item_set_set_difference
        do_recurse = True
        if do_recurse == True:
          result = ItemSet.isRInterestingHelper(X_item_set, pre_r_interesting_x_tree, total_count, close_ancestor_item_sets, difference_item_sets + [specialization_item_set], False, next_curr_contained_item_sets, R)
          if result == False:
            is_r_interesting = False
            break
      if is_r_interesting == True:
        return True
      else:
        return False
  def getFullExtentRectangleKey(self):
    ordered_items = self.getOrderedItems()
    attributes = [x.getAttribute() for x in ordered_items]
    ordered_interval_tuples = []
    for attribute in attributes:
      interval_tuple = attribute.getFullExtent()
      ordered_interval_tuples.append(interval_tuple)
    rectangle_keys = ordered_interval_tuples
    upper_left = tuple([x[0] for x in rectangle_keys])
    lower_right = tuple([x[1] for x in rectangle_keys])
    result = (upper_left, lower_right)
    return result
  def toVisString(self, attributes):
    items = self.getOrderedItems()
    num_columns = len(attributes)
    column_num_to_str_dict = {}
    for attribute in attributes:
      column_num = attribute.getColumnNum()
      column_num_to_str_dict[column_num] = ""
    for item in items:
      attribute = item.getAttribute()
      column_num = attribute.getColumnNum()
      column_num_to_str_dict[column_num] = item.toVisString()
    str_list = [x[1] for x in sorted(column_num_to_str_dict.items(), key = lambda x: x[0])]
    result_str = string.join(str_list, ",")
    return result_str
class Rule:
  def __init__(self, l_item_set, r_item_set, overall_item_set, confidence, support):
    self.l_item_set = l_item_set
    self.r_item_set = r_item_set
    self.overall_item_set = overall_item_set
    self.confidence = confidence
    self.support = support
  def getLeftItemSet(self):
    return self.l_item_set
  def getRightItemSet(self):
    return self.r_item_set
  def getOverallItemSet(self):
    return self.overall_item_set
  def getConfidence(self):
    return self.confidence
  def getSupport(self):
    return self.support
  def toString(self):
    return (self.getLeftItemSet().toString(), self.getRightItemSet().toString())
  @staticmethod
  def getExpectedSupport(rule_reference, rule, total_count):
    item_set_reference = rule.getOverallItemSet()
    item_set = rule.getOverallItemSet()
    return ItemSet.getExpectedSupport(item_set_reference, item_set, total_count)
  @staticmethod
  def getExpectedConfidence(rule_reference, rule, total_count):
    confidence = rule_reference.getConfidence()
    item_set_reference = rule.getOverallItemSet()
    item_set = rule.getOverallItemSet()
    ratio = ItemSet.getExpectedValueRatio(item_set_reference, item_set, total_count)
    expected_confidence = confidence * ratio
    return expected_confidence
  @staticmethod
  def isRInteresting(rule, pre_r_interesting_x_tree, item_set_to_close_ancestor_entries_dict, total_count, item_set_to_rule_list_dict, R, difference_item_sets = []):
    X_item_set = rule.getOverallItemSet()
    close_ancestor_entries = item_set_to_close_ancestor_entries_dict[X_item_set]
    close_ancestor_item_sets = [x.getMBR().getContainedItem() for x in close_ancestor_entries]
    rectangle_key = X_item_set.getRectangleKey()
    curr_left, curr_right = rectangle_key
    mbr = x_tree.RawMBR(curr_left, curr_right, X_item_set)
    curr_x_tree = pre_r_interesting_x_tree
    contained_entries = curr_x_tree.doContainmentQuery(mbr)
    contained_item_sets = [x.getMBR().getContainedItem() for x in contained_entries]
    contained_item_sets = [x for x in contained_item_sets if x != X_item_set]
    return Rule.isRInterestingHelper(rule, pre_r_interesting_x_tree, total_count, close_ancestor_item_sets, difference_item_sets, True, contained_item_sets, item_set_to_rule_list_dict, R)
  @staticmethod
  def isRInterestingHelper(rule, pre_r_interesting_x_tree, total_count, close_ancestor_item_sets, difference_item_sets, is_base_level, curr_contained_item_sets, item_set_to_rule_list_dict, R):
    X_item_set = rule.getOverallItemSet()
    have_difference_item_sets = len(difference_item_sets) != 0
    num_close_ancestor_item_sets = len(close_ancestor_item_sets)
    if num_close_ancestor_item_sets == 0:
      return True
    else:
      is_r_interesting = True
      for close_ancestor_item_set in close_ancestor_item_sets:
        if is_base_level == True:
          curr_rules = item_set_to_rule_list_dict[close_ancestor_item_set]
          for curr_rule in curr_rules:
            expected_support = Rule.getExpectedSupport(curr_rule, rule, total_count)
            support_a = rule.getSupport()
            support_b = R * expected_support
            if not (support_a >= support_b):
              is_r_interesting = False
              break
            expected_confidence = Rule.getExpectedConfidence(curr_rule, rule, total_count)
            confidence_a = rule.getConfidence()
            confidence_b = R * expected_confidence
            if not (confidence_a >= confidence_b):
              is_r_interesting = False
              break
            result = ItemSet.isRInteresting(X_item_set, pre_r_interesting_x_tree, None, total_count, R, overriding_close_ancestor_item_set = close_ancestor_item_set)
            if result == False:
              is_r_interesting = False
              break
          if is_r_interesting == False:
            break
      if is_r_interesting == True:
        return True
      else:
        return False
  @staticmethod
  def getHeaderString(attributes):
    attribute_names = [x.getName() for x in attributes]
    header_str = string.join(attribute_names, ",")
    return header_str
  @staticmethod
  def getAttributeTypeStr(attributes):
    attribute_types = [x.toTypeString() for x in attributes]
    result_str = string.join(attribute_types, ",")
    return result_str
  def toVisString(self, attributes):
    item_set = self.getOverallItemSet()
    return item_set.toVisString(attributes)
  def toAntecedentVisString(self, attributes):
    item_set = self.getLeftItemSet()
    return item_set.toVisString(attributes)
  def toConsequentVisString(self, attributes):
    item_set = self.getRightItemSet()
    return item_set.toVisString(attributes)
  def toSupportAndConfidenceVisString(self):
    support = self.getSupport()
    confidence = self.getConfidence()
    support_str = str(support)
    confidence_str = str(confidence)
    return support_str + "," + confidence_str

def createQuantitativeAttributeBaseIntervalItems(items, num_partitions, attribute):
  numeric_values = [x.getLeftValue() for x in items]
  min_numeric_value = min(numeric_values)
  max_numeric_value = max(numeric_values)
  interval_items = []
  span = max_numeric_value - min_numeric_value
  bucket_size = span / (1.0 * num_partitions)
  for i in xrange(num_partitions):
    left = i * bucket_size + min_numeric_value
    right = (i + 1) * bucket_size + min_numeric_value
    interval = (left, right)
    interval_item = IntervalItem(attribute, left, right, 1)
    interval_items.append(interval_item)
  curr_x_tree = x_tree.RTree()
  for interval_item in interval_items:
    curr_left, curr_right = interval_item.getValue()
    curr_mbr = x_tree.RawMBR((curr_left,), (curr_right,), interval_item)
    curr_node = x_tree.RTreeNode(None, [], True)
    curr_entry = x_tree.RTreeEntry(curr_mbr, curr_node)
    curr_node.setEntry(curr_entry)
    curr_x_tree.insert(curr_entry)
  for item in items:
    curr_numeric_value = float(item.getLeftValue())
    curr_mbr = x_tree.RawMBR((curr_numeric_value,), (curr_numeric_value,), None)
    matching_interval_entries = curr_x_tree.doEnclosureQuery(curr_mbr)
    for matching_interval_entry in matching_interval_entries:
      matching_interval_item = matching_interval_entry.getMBR().getContainedItem()
      matching_interval_item.setCount(matching_interval_item.getCount() + item.getCount())
  return interval_items
def createFrequentQuantitativeAttributeCompositeIntervalAndExactItems(items, ordered_base_interval_items, attribute, min_support, max_support, num_data_rows):
  min_support_count = int(math.ceil(min_support * num_data_rows))
  max_support_count = int(math.ceil(max_support * num_data_rows))
  composite_interval_items = []
  active_interval_count_tuple_set = set([])
  ordered_base_intervals = [(x.getLeftValue(), x.getRightValue()) for x in ordered_base_interval_items]
  for i in xrange(len(ordered_base_interval_items)):
    base_interval = ordered_base_intervals[i]
    base_interval_item = ordered_base_interval_items[i]
    curr_count = base_interval_item.getCount()
    curr_interval_count_tuple = (base_interval, curr_count)
    prev_active_interval_count_tuples = list(active_interval_count_tuple_set)
    active_interval_count_tuple_set = set(prev_active_interval_count_tuples)
    active_interval_count_tuple_set |= set([curr_interval_count_tuple])
    for active_interval_count_tuple in prev_active_interval_count_tuples:
      active_interval, active_interval_count = active_interval_count_tuple
      next_support_count = active_interval_count + curr_count
      if next_support_count <= max_support_count:
        next_interval = (active_interval[0], base_interval[1])
        next_interval_count_tuple = (next_interval, next_support_count)
        active_interval_count_tuple_set |= set([next_interval_count_tuple])
      active_interval_count_tuple_set.remove(active_interval_count_tuple)
      prev_left_value = active_interval[0]
      prev_right_value = active_interval[1]
      if next_support_count >= min_support_count:
        composite_interval_item = CompositeIntervalItem(attribute, prev_left_value, base_interval[1], next_support_count)
        composite_interval_items.append(composite_interval_item)
  return [x for x in ordered_base_interval_items if x.getCount() >= min_support_count] + composite_interval_items
def getFrequentCompositeIntervalAndExactItemsForIndex(num_partitions, attribute, min_support, max_support, num_data_rows, column_index, all_items):
  curr_items = [x for x in all_items if x.getAttribute().getColumnNum() == column_index and x.hasDegenerateValue() == False]
  ordered_base_interval_items = createQuantitativeAttributeBaseIntervalItems(curr_items, num_partitions, attribute)
  composite_interval_items = createFrequentQuantitativeAttributeCompositeIntervalAndExactItems(curr_items, ordered_base_interval_items, attribute, min_support, max_support, num_data_rows)
  curr_items = composite_interval_items
  return curr_items

def getFrequentExactItemsForIndex(min_support, max_support, num_data_rows, column_index, all_items):
  frequent_exact_items = [x for x in all_items if x.getCount() / (1.0 * num_data_rows) >= min_support and x.hasDegenerateValue() == False and x.getAttribute().getColumnNum() == column_index]
  return frequent_exact_items

def doCandidateGeneration(frequent_items, item_sets, num_data_rows, min_support, max_support, min_confidence, R, num_acknowledged_attributes, row_item_sets, pprip_multiplier, attribute_column_num_to_attribute_dict, ordered_acknowledged_attribute_column_num_list, antecedent_stream, consequent_stream, support_and_confidence_stream):
  key_to_item_set_list_dict = defaultdict(lambda: [])
  L = defaultdict(lambda: [])
  C = defaultdict(lambda: [])
  D = defaultdict(lambda: [])
  print "Number of frequent items:", len(frequent_items)
  print "Phase #0: determining support for size-one item-sets"
  phase_zero_attribute_tuple_to_x_tree_dict = defaultdict(lambda: x_tree.RTree())
  for item_set in item_sets:
    rectangle_key = item_set.getRectangleKey()
    curr_left, curr_right = rectangle_key
    curr_mbr = x_tree.RawMBR(curr_left, curr_right, item_set)
    curr_node = x_tree.RTreeNode(None, [], True)
    curr_entry = x_tree.RTreeEntry(curr_mbr, curr_node)
    curr_node.setEntry(curr_entry)
    attribute_tuple = item_set.getAttributeTuple()
    curr_x_tree = phase_zero_attribute_tuple_to_x_tree_dict[attribute_tuple]
    curr_x_tree.insert(curr_entry)
  for row_item_set in row_item_sets:
    next_item_sets = row_item_set.spawnItemSets(1)
    attribute_tuple_tagged_item_sets = [(x.getAttributeTuple(), x) for x in next_item_sets]
    for attribute_tuple_tagged_item_set in attribute_tuple_tagged_item_sets:
      attribute_tuple, curr_item_set = attribute_tuple_tagged_item_set
      curr_x_tree = phase_zero_attribute_tuple_to_x_tree_dict[attribute_tuple]
      curr_rectangle_key = curr_item_set.getRectangleKey()
      upper_left, lower_right = curr_rectangle_key
      curr_mbr = x_tree.RawMBR(upper_left, lower_right, None)
      matching_entry_sets = curr_x_tree.doEnclosureQuery(curr_mbr)
      for matching_entry_set in matching_entry_sets:
        matching_item_set = matching_entry_set.getMBR().getContainedItem()
        matching_item_set.setCount(matching_item_set.getCount() + 1)
  L[1] = item_sets[ : ]
  print "Phase #0b: pre-emptive r-interesting pre-processing prune phase; diminishes quality"
  prune_count = int(math.ceil(1 / (1.0 * R) * num_data_rows))
  prune_count = prune_count * pprip_multiplier
  print "Prune support count:", prune_count
  L[1] = [x for x in L[1] if x.getCount() <= prune_count]
  L[1] = L[1]
  for j in xrange(2, num_acknowledged_attributes + 1):
    if len(L[j - 1]) == 0:
      continue
    print "Apriori iteration:", j
    print "Phase #1: join phase"
    for item_set in L[j - 1]:
      next_item_sets = item_set.spawnItemSets(j - 1)
      for next_item_set in next_item_sets:
        first_i_minus_one_ordered_items = next_item_set.getFirstKOrderedItems(j - 2)
        key = tuple(first_i_minus_one_ordered_items)
        key_to_item_set_list_dict[key].append(next_item_set)
    for item_set in L[j - 1]:
      first_i_minus_one_ordered_items = item_set.getFirstKOrderedItems(j - 2)
      key = tuple(first_i_minus_one_ordered_items)
      matching_partners = [x for x in key_to_item_set_list_dict[key] if x != item_set]
      valid_partners = [x for x in matching_partners if item_set.canMergeWithItemSet(x) == True]
      merge_item_sets = [item_set.mergeWithItemSet(x) for x in valid_partners]
      C[j].extend(merge_item_sets)
    print "Phase #2: subset prune phase"
    if len(C[j]) == 0:
      continue
    prev_L_key_set = set([x.getKey() for x in L[j - 1]])
    for item_set in C[j]:
      do_keep = True
      for i in xrange(j):
        next_item_set = item_set.clone()
        next_item_set.removeItem(i)
        curr_key = next_item_set.getKey()
        if curr_key not in prev_L_key_set:
          do_keep = False
          break
      if do_keep == True:
        D[j].append(item_set)
    print "Item-sets for current iteration surviving subset prune:", len(D[j])
    if len(D[j]) == 0:
      continue
    print "Phase #3: determining support"
    phase_three_attribute_tuple_to_x_tree_dict = defaultdict(lambda: x_tree.RTree())
    for item_set in D[j]:
      rectangle_key = item_set.getRectangleKey()
      upper_left, lower_right = rectangle_key
      curr_mbr = x_tree.RawMBR(upper_left, lower_right, item_set)
      curr_node = x_tree.RTreeNode(None, [], True)
      curr_entry = x_tree.RTreeEntry(curr_mbr, curr_node)
      curr_node.setEntry(curr_entry)
      attribute_tuple = item_set.getAttributeTuple()
      curr_x_tree = phase_three_attribute_tuple_to_x_tree_dict[attribute_tuple]
      curr_x_tree.insert(curr_entry)
    for row_item_set in row_item_sets:
      next_item_sets = row_item_set.spawnItemSets(j)
      attribute_tuple_tagged_item_sets = [(x.getAttributeTuple(), x) for x in next_item_sets]
      for attribute_tuple_tagged_item_set in attribute_tuple_tagged_item_sets:
        attribute_tuple, curr_item_set = attribute_tuple_tagged_item_set
        curr_x_tree = phase_three_attribute_tuple_to_x_tree_dict[attribute_tuple]
        curr_rectangle_key = curr_item_set.getRectangleKey()
        upper_left, lower_right = curr_rectangle_key
        curr_mbr = x_tree.RawMBR(upper_left, lower_right, None)
        matching_entry_sets = curr_x_tree.doEnclosureQuery(curr_mbr)
        for matching_entry_set in matching_entry_sets:
          matching_item_set = matching_entry_set.getMBR().getContainedItem()
          matching_item_set.setCount(matching_item_set.getCount() + 1)
    print "Phase #4: support-prune phase using min. support"
    E = defaultdict(lambda: [])
    min_support_count = int(math.ceil(min_support * num_data_rows))
    E[j] = [x for x in D[j] if x.getCount() >= min_support_count]
    L[j] = E[j]
    if len(L[j]) == 0:
      continue
  print "Phase #5: support-prune post-processing phase using max. support"
  max_support_count = int(math.ceil(max_support * num_data_rows))
  curr_item_sets = reduce(lambda x, y: x + y, L.values())
  next_item_sets = [x for x in curr_item_sets if x.getCount() <= max_support_count]
  print "Phase #6: r-interesting item-set pruning post-processing"
  phase_six_attribute_tuple_to_x_tree_dict = defaultdict(lambda: x_tree.RTree())
  r_interesting_item_sets = []
  item_set_entries = []
  for item_set in next_item_sets:
    curr_left, curr_right = item_set.getRectangleKey()
    curr_mbr = x_tree.RawMBR(curr_left, curr_right, item_set)
    curr_node = x_tree.RTreeNode(None, [], True)
    curr_entry = x_tree.RTreeEntry(curr_mbr, curr_node)
    curr_node.setEntry(curr_entry)
    attribute_tuple = item_set.getAttributeTuple()
    curr_x_tree = phase_six_attribute_tuple_to_x_tree_dict[attribute_tuple]
    curr_x_tree.insert(curr_entry)
    item_set_entries.append(curr_entry)
  attribute_tuple_to_item_set_to_close_ancestor_entries_dict_dict = {}
  for item in phase_six_attribute_tuple_to_x_tree_dict.items():
    attribute_tuple, curr_x_tree = item
    entry_to_close_ancestor_entries_dict = curr_x_tree.getAllRectangleCloseAncestors()
    item_set_to_close_ancestor_entries_dict = {}
    for entry, close_ancestor_entries in entry_to_close_ancestor_entries_dict.items():
      curr_item_set = entry.getMBR().getContainedItem()
      item_set_to_close_ancestor_entries_dict[curr_item_set] = close_ancestor_entries
    attribute_tuple_to_item_set_to_close_ancestor_entries_dict_dict[attribute_tuple] = item_set_to_close_ancestor_entries_dict
  total_count = num_data_rows
  for item_set_entry in item_set_entries:
    item_set = item_set_entry.getMBR().getContainedItem()
    attribute_tuple = item_set.getAttributeTuple()
    curr_x_tree = phase_six_attribute_tuple_to_x_tree_dict[attribute_tuple]
    item_set_to_close_ancestor_entries_dict = attribute_tuple_to_item_set_to_close_ancestor_entries_dict_dict[attribute_tuple]
    if ItemSet.isRInteresting(item_set, curr_x_tree, item_set_to_close_ancestor_entries_dict, total_count, R) == True:
      r_interesting_item_sets.append(item_set)
  print "Number of r-interesting item-sets:", len(r_interesting_item_sets)
  print "Phase #7: generating rules"
  rectangle_key_to_item_set_dict = {}
  frequent_item_sets = reduce(lambda x, y: x + y, L.values())
  attribute_tuple_to_rectangle_key_to_item_set_dict_dict = defaultdict(lambda: {})
  for frequent_item_set in frequent_item_sets:
    rectangle_key = frequent_item_set.getRectangleKey()
    attribute_tuple = frequent_item_set.getAttributeTuple()
    attribute_tuple_to_rectangle_key_to_item_set_dict_dict[attribute_tuple][rectangle_key] = frequent_item_set
  rules = []
  for item_set in r_interesting_item_sets:
    l_k_item_set = item_set
    a_m_item_set = item_set
    curr_rules = genRules(l_k_item_set, a_m_item_set, total_count, min_confidence, attribute_tuple_to_rectangle_key_to_item_set_dict_dict, attribute_column_num_to_attribute_dict, ordered_acknowledged_attribute_column_num_list)
    rules.extend(curr_rules)
  print "Number of rules generated:", len(rules)
  print "Phase #8: rule r-interesting pruning"
  item_set_to_rule_list_dict = defaultdict(lambda: [])
  for rule in rules:
    item_set = rule.getOverallItemSet()
    item_set_to_rule_list_dict[item_set].append(rule)
  r_interesting_rules = []
  phase_eight_attribute_tuple_to_x_tree_dict = phase_six_attribute_tuple_to_x_tree_dict
  for rule in rules:
    item_set = rule.getOverallItemSet()
    attribute_tuple = item_set.getAttributeTuple()
    curr_x_tree = phase_eight_attribute_tuple_to_x_tree_dict[attribute_tuple]
    item_set_to_close_ancestor_entries_dict = attribute_tuple_to_item_set_to_close_ancestor_entries_dict_dict[attribute_tuple]
    if Rule.isRInteresting(rule, curr_x_tree, item_set_to_close_ancestor_entries_dict, total_count, item_set_to_rule_list_dict, R) == True:
      r_interesting_rules.append(rule)
  print "Number of r-interesting rules:", len(r_interesting_rules)
  print "Phase #9: rule vis. text printing"
  sorted_r_interesting_rules = sorted(r_interesting_rules, key = lambda x: (x.getSupport(), x.getConfidence()), reverse = True)
  attributes = []
  for i in sorted(attribute_column_num_to_attribute_dict.keys()):
    attribute = attribute_column_num_to_attribute_dict[i]
    attributes.append(attribute)
  header_str = Rule.getHeaderString(attributes)
  type_str = Rule.getAttributeTypeStr(attributes)
  antecedent_stream.write(header_str + "\n")
  consequent_stream.write(header_str + "\n")
  antecedent_stream.write(type_str + "\n")
  consequent_stream.write(type_str + "\n")
  antecedent_str_list = [x.toAntecedentVisString(attributes) for x in sorted_r_interesting_rules]
  consequent_str_list = [x.toConsequentVisString(attributes) for x in sorted_r_interesting_rules]
  support_and_confidence_str_list = [x.toSupportAndConfidenceVisString() for x in sorted_r_interesting_rules]
  for antecedent_str in antecedent_str_list:
    antecedent_stream.write(antecedent_str + "\n")
  for consequent_str in consequent_str_list:
    consequent_stream.write(consequent_str + "\n")
  support_and_confidence_stream.write("SUPPORT,CONFIDENCE" + "\n")
  for support_and_confidence_str in support_and_confidence_str_list:
    support_and_confidence_stream.write(support_and_confidence_str + "\n")

def genRules(l_k_item_set, a_m_item_set, total_count, min_conf, attribute_tuple_to_rectangle_key_to_item_set_dict_dict, attribute_column_num_to_attribute_dict, ordered_acknowledged_attribute_column_num_list):
  result_rules = []
  genRulesHelper(l_k_item_set, a_m_item_set, total_count, min_conf, result_rules, attribute_tuple_to_rectangle_key_to_item_set_dict_dict, attribute_column_num_to_attribute_dict, ordered_acknowledged_attribute_column_num_list)
  return result_rules
def genRulesHelper(l_k_item_set, a_m_item_set, total_count, min_conf, result_rules, attribute_tuple_to_rectangle_key_to_item_set_dict_dict, attribute_column_num_to_attribute_dict, ordered_acknowledged_attribute_column_num_list):
  if a_m_item_set.getNumOrderedItems() < 2:
    return
  A = a_m_item_set.spawnItemSets(a_m_item_set.getNumOrderedItems() - 1)
  for item_set in A:
    rectangle_key = item_set.getRectangleKey()
    attribute_tuple = item_set.getAttributeTuple()
    rectangle_key_to_item_set_dict = attribute_tuple_to_rectangle_key_to_item_set_dict_dict[attribute_tuple]
    next_item_set = rectangle_key_to_item_set_dict[rectangle_key]
    actual_count = next_item_set.getCount()
    conf = l_k_item_set.getCount() / (1.0 * actual_count)
    if conf >= min_conf:
      rule = Rule(next_item_set, l_k_item_set.getItemSetDifference(next_item_set), l_k_item_set, conf, l_k_item_set.getCount() / (1.0 * total_count))
      result_rules.append(rule)
      if (a_m_item_set.getNumOrderedItems() - 1) > 1:
        genRulesHelper(l_k_item_set, next_item_set, total_count, min_conf, result_rules, attribute_tuple_to_rectangle_key_to_item_set_dict_dict, attribute_column_num_to_attribute_dict, ordered_acknowledged_attribute_column_num_list)

def main():

  stream = sys.stdin
  line = stream.readline()
  line = line.rstrip("\n")
  args = line.split(" ")
  args = [string.atof(x) for x in args if x != ""]
  min_support = args[0]
  max_support = args[1]
  min_confidence = args[2]
  R = args[3]
  K = args[4]
  pprip_multiplier = args[5]
  line = stream.readline()
  line = line.rstrip("\n")
  args = line.split(" ")
  args = [string.atoi(x) for x in args if x != ""]
  non_date_quantitative_attribute_indices = args
  line = stream.readline()
  line = line.rstrip("\n")
  args = line.split(" ")
  args = [string.atoi(x) for x in args if x != ""]
  categorical_attribute_indices = args
  line = stream.readline()
  line = line.rstrip("\n")
  args = line.split(" ")
  args = [string.atoi(x) for x in args if x != ""]
  date_quantitative_attribute_indices = args
  line = stream.readline()
  line = line.rstrip("\n")
  args = line.split(" ")
  args = [string.atoi(x) for x in args if x != ""]
  percent_quantitative_attribute_indices = args
  line = stream.readline()
  line = line.rstrip("\n")
  input_csv_path = line
  line = stream.readline()
  line = line.rstrip("\n")
  output_antecedent_csv_path = line
  line = stream.readline()
  line = line.rstrip("\n")
  output_consequent_csv_path = line
  line = stream.readline()
  line = line.rstrip("\n")
  output_sc_csv_path = line
  antecedent_stream = open(output_antecedent_csv_path, "w")
  consequent_stream = open(output_consequent_csv_path, "w")
  support_and_confidence_stream = open(output_sc_csv_path, "w")
  csv_stream1 = open(input_csv_path, "rb")
  csv_stream2 = open(input_csv_path, "rb")
  
  csv_reader1 = csv.reader(csv_stream1, delimiter = ",", quotechar = "|")
  num_data_rows = 0
  while True:
    line = csv_stream2.readline()
    if line == "":
      break
    num_data_rows += 1
  num_data_rows -= 2
  type_row = csv_reader1.next()
  name_row = csv_reader1.next()
  attribute_column_num_to_attribute_dict = {}
  quantitative_attribute_indices = sorted(non_date_quantitative_attribute_indices + date_quantitative_attribute_indices + percent_quantitative_attribute_indices)
  num_acknowledged_attributes = len(categorical_attribute_indices) + len(quantitative_attribute_indices)
  ordered_acknowledged_attribute_column_num_list = sorted(quantitative_attribute_indices + categorical_attribute_indices)
  ndqai_set = set(non_date_quantitative_attribute_indices)
  cai_set = set(categorical_attribute_indices)
  dqai_set = set(date_quantitative_attribute_indices)
  pqai_set = set(percent_quantitative_attribute_indices)
  num_attributes = len(name_row)
  for i in xrange(num_attributes):
    name = name_row[i]
    attribute = None
    if i in ndqai_set:
      attribute = QuantitativeAttribute(i, name)
    elif i in cai_set:
      attribute = CategoricalAttribute(i, name)
    elif i in dqai_set:
      attribute = DateQuantitativeAttribute(i, name)
    elif i in pqai_set:
      attribute = PercentQuantitativeAttribute(i, name)
    if attribute != None:
      attribute_column_num_to_attribute_dict[i] = attribute
  attribute_item_value_tuple_to_item_dict = {}
  row_item_sets = []
  for i in xrange(num_data_rows):
    row = csv_reader1.next()
    row_items = []
    for j in xrange(len(row)):
      if j not in attribute_column_num_to_attribute_dict:
        continue
      attribute = attribute_column_num_to_attribute_dict[j]
      item_value = row[j]
      curr_tuple = (attribute, item_value)
      if curr_tuple in attribute_item_value_tuple_to_item_dict:
        item = attribute_item_value_tuple_to_item_dict[curr_tuple]
        item.setCount(item.getCount() + 1)
        row_items.append(item)
      else:
        item = None
        if Item.isDegenerateValue(item_value) == True:
          continue
        if attribute.isQuantitative() == True:
          if attribute.isDateQuantitative() == True:
            date_int = IntervalItem.getUTCDateInteger(item_value)
            item = IntervalItem(attribute, date_int, date_int, is_date = True)
          if attribute.isPercentQuantitative == True or attribute.isDateQuantitative() == False:
            item = IntervalItem(attribute, float(item_value), float(item_value), 1)
        elif attribute.isCategorical() == True:
          item = CategoricalItem(attribute, item_value, 1)
        attribute_item_value_tuple_to_item_dict[curr_tuple] = item
        row_items.append(item)
    item_set = ItemSet(row_items, 0)
    row_item_sets.append(item_set)
  num_partitions = int(math.ceil(2 * len(quantitative_attribute_indices) / (1.0 * min_support * (K - 1))))
  print "Number of partitions for quantitative attributes:", num_partitions

  column_index_to_quantitative_items_dict = {}
  for column_index in quantitative_attribute_indices:
    result = getFrequentCompositeIntervalAndExactItemsForIndex(num_partitions, attribute_column_num_to_attribute_dict[column_index], min_support, max_support, num_data_rows, column_index, attribute_item_value_tuple_to_item_dict.values())
    column_index_to_quantitative_items_dict[column_index] = result
  column_index_to_categorical_items_dict = {}

  for column_index in categorical_attribute_indices:
    result = getFrequentExactItemsForIndex(min_support, max_support, num_data_rows, column_index, attribute_item_value_tuple_to_item_dict.values())
    column_index_to_categorical_items_dict[column_index] = result
  column_index_to_frequent_items_dict = column_index_to_quantitative_items_dict.copy()
  column_index_to_frequent_items_dict.update(column_index_to_categorical_items_dict)
  ordered_column_indices = sorted(quantitative_attribute_indices + categorical_attribute_indices)

  frequent_items = reduce(lambda x, y: x + y, column_index_to_frequent_items_dict.values(), [])
  frequent_items = sorted(frequent_items, key = lambda x: x.getKey())
  item_sets = [ItemSet([x], 0) for x in frequent_items]
  doCandidateGeneration(frequent_items, item_sets, num_data_rows, min_support, max_support, min_confidence, R, num_acknowledged_attributes, row_item_sets, pprip_multiplier, attribute_column_num_to_attribute_dict, ordered_acknowledged_attribute_column_num_list, antecedent_stream, consequent_stream, support_and_confidence_stream)
  antecedent_stream.close()
  consequent_stream.close()
  support_and_confidence_stream.close()
  csv_stream1.close()
  csv_stream2.close()

if __name__ == "__main__":
  main()
