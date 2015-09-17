# 2015-09-16

from __future__ import print_function
import math
def getSquaredDistance(vector1, vector2):
  x1, y1 = vector1
  x2, y2 = vector2
  x_difference = x2 - x1
  y_difference = y2 - y1
  result = x_difference * x_difference + y_difference * y_difference
  return result
def pointIsInsideCircle(r, x, y):
  is_inside = (x * x + y * y) <= r * r
  return is_inside
# looking for a left side of boundary
# assume r_list is sorted to have radii in non-decreasing order from left to right
# tend to have non-inside towards left
# note: (high - 1) >= r >= -1
def binarySearch(r_list, low, high, x, y):
  if (low > high):
    return low - 1
  else:
    mid = int(math.floor((low + high) / 2.0))
    radius = r_list[mid]
    is_inside = pointIsInsideCircle(radius, x, y)
    if is_inside == False:
      # go right; go in direction of INSIDE
      return binarySearch(r_list, mid + 1, high, x, y)
    else:
      # go left; go in direction of OUTSIDE
      return binarySearch(r_list, low, mid - 1, x, y)
# (x2, y2) must be at least as far from origin as (x1, y1)
def countingRangeQuery(sorted_r_list, x1, y1, x2, y2):
  low = 0
  high = len(sorted_r_list) - 1
  value1 = binarySearch(sorted_r_list, low, high, x1, y1)
  value2 = binarySearch(sorted_r_list, low, high, x2, y2)
  # look for right side of boundary
  next_value1 = value1 + 1
  # look for left side of boundary
  next_value2 = value2
  result = next_value2 - next_value1 + 1
  return result
def main():
  import sys
  import string
  stream = sys.stdin
  # stream = open("tests/official/input29.txt")
  line = stream.readline()
  line = line.rstrip("\n")
  args = line.split(" ")
  args = [string.atol(x) for x in args]
  N = int(args[0])
  line = stream.readline()
  line = line.rstrip("\n")
  args = line.split(" ")
  args = [string.atol(x) for x in args]
  radii = [int(x) for x in args]
  sorted_radii = sorted(radii)
  line = stream.readline()
  line = line.rstrip("\n")
  args = line.split(" ")
  args = [string.atol(x) for x in args]
  M = int(args[0])
  endpoint_pairs = []
  for i in range(M):
    line = stream.readline()
    line = line.rstrip("\n")
    args = line.split(" ")
    args = [string.atol(x) for x in args]
    x1 = int(args[0])
    y1 = int(args[1])
    x2 = int(args[2])
    y2 = int(args[3])
    endpoint1 = (x1, y1)
    endpoint2 = (x2, y2)
    endpoint_pair = (endpoint1, endpoint2)
    endpoint_pairs.append(endpoint_pair)
  num_qs = 0
  for endpoint_pair in endpoint_pairs:
    endpoint1, endpoint2 = endpoint_pair
    distance1 = getSquaredDistance((0, 0), endpoint1)
    distance2 = getSquaredDistance((0, 0), endpoint2)
    candidate_distances = [distance1, distance2]
    min_distance = min(candidate_distances)
    max_distance = max(candidate_distances)
    closer_endpoint = None
    farther_endpoint = None
    if (min_distance == distance1):
      closer_endpoint = endpoint1
      farther_endpoint = endpoint2
    else:
      closer_endpoint = endpoint2
      farther_endpoint = endpoint1
    x1, y1 = closer_endpoint
    x2, y2 = farther_endpoint
    curr_num_qs = countingRangeQuery(sorted_radii, x1, y1, x2, y2)
    num_qs = num_qs + curr_num_qs
  print(num_qs, end = '')
if __name__ == "__main__":
  main()
