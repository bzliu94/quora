# 2015-11-30

# inspired by anand krishnamoorthi

class Vertex:
  def __init__(self, row, col, path_end, base_num_connections, non_base_num_connections):
    self.path_end = None
    self.base_num_connections = base_num_connections
    self.non_base_num_connections = non_base_num_connections
    self.row = row
    self.col = col
  def getNumConnections(self):
    return self.getBaseNumConnections() + self.getNonBaseNumConnections()
  def setNumConnections(self, val):
    base_num_connections = self.getBaseNumConnections()
    non_base_num_connections = val - base_num_connections
    self.setNonBaseNumConnections(non_base_num_connections)
  def getNonBaseNumConnections(self):
    return self.non_base_num_connections
  def setNonBaseNumConnections(self, val):
    self.non_base_num_connections = val
  def getBaseNumConnections(self):
    return self.base_num_connections
  def setBaseNumConnections(self, val):
    self.base_num_connections = val
  def toLocationString(self):
    return str((self.row, self.col))
  def toString(self):
    node1 = self
    node2 = self.getPathEnd()
    node_str1 = node1.toLocationString()
    node_str2 = node2.toLocationString()
    result = "(" + node_str1 + ", " + node_str2 + ")"
    return result
  def getPathEnd(self):
    return self.path_end
  def setPathEnd(self, path_end):
    self.path_end = path_end
class Connection:
  def __init__(self, vertex_a, vertex_b):
    room = vertex_a
    neighbor = vertex_b
    connected = False
    num_connections1 = room.getNumConnections()
    num_connections2 = neighbor.getNumConnections()
    room_partner = None
    neighbor_partner = None
    if num_connections1 != 2 and num_connections2 != 2:
      if room != neighbor.getPathEnd():
        room_partner = room.getPathEnd()
        neighbor_partner = neighbor.getPathEnd()
        assert(room_partner.getPathEnd() == room)
        assert(neighbor_partner.getPathEnd() == neighbor)
        connected = True
        room_partner.setPathEnd(neighbor_partner)
        neighbor_partner.setPathEnd(room_partner)
        room.setNumConnections(room.getNumConnections() + 1)
        neighbor.setNumConnections(neighbor.getNumConnections() + 1)
    self.connected = connected
    self.room = room
    self.neighbor = neighbor
    self.room_partner = room_partner
    self.neighbor_partner = neighbor_partner
  def undoConnection(self):
    connected = self.connected
    room = self.room
    neighbor = self.neighbor
    room_partner = self.room_partner
    neighbor_partner = self.neighbor_partner
    if connected == True:
      room_partner.setPathEnd(room)
      neighbor_partner.setPathEnd(neighbor)
      room.setNumConnections(room.getNumConnections() - 1)
      neighbor.setNumConnections(neighbor.getNumConnections() - 1)
  def successfullyConnected(self):
    return self.connected
class SolutionCounter:
  def __init__(self, count = 0):
    self.count = count
  def getCount(self):
    return self.count
  def setCount(self, count):
    self.count = count
  def increment(self):
    self.count += 1
def solve(grid, row, col, counter):
  H = len(grid) - 1
  W = len(grid[0]) - 1
  if col == W:
    col = 0
    row += 1
    if row == H:
      counter.increment()
      return
  vertex = grid[row][col]
  vertex_right = grid[row][col + 1]
  vertex_down = grid[row + 1][col]
  num_connections = vertex.getNumConnections()
  if num_connections == 2:
    solve(grid, row, col + 1, counter)
    return
  elif num_connections == 0:
    c1 = Connection(vertex, vertex_right)
    c2 = Connection(vertex, vertex_down)
    if c1.successfullyConnected() and c2.successfullyConnected():
      solve(grid, row, col + 1, counter)
    else:
      pass
    c2.undoConnection()
    c1.undoConnection()
    return
  elif num_connections == 1:
    c1 = Connection(vertex, vertex_right)
    if c1.successfullyConnected() == True:
      solve(grid, row, col + 1, counter)
    c1.undoConnection()
    c2 = Connection(vertex, vertex_down)
    if c2.successfullyConnected() == True:
      solve(grid, row, col + 1, counter)
    c2.undoConnection()
def drawGrid(grid, W, H):
  str_grid = []
  for i in xrange(H):
    row = grid[i]
    str_row = []
    for j in xrange(W):
      vertex = row[j]
      chain = vertex.getChain()
      vertex_right = grid[i][j + 1]
      vertex_down = grid[i + 1][j]
      vertex_str = vertex.toString()
      str_row.append(vertex_str)
    str_grid.append(str_row)
  for row in str_grid:
    print row
import sys
import string
stream = sys.stdin
# stream = open("tests/input01.txt")
line = stream.readline()
line = line.rstrip("\n")
args = line.split()
args = [string.atol(x) for x in args]
W = int(args[0])
H = int(args[1])
rows = []
for i in xrange(H):
  line = stream.readline()
  line = line.rstrip("\n")
  args = line.split()
  row = [string.atoi(x) for x in args]
  rows.append(row)
grid = []
for i in xrange(H + 1):
  vertex_row = []
  for j in xrange(W + 1):
    kind = 1
    base_num_connections = 0
    if (i < H and j < W):
      kind = rows[i][j]
    if kind == 0:
      base_num_connections = 0
    elif kind == 1:
      base_num_connections = 2
    elif kind == 2:
      base_num_connections = 1
    elif kind == 3:
      base_num_connections = 1
    vertex = Vertex(i, j, None, base_num_connections, 0)
    vertex.setPathEnd(vertex)
    vertex_row.append(vertex)
  grid.append(vertex_row)
counter = SolutionCounter()
solve(grid, 0, 0, counter)
num_solutions = counter.getCount()
print num_solutions
