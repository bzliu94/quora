# 2015-09-15

# window is made of sequences

# le-sequence is non-decreasing from left to right

# ge-sequence is non-increasing from right to left

# we assume K >= 1

# find first window information in O(K) time

# move window to right by one in O(1) time

# move window to right a number of times in O(N - K)

from collections import deque
def retrieveUnbrokenLESequences(upvote_counts):
  next_upvote_counts = deque(upvote_counts)
  if len(upvote_counts) == 0:
    return []
  else:
    curr_count = next_upvote_counts.popleft()
    curr_LE_sequence = LESequence([curr_count])
    sequence_list = [curr_LE_sequence]
    remaining_counts = next_upvote_counts
    result = retrieveUnbrokenLESequencesHelper(remaining_counts, curr_LE_sequence, sequence_list)
    next_result = list(result)
    return next_result
def retrieveUnbrokenLESequencesHelper(count_values_deque, prev_LE_sequence, sequence_list):
  while True:
    if len(count_values_deque) == 0:
      return sequence_list
    else:
      curr_count = count_values_deque.popleft()
      prev_count = prev_LE_sequence.getRightmostCount()
      next_count_values_deque = count_values_deque
      if prev_count <= curr_count:
        prev_LE_sequence.addCountToRight(curr_count)
        count_values_deque = next_count_values_deque; prev_LE_sequence = prev_LE_sequence; sequence_list = sequence_list
      else:
        LE_sequence = LESequence([curr_count])
        sequence_list.append(LE_sequence)
        count_values_deque = next_count_values_deque; prev_LE_sequence = LE_sequence; sequence_list = sequence_list
def retrieveUnbrokenGESequences(upvote_counts):
  next_upvote_counts = deque(upvote_counts)
  if len(upvote_counts) == 0:
    return []
  else:
    curr_count = next_upvote_counts.popleft()
    curr_GE_sequence = GESequence([curr_count])
    sequence_list = [curr_GE_sequence]
    remaining_counts = next_upvote_counts
    return retrieveUnbrokenGESequencesHelper(remaining_counts, curr_GE_sequence, sequence_list)
def retrieveUnbrokenGESequencesHelper(count_values_deque, prev_GE_sequence, sequence_list):
  while True:
    if len(count_values_deque) == 0:
      return sequence_list
    else:
      curr_count = count_values_deque.popleft()
      prev_count = prev_GE_sequence.getRightmostCount()
      next_count_values_deque = count_values_deque
      if prev_count >= curr_count:
        prev_GE_sequence.addCountToRight(curr_count)
        count_values_deque = next_count_values_deque; prev_GE_sequence = prev_GE_sequence; sequence_list = sequence_list
      else:
        GE_sequence = GESequence([curr_count])
        sequence_list.append(GE_sequence)
        count_values_deque = next_count_values_deque; prev_GE_sequence = GE_sequence; sequence_list = sequence_list
class Window:
  def __init__(self, sequences):
    self.sequences = sequences
    distinct_subsequence_count_contributions = [self.getUnbrokenSequenceSizeToNumDistinctSequences(x.getSize()) for x in sequences]
    self.distinct_subsequence_count = sum(distinct_subsequence_count_contributions)
  def getUnbrokenSequenceSizeToNumDistinctSequences(self, size):
    return None
  def getOperator(self):
    return lambda x, y: x == y
  def createSequence(self):
    pass
  def getSequences(self):
    return self.sequences
  def getNumSequences(self):
    return len(self.getSequences())
  def getLeftmostSequence(self):
    sequences = self.getSequences()
    leftmost_sequence = sequences[0]
    return leftmost_sequence
  def getRightmostSequence(self):
    sequences = self.getSequences()
    rightmost_sequence = sequences[self.getNumSequences() - 1]
    return rightmost_sequence
  def haveSequences(self):
    return len(self.getSequences()) != 0
  def setSequences(self, sequences):
    self.sequences = sequences
  def addSequenceToRight(self, sequence):
    (self.getSequences()).append(sequence)
  def removeSequenceAtLeft(self):
    (self.getSequences()).pop(0)
  def toString(self):
    return str(self.getCountValues())
  def moveToRightByOne(self, next_count):
    if self.haveSequences() == False:
      sequence = self.createSequence([next_count])
      sequences = [sequence]
      self.setSequences(sequences)
      prev_total_contribution = 0
      next_total_contribution = prev_total_contribution + 0 + 1
      self.setNumDistinctSubsequences(next_total_contribution)
      return
    leftmost_sequence = self.getLeftmostSequence()
    rightmost_sequence = self.getRightmostSequence()
    prev_right_count = rightmost_sequence.getRightmostCount()
    prev_left_count = leftmost_sequence.getLeftmostCount()
    prev_leftmost_sequence_size = leftmost_sequence.getSize()
    prev_left_distinct_subsequence_contribution = self.getUnbrokenSequenceSizeToNumDistinctSequences(prev_leftmost_sequence_size)
    prev_total_contribution = self.getNumDistinctSubsequences()
    leftmost_sequence.removeCountAtLeft()
    if leftmost_sequence.getSize() == 0:
      self.removeSequenceAtLeft()
    next_leftmost_sequence_size = prev_leftmost_sequence_size - 1
    next_left_distinct_subsequence_contribution = self.getUnbrokenSequenceSizeToNumDistinctSequences(next_leftmost_sequence_size)
    left_sequence_change_contribution_change = next_left_distinct_subsequence_contribution -      prev_left_distinct_subsequence_contribution
    prev_rightmost_sequence_size = None
    prev_rightmost_sequence_size = None
    prev_rightmost_sequence_size = rightmost_sequence.getSize() if (self.getOperator()(prev_right_count, next_count)) else 0
    prev_right_distinct_subsequence_contribution = self.getUnbrokenSequenceSizeToNumDistinctSequences(prev_rightmost_sequence_size)
    next_rightmost_sequence_size = (rightmost_sequence.getSize() + 1) if (self.getOperator()(prev_right_count, next_count)) else 1
    if self.getOperator()(prev_right_count, next_count):
      rightmost_sequence.addCountToRight(next_count)
    else:
      sequence_to_add = self.createSequence([next_count])
      self.addSequenceToRight(sequence_to_add)
    next_right_distinct_subsequence_contribution = self.getUnbrokenSequenceSizeToNumDistinctSequences(next_rightmost_sequence_size)
    right_sequence_change_contribution_change = next_right_distinct_subsequence_contribution -      prev_right_distinct_subsequence_contribution
    next_total_contribution = prev_total_contribution + left_sequence_change_contribution_change + right_sequence_change_contribution_change
    self.setNumDistinctSubsequences(next_total_contribution)
  def setNumDistinctSubsequences(self, value):
    self.distinct_subsequence_count = value
  def getNumDistinctSubsequences(self):
    return self.distinct_subsequence_count
class LEWindow(Window):
  def __init__(self, sequences):
    Window.__init__(self, sequences)
  def getOperator(self):
    return lambda x, y: x <= y
  def createSequence(self, count_values):
    return LESequence(count_values)
  def getUnbrokenSequenceSizeToNumDistinctSequences(self, size):
    return unbrokenLESequenceSizeToNumDistinctLESequences(size)
class GEWindow(Window):
  def __init__(self, sequences):
    Window.__init__(self, sequences)
  def getOperator(self):
    return lambda x, y: x >= y
  def createSequence(self, count_values):
    return GESequence(count_values)
  def getUnbrokenSequenceSizeToNumDistinctSequences(self, size):
    return unbrokenGESequenceSizeToNumDistinctGESequences(size)
class Sequence:
  def __init__(self, count_values):
    self.count_values = count_values
  def getCountValues(self):
    return self.count_values
  def getSize(self):
    return len(self.getCountValues())
  def getLeftmostCount(self):
    count_values = self.getCountValues()
    leftmost_count_value = count_values[0]
    return leftmost_count_value
  def getRightmostCount(self):
    count_values = self.getCountValues()
    rightmost_count_value = count_values[self.getSize() - 1]
    return rightmost_count_value
  def addCountToRight(self, count):
    (self.getCountValues()).append(count)
  def removeCountAtLeft(self):
    (self.getCountValues()).pop(0)
  def toString(self):
    return str(self.getCountValues())
class LESequence(Sequence):
  def __init__(self, count_values):
    Sequence.__init__(self, count_values)
class GESequence(Sequence):
  def __init__(self, count_values):
    Sequence.__init__(self, count_values)
def unbrokenLESequenceSizeToNumDistinctLESequences(size):
  if size == 0:
    return 0
  else:
    return size * (size - 1) / 2
def unbrokenGESequenceSizeToNumDistinctGESequences(size):
  if size == 0:
    return 0
  else:
    return size * (size - 1) / 2
import sys
import string
stream = sys.stdin
line = stream.readline()
line = line.rstrip("\n")
args = line.split(" ")
args = [string.atol(x) for x in args]
N = int(args[0])
K = int(args[1])
line = stream.readline()
line = line.rstrip("\n")
args = line.split(" ")
upvote_counts = [long(x) for x in args if x != ""]
count_sequence = upvote_counts
curr_le_window = LEWindow(retrieveUnbrokenLESequences(count_sequence[0 : K]))
curr_ge_window = GEWindow(retrieveUnbrokenGESequences(count_sequence[0 : K]))
num_non_dec_sequences = curr_le_window.getNumDistinctSubsequences()
num_non_inc_sequences = curr_ge_window.getNumDistinctSubsequences()
print num_non_dec_sequences - num_non_inc_sequences
for i in range(N - K + 1 - 1):
  next_count = count_sequence[K + i]
  curr_le_window.moveToRightByOne(next_count)
  curr_ge_window.moveToRightByOne(next_count)
  num_non_dec_sequences = curr_le_window.getNumDistinctSubsequences()
  num_non_inc_sequences = curr_ge_window.getNumDistinctSubsequences()
  print num_non_dec_sequences - num_non_inc_sequences
