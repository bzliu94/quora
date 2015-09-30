# 2015-09-29

# memoize item sets on basis of word base node

# inspired by ishaan gulrajani

class Tree:
  def __init__(self):
    self.root = None
  def getRoot(self):
    return self.root
  def setRoot(self, v):
    self.root = v
class Node:
  def __init__(self, element, parent, children):
    self.element = element
    self.parent = parent
    self.item_set = set([])
    children_dict = {}
    for child in children:
      key = child.element
      children_dict[key] = child
    self.children_dict = children_dict
  def getItemSet(self):
    return self.item_set
  def addItem(self, item):
    (self.item_set).add(item)
  def addItems(self, items):
    for item in items:
      self.addItem(item)
  def removeItem(self, item):
    item_set = self.item_set
    if item in item_set:
      item_set.remove(item)
  def removeItems(self, items):
    for item in items:
      self.removeItem(item)
  def getElement(self):
    return self.element
  def getParent(self):
    return self.parent
  def getChildren(self):
    return (self.children_dict).values()
  def getNumChildren(self):
    children_dict = self.children_dict
    num_children = len(children_dict)
    return num_children
  def getChild(self, key):
    return (self.children_dict)[key]
  def setElement(self, element):
    self.element = element
  def setParent(self, v):
    self.parent = v
  def addChild(self, v):
    key = v.element
    (self.children_dict)[key] = v
  def removeChild(self, v):
    key = v.element
    (self.children_dict).pop(key)
  def getDepth(self):
    if self.parent == None:
      return 0
    else:
      return (self.parent).getDepth() + 1
  def haveChild(self, element):
    return element in self.children_dict
class Trie(Tree):
  def __init__(self):
    Tree.__init__(self)
    root = Node(None, None, [])
    self.setRoot(root)
  def haveChildWithCharacter(self, node, character):
    element = character
    result = node.haveChild(element)
    return result
  def addWord(self, items, word):
    word = word + '\0'
    root = self.getRoot()
    curr_node = root
    item_set = root.item_set
    for item in items:
      item_set.add(item)
    for char in word:
      if curr_node.haveChild(char) == True:
        curr_node = curr_node.getChild(char)
      else:
        node = Node(char, curr_node, [])
        curr_node.addChild(node)
        curr_node = node
      item_set = curr_node.item_set
      for item in items:
        item_set.add(item)
  def hasPrefix(self, prefix):
    word = prefix
    root = self.getRoot()
    curr_node = root
    next_nodes = (root.children_dict).values()
    for char in word:
      if curr_node.haveChild(char) == True:
        curr_node = curr_node.getChild(char)
      else:
        return False
    return True
  def hasWord(self, word):
    next_word = word + '\0'
    return self.hasPrefix(next_word)
  def isWordTerminatorNode(self, node):
    return node.element == '\0'
  def isNodeForAWord(self, node):
    children = (node.children_dict).values()
    for child in children:
      if self.isWordTerminatorNode(child):
        return True
    return False
  def isNodeForAnExtendableWordBase(self, node):
    if len(node.children_dict) == 1 and self.isNodeForAWord(node):
      return False
    return True
  def getWordBaseNode(self, word_base):
    root = self.getRoot()
    curr_node = root
    for char in word_base:
      if curr_node.haveChild(char) == True:
        curr_node = curr_node.getChild(char)
      else:
        return None
    return curr_node
  def getPrefixForNode(self, node):
    path_chars = self.getPrefixForNodeHelper(node, [])
    prefix = "".join(path_chars)
    return prefix
  def getPrefixForNodeHelper(self, node, path_chars):
    if node == self.getRoot():
      return path_chars
    else:
      curr_char = node.element
      return self.getPrefixForNodeHelper(node.getParent(), [curr_char] + path_chars)
  def _retrieveItemsInSubtree(self, word):
    node = self.getWordBaseNode(word)
    if node != None:
      return node.getItemSet()
    else:
      return set([])
  def toString(self):
    root = self.getRoot()
    result = self.toStringHelper(root)
    return result
  def toStringHelper(self, node):
    children = node.getChildren()
    num_children = len(children)
    if num_children == 0:
      return "\\0"
    curr_entry_str = node.element
    component_str_list = []
    if node != self.getRoot():
      component_str_list.append(curr_entry_str)
    child_str_list = [self.toStringHelper(children[i]) for i in xrange(num_children)]
    component_str_list = component_str_list + child_str_list
    if (len(child_str_list) == 1 and self.isWordTerminatorNode(children[0]) == True) == False:
      partial_str = "(" + " ".join(component_str_list) + ")"
    else:
      partial_str = "(" + curr_entry_str + ")"
    return partial_str
  def removeWord(self, items, word, do_remove_nodes):
    root = self.getRoot()
    node = self.removeWordHelper1(root, word)
    if node == None:
      return
    have_children_to_keep = node.getNumChildren() > 0
    self.removeWordHelper2(items, node, do_remove_nodes, have_children_to_keep, True)
  def removeWordHelper1(self, node, word):
    next_word = word + '\0'
    node = self.getWordBaseNode(next_word)
    return node
  def removeWordHelper2(self, items, node, do_remove_nodes, have_children_to_keep, is_first_call):
    node.removeItems(items)
    if node == self.getRoot():
      return
    else:
      parent = node.getParent()
      num_children = parent.getNumChildren()
      next_have_children_to_keep = None
      if do_remove_nodes == True and have_children_to_keep == False:
        parent.removeChild(node)
        next_have_children_to_keep = have_children_to_keep or parent.getNumChildren() > 0
      else:
        next_have_children_to_keep = have_children_to_keep or parent.getNumChildren() > 1
      self.removeWordHelper2(items, parent, do_remove_nodes, next_have_children_to_keep, False)
  def getPreorderNodes(self):
    root = self.getRoot()
    return self.getPreorderNodesHelper(root)
  def getPreorderNodesHelper(self, node):
    children = (node.children_dict).values()
    node_list = []
    node_list.append(node)
    for child in children:
      curr_node_list = self.getPreorderNodesHelper(child)
      node_list = node_list + curr_node_list
    return node_list
  def getPreorderItemSetCounts(self):
    root = self.getRoot()
    result = [len(x.getItemSet()) for x in self.getPreorderNodes()]
    return result
class Command:
  def __init__(self):
    pass
  def handle(self, trie, user_list_dict, topic_list_dict, question_list_dict, board_list_dict, word_count_dict, id_to_item_dict, id_to_word_list_dict, word_to_id_to_count_dict_dict):
    pass
class AddCommand(Command):
  def __init__(self, type_value, id_str, score, data_string, item_numeric_id_value):
    self.type_value = type_value
    self.id_str = id_str
    self.score = score
    self.data_string = data_string
    self.item_numeric_id_value = item_numeric_id_value
  def getTypeValue(self):
    return self.type_value
  def getIDString(self):
    return self.id_str
  def getScore(self):
    return self.score
  def getDataString(self):
    return self.data_string
  def getItemNumericIDValue(self):
    return self.item_numeric_id_value
  def handle(self, trie, user_list_dict, topic_list_dict, question_list_dict, board_list_dict, word_count_dict, id_to_item_dict, id_to_word_list_dict, word_to_id_to_count_dict_dict):
    data_string = self.getDataString()
    type_value = self.getTypeValue()
    id_value = self.getIDString()
    score = self.getScore()
    item_numeric_id_value = self.getItemNumericIDValue()
    item = makeItemUsingTypeCode(type_value, id_value, score, item_numeric_id_value)
    id_to_item_dict[id_value] = item
    items = [item]
    words = data_string.split()
    for word in words:
      next_word = word.lower()
      trie.addWord(items, next_word)
      word_count_dict[next_word] += 1
      id_to_word_list_dict[id_value].append(next_word)
      word_to_id_to_count_dict_dict[next_word][id_value] += 1
    addToCollection(user_list_dict, topic_list_dict, question_list_dict, board_list_dict, item)
class DelCommand(Command):
  def __init__(self, id_str):
    self.id_str = id_str
  def getIDString(self):
    return self.id_str
  def handle(self, trie, user_list_dict, topic_list_dict, question_list_dict, board_list_dict, word_count_dict, id_to_item_dict, id_to_word_list_dict, word_to_id_to_count_dict_dict):
    id_value = self.getIDString()
    if id_value not in id_to_item_dict:
      return
    item = id_to_item_dict[id_value]
    items = [item]
    words = id_to_word_list_dict[id_value]
    for word in words:
      next_word = word.lower()
      do_remove_nodes = word_count_dict[next_word] == 1
      trie.removeWord(items, next_word, do_remove_nodes)
      if do_remove_nodes == True:
        word_count_dict.pop(next_word)
      word_to_id_to_count_dict_dict[next_word][id_value] -= 1
      if word_to_id_to_count_dict_dict[next_word][id_value] == 0:
        word_to_id_to_count_dict_dict[next_word].pop(id_value)
      if len(word_to_id_to_count_dict_dict[next_word]) == 0:
        word_to_id_to_count_dict_dict.pop(next_word)
    removeFromCollection(user_list_dict, topic_list_dict, question_list_dict, board_list_dict, item)
    id_to_item_dict.pop(id_value)
    id_to_word_list_dict.pop(id_value)
class QueryCommand(Command):
  def __init__(self, num_results, query_string):
    self.num_results = num_results
    self.query_string = query_string
  def getNumResults(self):
    return self.num_results
  def getQueryString(self):
    return self.query_string
  def handle(self, trie, user_list_dict, topic_list_dict, question_list_dict, board_list_dict, word_count_dict, id_to_item_dict, id_to_word_list_dict, word_to_id_to_count_dict_dict):
    num_results = self.getNumResults()
    query_string = self.getQueryString()
    query_words = query_string.split()
    item_set = set([])
    seen_first_set = False
    for query_word in query_words:
      next_query_word = query_word.lower()
      curr_item_set = set([])
      curr_item_set = trie._retrieveItemsInSubtree(next_query_word)
      if len(curr_item_set) != 0:
        pass
      else:
        item_set = set([])
        break
      if seen_first_set == False:
        item_set = curr_item_set
        seen_first_set = True
      else:
        item_set = item_set & curr_item_set
    item_list = list(item_set)
    score_tagged_item_list = [((x.getScore(), x.getItemNumericIDValue()), x) for x in item_list]
    sorted_score_tagged_item_list = score_tagged_item_list[ : ]
    sorted_score_tagged_item_list.sort(key = lambda x: x[0], reverse = True)
    culled_sorted_score_tagged_item_list = sorted_score_tagged_item_list[0 : num_results]
    culled_sorted_id_values = [x[1].getIDString() for x in culled_sorted_score_tagged_item_list]
    result_str = " ".join(culled_sorted_id_values)
    print result_str
class WQueryCommand(Command):
  def __init__(self, num_results, boosts, query_string):
    self.num_results = num_results
    self.boosts = boosts
    self.query_string = query_string
  def getNumResults(self):
    return self.num_results
  def getBoosts(self):
    return self.boosts
  def getQueryString(self):
    return self.query_string
  def handle(self, trie, user_list_dict, topic_list_dict, question_list_dict, board_list_dict, word_count_dict, id_to_item_dict, id_to_word_list_dict, word_to_id_to_count_dict_dict):
    type_value_to_overall_multiplier_dict = defaultdict(lambda: 1)
    id_value_to_overall_multiplier_dict = defaultdict(lambda: 1)
    num_results = self.getNumResults()
    boosts = self.getBoosts()
    query_string = self.getQueryString()
    for boost in boosts:
      if boost.isTypeBoost():
        type_value = boost.getTypeValue()
        multiplier_value = boost.getMultiplierValue()
        type_value_to_overall_multiplier_dict[type_value] *= multiplier_value
      elif boost.isItemBoost():
        id_value = boost.getItemIDValue()
        multiplier_value = boost.getMultiplierValue()
        id_value_to_overall_multiplier_dict[id_value] *= multiplier_value
    query_words = query_string.split()
    item_set = set([])
    seen_first_set = False
    for query_word in query_words:
      next_query_word = query_word.lower()
      curr_item_set = set([])
      curr_item_set = trie._retrieveItemsInSubtree(next_query_word)
      if len(curr_item_set) != 0:
        pass
      else:
        item_set = set([])
        break
      if seen_first_set == False:
        item_set = curr_item_set
        seen_first_set = True
      else:
        item_set = item_set & curr_item_set
    item_list = list(item_set)
    score_tagged_item_list = [((x.getScore() * type_value_to_overall_multiplier_dict[getTypeCodeForItem(x)] * id_value_to_overall_multiplier_dict[x.getIDString()], x.getItemNumericIDValue()), x) for x in item_list]
    sorted_score_tagged_item_list = score_tagged_item_list[ : ]
    sorted_score_tagged_item_list.sort(key = lambda x: x[0], reverse = True)
    culled_sorted_score_tagged_item_list = sorted_score_tagged_item_list[0 : num_results]
    culled_sorted_id_values = [x[1].getIDString() for x in culled_sorted_score_tagged_item_list]
    result_str = " ".join(culled_sorted_id_values)
    print result_str
class Boost:
  def __init__(self, multiplier_value):
    self.multiplier_value = multiplier_value
  def getMultiplierValue(self):
    return self.multiplier_value
  def isTypeBoost(self):
    return False
  def isItemBoost(self):
    return False
class TypeBoost(Boost):
  def __init__(self, type_value, multiplier_value):
    Boost.__init__(self, multiplier_value)
    self.type_value = type_value
  def getTypeValue(self):
    return self.type_value
  def isTypeBoost(self):
    return True
class ItemBoost(Boost):
  def __init__(self, id_value, multiplier_value):
    Boost.__init__(self, multiplier_value)
    self.id_value = id_value
  def getItemIDValue(self):
    return self.id_value
  def isItemBoost(self):
    return True
class Item:
  def __init__(self, id_str, score, item_numeric_id_value):
    self.id_str = id_str
    self.score = score
    self.item_numeric_id_value = item_numeric_id_value
  def getIDString(self):
    return self.id_str
  def getScore(self):
    return self.score
  def getItemNumericIDValue(self):
    return self.item_numeric_id_value
  def isUser(self):
    return False
  def isTopic(self):
    return False
  def isQuestion(self):
    return False
  def isBoard(self):
    return False
class User(Item):
  def __init__(self, id_str, score, item_numeric_id_value):
    Item.__init__(self, id_str, score, item_numeric_id_value)
  def isUser(self):
    return True
class Topic(Item):
  def __init__(self, id_str, score, item_numeric_id_value):
    Item.__init__(self, id_str, score, item_numeric_id_value)
  def isTopic(self):
    return True
class Question(Item):
  def __init__(self, id_str, score, item_numeric_id_value):
    Item.__init__(self, id_str, score, item_numeric_id_value)
  def isQuestion(self):
    return True
class Board(Item):
  def __init__(self, id_str, score, item_numeric_id_value):
    Item.__init__(self, id_str, score, item_numeric_id_value)
  def isBoard(self):
    return True
USER = 1
TOPIC = 2
QUESTION = 3
BOARD = 4
def getTypeCode(type_str):
  if type_str == "user":
    return USER
  elif type_str == "topic":
    return TOPIC
  elif type_str == "question":
    return QUESTION
  elif type_str == "board":
    return BOARD
def makeItemUsingTypeCode(type_value, id_value, score, item_numeric_id_value):
  if type_value == USER:
    return User(id_value, score, item_numeric_id_value)
  elif type_value == TOPIC:
    return Topic(id_value, score, item_numeric_id_value)
  elif type_value == QUESTION:
    return Question(id_value, score, item_numeric_id_value)
  elif type_value == BOARD:
    return Board(id_value, score, item_numeric_id_value)
def getTypeCodeForItem(item):
  if item.isUser():
    return USER
  elif item.isTopic():
    return TOPIC
  elif item.isQuestion():
    return QUESTION
  elif item.isBoard():
    return BOARD
def makeBoostGivenQualifier(qualifier_str, multiplier):
  boost = None
  if qualifier_str == "user" or qualifier_str == "topic" or qualifier_str == "question" or qualifier_str == "board":
    boost = TypeBoost(getTypeCode(qualifier_str), multiplier)
  else:
    boost = ItemBoost(qualifier_str, multiplier)
  return boost
def addToCollection(user_list_dict, topic_list_dict, question_list_dict, board_list_dict, item):
  curr_dict = None
  if item.isUser() == True:
    curr_dict = user_list_dict
  elif item.isTopic() == True:
    curr_dict = topic_list_dict
  elif item.isQuestion() == True:
    curr_dict = question_list_dict
  elif item.isBoard() == True:
    curr_dict = board_list_dict
  key = item.getIDString()
  curr_dict[key] = item
def removeFromCollection(user_list_dict, topic_list_dict, question_list_dict, board_list_dict, item):
  curr_dict = None
  if item.isUser() == True:
    curr_dict = user_list_dict
  elif item.isTopic() == True:
    curr_dict = topic_list_dict
  elif item.isQuestion() == True:
    curr_dict = question_list_dict
  elif item.isBoard() == True:
    curr_dict = board_list_dict
  key = item.getIDString()
  curr_dict.pop(key)
trie = Trie()
commands = []
from collections import defaultdict
user_list_dict = {}
topic_list_dict = {}
question_list_dict = {}
board_list_dict = {}
word_count_dict = defaultdict(int)
id_to_item_dict = {}
id_to_word_list_dict = defaultdict(list)
word_to_id_to_count_dict_dict = defaultdict(lambda: defaultdict(int))
item_count = 0
import sys
import string
stream = sys.stdin
line = stream.readline()
line = line.rstrip("\n")
args = line.split()
args = [string.atol(x) for x in args]
N = int(args[0])
for i in xrange(N):
  line = stream.readline()
  line = line.rstrip("\n")
  args = line.split()
  command_str = args[0]
  command = None
  if command_str == "ADD":
    type_str = args[1]
    type_value = getTypeCode(type_str)
    id_str = args[2]
    score = float(args[3])
    data_components = args[4 : ]
    data_string = string.join(data_components, " ")
    command = AddCommand(type_value, id_str, score, data_string, item_count + 1)
    item_count = item_count + 1
  elif command_str == "DEL":
    id_str = args[1]
    command = DelCommand(id_str)
  elif command_str == "QUERY":
    num_results = int(args[1])
    query_components = args[2 : ]
    query_string = string.join(query_components, " ")
    command = QueryCommand(num_results, query_string)
  elif command_str == "WQUERY":
    num_results = int(args[1])
    num_boosts = int(args[2])
    boost_components = args[3 : 3 + num_boosts]
    boosts = []
    for boost_component in boost_components:
      next_components = boost_component.split(":")
      qualifier_str = next_components[0]
      multiplier_value = float(next_components[1])
      boost = makeBoostGivenQualifier(qualifier_str, multiplier_value)
      boosts.append(boost)
    query_components = args[3 + num_boosts : ]
    query_string = string.join(query_components, " ")
    command = WQueryCommand(num_results, boosts, query_string)
  commands.append(command)
for command in commands:
  command.handle(trie, user_list_dict, topic_list_dict, question_list_dict, board_list_dict, word_count_dict, id_to_item_dict, id_to_word_list_dict, word_to_id_to_count_dict_dict)
