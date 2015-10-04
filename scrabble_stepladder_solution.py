# 2015-10-03

# uses branch and bound and memoizing

# uses score group sets

# inspired by marcello la rocca

import heapq
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
import sys
import string
import math
from collections import defaultdict
letter_scores = {'A' : 1, 'E' : 1, 'I' : 1, 'L' : 1, 'N' : 1, 
                  'O' : 1, 'R' : 1, 'S' : 1, 'T' : 1, 'U' : 1, 
                  'D' : 2, 'G' : 2, 'B' : 3, 'C' : 3, 'M' : 3, 
                  'P' : 3, 'F' : 4, 'H' : 4, 'V' : 4, 'W' : 4, 
                  'Y' : 4, 'K' : 5, 'J' : 8, 'X' : 8, 'Q' : 10, 
                  'Z' : 10}
score_group_set_table = defaultdict(lambda: None)
scores = {}
truncated_sum_of_lower_scores_table = defaultdict(lambda: 0)
word_to_index_dict = defaultdict(lambda: None)
def getNeighborList(word):
  return neighbors[word]
def getTruncatedSumOfLowerScores(word, neighbor_list, dictionary):
  if word in truncated_sum_of_lower_scores_table:
    return truncated_sum_of_lower_scores_table[word]
  else:
    score_group_set = getScoreGroupSet(word, neighbor_list, dictionary)
    truncated_sum = score_group_set.getTruncatedSumOfLowerScores(score_group_set)
    truncated_sum_of_lower_scores_table[word] = truncated_sum
    return truncated_sum
def getScoreGroupSet(word, neighbor_list, dictionary):
  if word in score_group_set_table:
    return score_group_set_table[word]
  else:
    adjacency_list = neighbor_list
    word_score = scores[word]
    score_group_set = None
    filtered_adjacency_list = [x for x in adjacency_list if scores[x] < word_score]
    if len(filtered_adjacency_list) == 0:
      score_group_set = ScoreGroupSet(word, word_score)
    else: 
      score_group_sets = [getScoreGroupSet(x, getNeighborList(x), dictionary) for x in filtered_adjacency_list]
      next_score_group_sets = []
      for score_group_set in score_group_sets:
        next_word = score_group_set.getWord()
        next_score_group_set = score_group_set.copy()
        next_word_score = scores[next_word]
        next_score_group_set.addScoreGroup(next_word_score)
        next_score_group_sets.append(next_score_group_set)
      if len(next_score_group_sets) == 1:
        chosen_score_group_set = next_score_group_sets[0]
        score_group_set = chosen_score_group_set.copy()
        score_group_set.setWord(word)
        score_group_set.setWordScore(word_score)
      else:
        score_group_set = reduce(lambda x, y: x.doOr(word, word_score, y), next_score_group_sets)
    score_group_set_table[word] = score_group_set
    return score_group_set
class BitSet:
  def __init__(self, n = 128):
    self.n = n
    num_groups = int(math.ceil(n / (1.0 * 32)))
    self.num_groups = num_groups
    groups = [0] * num_groups
    self.groups = groups
  def _getGroupIndex(self, i):
    group_i = int(math.floor(i / 32))
    return group_i
  def _getRemainderIndex(self, i):
    num_groups = self.num_groups
    remainder_index = i % 32
    return remainder_index
  def setBit(self, i, value):
    group_i = self._getGroupIndex(i)
    remainder_index = self._getRemainderIndex(i)
    if value == 0:
      (self.groups)[group_i] = (self.groups)[group_i] & (1 << remainder_index)
    elif value == 1:
      (self.groups)[group_i] = (self.groups)[group_i] | (1 << remainder_index)
  def getBit(self, i):
    group_i = self._getGroupIndex(i)
    remainder_index = self._getRemainderIndex(i)
    pred_value = ((self.groups)[group_i] >> remainder_index) != 0
    value = 0 if pred_value == False else 1
    return value
  def getNumOneBits(self):
    groups = self.groups
    counts = [bin(x).count("1") for x in groups]
    count = sum(counts)
    return count
  def _getNumOneBits(self, group_i):
    v = (self.groups)[group_i]
    c = 0
    for i in xrange(32):
      if v == 0:
        break
      v &= v - 1
      c += 1
    return c
  def doOr(self, bit_set):
    num_groups = len(self.groups)
    bit_set_a = self
    bit_set_b = bit_set
    result_bit_set = self.doOrHelper()
    for i in xrange(num_groups):
      group_a = (bit_set_a.groups)[i]
      group_b = (bit_set_b.groups)[i]
      result_group = group_a | group_b
      result_bit_set.groups[i] = result_group
    return result_bit_set
  def doOrHelper(self):
    return BitSet()
  def getNumBits(self):
    return self.n
  def toString(self):
    reversed_bits = []
    for i in xrange(len(self.groups)):
      group = (self.groups)[i]
      for j in xrange(32):
        value = None
        if group & (1 << j) == 0:
          value = 0
        else:
          value = 1
        reversed_bits.append(value)
    bits = reversed_bits[ : ]
    bits.reverse()
    bit_str_list = [str(x) for x in bits]
    result_str = "".join(bit_str_list)
    return result_str
class ScoreGroupSet(BitSet):
  def __init__(self, word, word_score, max_word_score = 51):
    BitSet.__init__(self, max_word_score + 1)
    self.word = word
    self.word_score = word_score
  def getWord(self):
    return self.word
  def getWordScore(self):
    return self.word_score
  def includesScoreGroup(self, n):
    return self.getBit(n)
  def getNumScoreGroupsIncluded(self):
    return self.getNumOneBits()
  def getMaxWordScore(self):
    return self.getNumBits()
  @staticmethod
  def getSumOfLowerIncludedScores(score_group_set):
    max_word_score = score_group_set.getMaxWordScore()
    num_bits = max_word_score
    result_sum = 0
    for i in xrange(1, num_bits + 1):
      bit = score_group_set.getBit(i)
      value = bit * i
      result_sum += value
    return result_sum
  @staticmethod
  def getTruncatedSumOfLowerScores(score_group_set):
    num_ones = score_group_set.getNumOneBits()
    max_num_ones = score_group_set.getWordScore() - 1
    num_zeroes = max_num_ones - num_ones
    sum_a = max_num_ones * (max_num_ones + 1) / 2
    sum_b = num_zeroes * (num_zeroes + 1) / 2
    result_sum = sum_a - sum_b
    return result_sum
  def addScoreGroup(self, score):
    self.setBit(score, 1)
  def getWordScore(self):
    return self.word_score
  def doOr(self, word, word_score, score_group_set):
    num_groups = len(self.groups)
    set_a = self
    set_b = score_group_set
    result_set = self.doOrHelper(word, word_score)
    for i in xrange(num_groups):
      group_a = (set_a.groups)[i]
      group_b = (set_b.groups)[i]
      result_group = group_a | group_b
      result_set.groups[i] = result_group
    return result_set
  def doOrHelper(self, word, word_score):
    result = ScoreGroupSet(word, word_score)
    return result
  def copy(self):
    word = self.getWord()
    word_score = self.getWordScore()
    max_word_score = self.getMaxWordScore()
    score_group_set = ScoreGroupSet(word, word_score, max_word_score)
    groups = self.groups
    score_group_set.groups = groups[ : ]
    return score_group_set
  def setWord(self, word):
    self.word = word
  def setWordScore(self, word_score):
    self.word_score = word_score
def word_score(word):
  word = string.upper(word)
  score = 0
  for i in xrange(len(word)):
      score += letter_scores[word[i]]
  return score
def are_neighbors(w1, w2):
  num_diff = 0
  for i in xrange(len(w1)):
    if w1[i] != w2[i]:
      num_diff += 1
      if num_diff > 1:
        return False
  if num_diff == 1:
    return True
  else:
    return False
def determineNeighborLists(words):
  neighbors = defaultdict(list)
  for i in xrange(len(words)):
    word = words[i]
    indices = xrange(i + 1, len(words))
    for j in indices:
      word1 = word
      word2 = words[j]
      if are_neighbors(word1, word2):
        neighbors[word1].append(word2)
        neighbors[word2].append(word1)
  return neighbors
class StepladderProblem:
  def __init__(self, words, top_word, bottom_word, score):
    self.word_set = set(words)
    self.top_word = top_word
    self.bottom_word = bottom_word
    self.score = score
    self.left_words = words
    self.right_words = []
  def hasWord(self, word):
    return word in self.word_set
  def getWords(self):
    return list(self.words)
  def getTopWord(self):
    return self.top_word
  def getBottomWord(self):
    return self.bottom_word
  def getScore(self):
    return self.score
  def setScore(self, score):
    self.score = score
  def addTopWord(self, word):
    self.top_word = word
    score = scores[word]
    prev_total_score = self.getScore()
    next_score = prev_total_score + score
    self.setScore(next_score)
    self.word_set.add(word)
    self.left_words.insert(0, word)
  def addBottomWord(self, word):
    self.bottom_word = word
    score = scores[word]
    prev_total_score = self.getScore()
    next_score = prev_total_score + score
    self.setScore(next_score)
    self.word_set.add(word)
    self.right_words.append(word)
  def setTopWord(self, word):
    self.top_word = word
  def setBottomWord(self, word):
    self.bottom_word = word
  def addWord(self, word):
    (self.words).append(word)
  def getPriority(self):
    return -1 * self.getScore()
  def getNumWords(self):
    return len(self.words)
  def haveNoWords(self):
    return self.getNumWords() == 0
  def copy(self):
    word_set = self.word_set.copy()
    top_word = self.getTopWord()
    bottom_word = self.getBottomWord()
    score = self.getScore()
    problem = StepladderProblem([], top_word, bottom_word, score)
    problem.word_set = word_set
    left_words = self.left_words[ : ]
    right_words = self.right_words[ : ]
    problem.left_words = left_words
    problem.right_words = right_words
    return problem
  def toString(self):
    left_words = self.left_words
    right_words = self.right_words
    top_word = self.getTopWord()
    bottom_word = self.getBottomWord()
    score = self.getScore()
    result_str = str(left_words) + " " + str(right_words) + " " + top_word + " " + bottom_word + " " + str(score)
    return result_str
def solve(K, words, scores, dictionary):
  S = PriorityQueue()
  best_so_far = float("-inf")
  best_problem = None
  for w in words:
    P0 = StepladderProblem([], w, w, -1 * scores[w])
    S.push(P0, P0.getPriority())
    curr_score = scores[w]
    if curr_score > best_so_far:
      best_so_far = curr_score
      best_problem = P0
    while S.getSize() != 0:
      P = S.pop()
      bottom = P.getBottomWord()
      top = P.getTopWord()
      P.addBottomWord(bottom)
      P.addTopWord(top)
      score = P.getScore()
      bottom_neighbors = getNeighborList(bottom)
      next_bottom_neighbors = [x for x in bottom_neighbors if P.hasWord(x) == False and scores[x] < scores[bottom]]
      top_neighbors = getNeighborList(top)
      next_top_neighbors = [x for x in top_neighbors if P.hasWord(x) == False and scores[x] < scores[top]]
      for bottom_word in next_bottom_neighbors:
        for top_word in next_top_neighbors:
          if bottom_word == top_word:
            continue
          top_word_score = scores[top_word]
          bottom_word_score = scores[bottom_word]
          top_truncated_sum = getTruncatedSumOfLowerScores(top_word, getNeighborList(top_word), dictionary)
          bottom_truncated_sum = getTruncatedSumOfLowerScores(bottom_word, getNeighborList(bottom_word), dictionary)
          P_i = P.copy()
          P_i.setBottomWord(bottom_word)
          P_i.setTopWord(top_word)
          curr_score = score + bottom_word_score + top_word_score
          if curr_score > best_so_far:
            best_so_far = curr_score
            best_problem = P_i
          upper_bound = score + bottom_truncated_sum + bottom_word_score + top_truncated_sum + top_word_score
          if upper_bound >= best_so_far:
            S.push(P_i, P_i.getPriority() - bottom_word_score - top_word_score)
  return (best_so_far, best_problem)
stream = sys.stdin
line = stream.readline()
line = line.rstrip("\n")
args = line.split(" ")
args = [string.atol(x) for x in args]
K = int(args[0])
line = stream.readline()
line = line.rstrip("\n")
args = line.split(" ")
args = [string.atol(x) for x in args]
N = int(args[0])
words = []
for i in xrange(N):
  line = stream.readline()
  line = line.rstrip("\n")
  args = line.split(" ")
  w = args[0]
  if len(w) == K:     
    words.append(w)
    scores[w] = word_score(w)
dictionary = []
neighbors = determineNeighborLists(words)
best_score, best_problem = solve(K, words, scores, dictionary)
score = None
if best_problem == None:
  score = 0
else:
  score = best_score
print score
