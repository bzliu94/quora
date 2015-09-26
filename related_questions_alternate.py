# 2015-09-26

# based on recursive version by adel ali

# uses dynamic programming

# takes O(n) time

import sys
from collections import defaultdict
N = 10 ** 5 + 1
v = []
adj = []
for i in xrange(N):
  adj.append([])
dp = {}
done = {}
for i in xrange(N + 1):
  dp[i] = {}
for i in xrange(N + 1):
  done[i] = {}
memo = [0.0] * N
class FrameContainer:
  def __init__(self, tot, cur, par, parent_container = None):
    self.parent_container = parent_container
    self.tot = tot
    self.cur = cur
    self.par = par
    self.score = 0
    self.bypass_total = False
  def getParentContainer(self):
    return self.parent_container
  def getTotal(self):
    return self.tot
  def setTotal(self, tot):
    self.tot = tot
  def getCurrentNode(self):
    return self.cur
  def getPartnerNode(self):
    return self.par
  def haveParentContainer(self):
    return self.parent_container != None
  def getTValue(self):
    cur = self.getCurrentNode()
    T_value = v[cur]
    return T_value
  def getScore(self):
    return self.score
  def setScore(self, score):
    self.score = score
  def setBypassTotal(self, bypass_total):
    self.bypass_total = bypass_total
  def getBypassTotal(self):
    return self.bypass_total
def iterativeSolve(cur):
  par = 0
  container = FrameContainer(0, cur, par, None)
  stack = [container]
  visited = defaultdict(lambda: False)
  result = iterativeSolveHelper(cur, par, stack, visited)
  return result
def previsit(container):
  cur = container.getCurrentNode()
  par = container.getPartnerNode()
  parent_container = container.getParentContainer()
  have_parent_container = container.haveParentContainer()
  if have_parent_container == True:
    if (cur in dp) and (par in dp[cur]):
      value = dp[cur][par]
      container.setScore(value)
      container.setBypassTotal(True)
      return []
  tot = 0
  next_containers = []
  if (cur in done) and len(done[cur]) == len(adj[cur]):
    if (par != 0):
      tot = memo[cur] - done[cur][par]
    else:
      tot = memo[cur]
  else:
    for i in xrange(len(adj[cur])):
      to = adj[cur][i]
      if (to == par):
        continue
      next_container = FrameContainer(0, to, cur, container)
      next_containers.append(next_container)
  container.setTotal(tot)
  return next_containers
def postvisit(container):
  cur = container.getCurrentNode()
  par = container.getPartnerNode()
  parent_container = container.getParentContainer()
  have_parent_container = container.haveParentContainer()
  T_value = container.getTValue()
  tot = container.getTotal()
  score = None
  if container.getBypassTotal() == True:
    score = container.getScore()
  else:
    if par == 0:
      if len(adj[cur]) != 0:
        tot /= len(adj[cur])
    else:
      if len(adj[cur]) - 1 != 0:
        tot /= len(adj[cur]) - 1
    score = T_value + tot
  container.setScore(score)
  if have_parent_container == True:
    parent_container.setTotal(parent_container.getTotal() + score)
    if (cur in done[par]) == False:
      done[par][cur] = score
      memo[par] += score
    if (par in dp[cur]) == False:
      dp[cur][par] = score
  return score
def iterativeSolveHelper(cur, par, stack, visited):
  result = None
  while len(stack) != 0:
    x = stack.pop(len(stack) - 1)
    if visited[x] == False:
      stack.append(x)
      containers = previsit(x)
      visited[x] = True
      for container in containers:
        stack.append(container)
    else:
      result = postvisit(x)
  return result
import sys
import string
stream = sys.stdin
# stream = open("tests/official/input19.txt")
# stream = open("tests/official/input00.txt")
# stream = open("tests/official/input07.txt")
line = stream.readline()
line = line.rstrip("\n")
args = line.split(" ")
args = [string.atol(x) for x in args]
n = int(args[0])
v.append(0)
line = stream.readline()
line = line.rstrip("\n")
args = line.split(" ")
args = [string.atol(x) for x in args]
T_list = [float(x) for x in args]
for T in T_list:
  v.append(T)
for i in xrange(1, n):
  line = stream.readline()
  line = line.rstrip("\n")
  args = line.split(" ")
  args = [string.atol(x) for x in args]
  q_list = [int(x) for x in args]
  q1 = q_list[0]
  q2 = q_list[1]
  adj[q1].append(q2)
  adj[q2].append(q1)
best = 10 ** 11 + 1
ans = -1
for i in xrange(1, n + 1):
  cur = iterativeSolve(i)
  if cur < best:
    best = cur
    ans = i
print ans
