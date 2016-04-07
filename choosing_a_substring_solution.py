# 2016-04-07

# linear time, linear space

# for a given string, find the longest substring that contains at most 2 different characters

# example:
# 'cabbaadd' -> 'abbaa'

class Counter:
  def __init__(self):
    self.dict = {}
  def add(self, x):
    if x not in self.dict:
      self.dict[x] = 1
    else:
      self.dict[x] += 1
  def remove(self, x):
    if x not in self.dict:
      raise Exception()
    elif self.dict[x] == 1:
      self.dict.pop(x)
    else:
      self.dict[x] -= 1
  def getNumKeys(self):
    keys = self.dict.keys()
    num_keys = len(keys)
    return num_keys
class Best:
  def __init__(self):
    self.left = 0
    self.length = 0
  def setBest(self, left, length):
    prev_left = self.left
    prev_length = self.length
    prev_tuple = (prev_length, -1 * prev_left)
    curr_tuple = (length, -1 * left)
    best_tuple = max(prev_tuple, curr_tuple)
    best_left = -1 * best_tuple[1]
    best_length = best_tuple[0]
    self.left = best_left
    self.length = best_length
  def getBest(self):
    left = self.left
    length = self.length
    result = (left, length)
    return result
def getLongestSubstrWithAtMostTwoDistinctChars(given_str):
  curr_str = given_str
  chars = list(curr_str)
  num_chars = len(chars)
  # inclusive
  left = 0
  # exclusive
  right = 0
  counter = Counter()
  best = Best()
  while left <= num_chars - 1:
    # attempt to move right as far as possible
    while (right <= num_chars - 1):
      next_char = chars[right]
      counter.add(next_char)
      if counter.getNumKeys() > 2:
        # revert
        counter.remove(next_char)
        break
      else:
        best.setBest(left, right - left + 1)
      right += 1
    # attempt to move left
    remove_char = chars[left]
    counter.remove(remove_char)
    left += 1
  best_tuple = best.getBest()
  best_left, best_length = best_tuple
  result_chars = chars[best_left : best_left + best_length]
  result_str = "".join(result_chars)
  return result_str
result_str = getLongestSubstrWithAtMostTwoDistinctChars("cabbaadd")
print result_str
