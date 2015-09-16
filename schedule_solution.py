# 2015-09-15

# optimal ordering is s.t. we consider items with best (chance of failure) / time ratio

# using this information, we find ordering of items

# using this permutation, find expected value of time to a conclusion

def getExpectedTime(pairs):
  if len(pairs) == 0:
    # consider that all tests succeeded
    return None
  else:
    return getExpectedTimeHelper(pairs, [0], [1])
def getExpectedTimeHelper(pairs, curr_time_values, curr_p_success_values):
  if len(pairs) == 0:
    return sum(curr_time_values) * reduce(lambda x, y: x * y, curr_p_success_values)
  else:
    curr_pair = pairs[0]
    t, p_success, id_value = curr_pair
    p_failure = 1 - p_success
    # consider that current test succeeds
    succeed_time_contribution = getExpectedTimeHelper(pairs[1 : ], curr_time_values + [t], curr_p_success_values + [p_success])
    # consider that current test fails
    fail_time_contribution = sum(curr_time_values + [t]) * reduce(lambda x, y: x * y, curr_p_success_values + [p_failure])
    return succeed_time_contribution + fail_time_contribution
import sys
import string
stream = sys.stdin
line = stream.readline()
line = line.rstrip("\n")
args = line.split(" ")
args = [string.atol(x) for x in args]
n = int(args[0])
pairs = []
for i in range(1, n + 1):
  stream = sys.stdin
  line = stream.readline()
  line = line.rstrip("\n")
  args = line.split(" ")
  id_value = i
  t = int(args[0])
  p_success = float(args[1])
  pair = (t, p_success, id_value)
  pairs.append(pair)
# high first component is desirable
# high second component is desirable
pairs.sort(key = lambda x: ((1 - x[1])/x[0], (1 - x[1])), reverse = True)
# order of pairs describes permutation for best ordering
print getExpectedTime(pairs)
