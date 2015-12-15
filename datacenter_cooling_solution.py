# 2015-11-30

# takes O(2 ^ L * L ^ 2) time

# involves memoizing using a surface key

# inspired by anand krishnamoorthi

# algorithm comes from a paper by j. l. jacobsen

# uses a slightly different surface key;
# upon adding a horizontal cut-edge with a neighbor vertical cut-edge, 
# we immediately seal the cut-edges converging at the shared node and increment k, 
# rather than wait for a pass move later on that will increment k

# takes 2.6 seconds (under five) on a 2.6 ghz system for given 7 by 8 grid

import math
from collections import defaultdict
import random
class Grid:
  def __init__(self, W, H):
    self.W = W
    self.H = H
  def getWidth(self):
    return self.W
  def getHeight(self):
    return self.H
# id values are in [0, inf)
def idToLocation(id_value, eff_W, eff_H):
  t = id_value
  row = getRow(t, eff_W, eff_H)
  col = getCol(t, eff_W, eff_H)
  location = (row, col)
  return location
def getRow(t, W, H):
  result = int(math.floor(t / W))
  return result
def getCol(t, W, H):
  return t % W
def getTime(row, col, W, H):
  t = row * W + col
  return t
class FullGrid(Grid):
  def __init__(self, W, H):
    Grid.__init__(self, W, H)
    vertex_rows = []
    for i in xrange(H + 1):
      vertex_row = []
      for j in xrange(W + 1):
        vertex = None
        vertex_row.append(vertex)
      vertex_rows.append(vertex_row)
    self.vertex_rows = vertex_rows
    self.id_to_vertex_dict = {}
    self.location_to_incident_path_far_node_id = defaultdict(lambda: [])
  # add a vertex to the grid
  def addVertex(self, id_value, row1, col1, path_end_id_value, base_num_connections, non_base_num_connections):
    vertex = Vertex(id_value, row1, col1, path_end_id_value, base_num_connections, non_base_num_connections)
    (self.vertex_rows)[row1][col1] = vertex
    (self.id_to_vertex_dict)[id_value] = vertex
    location1 = (row1, col1)
    location2 = idToLocation(path_end_id_value, self.getWidth() + 1, self.getHeight() + 1)
    (self.location_to_incident_path_far_node_id)[location1].append(path_end_id_value)
    (self.location_to_incident_path_far_node_id)[location2].append(id_value)
    return vertex
  def getVertex(self, row, col):
    return (self.vertex_rows)[row][col]
  def getVertexUsingIDValue(self, id_value):
    return (self.id_to_vertex_dict)[id_value]
  def getVertexRow(self, row):
    return (self.vertex_rows)[row]
  def getPathEndNode(self, row, col):
    vertex = self.getVertex(row, col)
    path_end_id_value = vertex.getPathEndIDValue()
    path_end_node = self.getVertexUsingIDValue(path_end_id_value)
    return path_end_node
  # set partner of node at (row1, col1) to be node at (row2, col2)
  def setPathEnd(self, row1, col1, row2, col2):
    vertex1 = self.getVertex(row1, col1)
    vertex2 = self.getVertex(row2, col2)
    id_value1 = vertex1.getIDValue()
    id_value2 = vertex2.getIDValue()
    old_partner_id = vertex1.getPathEndIDValue()
    old_partner_location = idToLocation(old_partner_id, self.getWidth() + 1, self.getHeight() + 1)
    path_end_id_value = vertex2.getIDValue()
    vertex1.setPathEndIDValue(path_end_id_value)
    location1 = (row1, col1)
    location2 = (row2, col2)
    (self.location_to_incident_path_far_node_id)[old_partner_location].remove(id_value1)
    (self.location_to_incident_path_far_node_id)[location1].remove(old_partner_id)
    (self.location_to_incident_path_far_node_id)[location2].append(id_value1)
    (self.location_to_incident_path_far_node_id)[location1].append(id_value2)
  def setNumConnections(self, row, col, val):
    vertex = self.getVertex(row, col)
    vertex.setNumConnections(val)
  def getNumConnections(self, row, col):
    vertex = self.getVertex(row, col)
    result = vertex.getNumConnections()
    return result
  @staticmethod
  def formKey(grid):
    vertex_rows = grid.vertex_rows
    W = grid.getWidth()
    H = grid.getHeight()
    vertices = []
    for vertex_row in vertex_rows:
      vertices += vertex_row
    vertex_keys = [Vertex.formKey(x) for x in vertices]
    keys = [W, H] + vertex_keys
    result = tuple(keys)
    return result
  @staticmethod
  def formFromKey(key):
    W = key[0]
    H = key[1]
    vertex_keys = key[2 : ]
    grid = FullGrid(W, H)
    for vertex_key in vertex_keys:
      vertex = Vertex.formFromKey(vertex_key)
      id_value = vertex.getIDValue()
      row1 = vertex.getRow()
      col1 = vertex.getCol()
      path_end_id_value = vertex.getPathEndIDValue()
      base_num_connections = vertex.getBaseNumConnections()
      non_base_num_connections = vertex.getNonBaseNumConnections()
      grid.addVertex(id_value, row1, col1, path_end_id_value, base_num_connections, non_base_num_connections)
    return grid
class Surface(Grid):
  def __init__(self, W, H, curr_row_index):
    Grid.__init__(self, W, H)
    self.curr_row_index = curr_row_index
    vertex_rows = defaultdict(lambda: defaultdict(lambda: None))
    self.vertex_rows = vertex_rows
    self.id_to_vertex_dict = {}
    self.location_to_horizontal_cut_edge_path_key_list_dict = defaultdict(lambda: [])
    self.location_to_vertical_cut_edge_path_key_list_dict = defaultdict(lambda: [])
  def getHorizontalCutEdgeExists(self, location):
    matching_path_keys = self.getHorizontalCutEdgePathKeys(location)
    num_matching_path_keys = len(matching_path_keys)
    return num_matching_path_keys > 0
  def getVerticalCutEdgeExists(self, location):
    matching_path_keys = self.getVerticalCutEdgePathKeys(location)
    num_matching_path_keys = len(matching_path_keys)
    return num_matching_path_keys > 0
  def getHorizontalCutEdgePathKeys(self, location):
    matching_path_keys = (self.location_to_horizontal_cut_edge_path_key_list_dict)[location]
    return matching_path_keys[ : ]
  def getVerticalCutEdgePathKeys(self, location):
    matching_path_keys = (self.location_to_vertical_cut_edge_path_key_list_dict)[location]
    return matching_path_keys[ : ]
  # add for location #2
  def _addHorizontalCutEdgePathKey(self, location1, location2):
    path_key = Surface.getPathKey(location1, location2)
    (self.location_to_horizontal_cut_edge_path_key_list_dict)[location2].append(path_key)
  # add for location #2
  def _addVerticalCutEdgePathKey(self, location1, location2):
    path_key = Surface.getPathKey(location1, location2)
    (self.location_to_vertical_cut_edge_path_key_list_dict)[location2].append(path_key)
  # remove for location #2
  def _removeHorizontalCutEdgePathKey(self, location1, location2):
    path_key = Surface.getPathKey(location1, location2)
    (self.location_to_horizontal_cut_edge_path_key_list_dict)[location2].remove(path_key)
  # remove for location #2
  def _removeVerticalCutEdgePathKey(self, location1, location2):
    path_key = Surface.getPathKey(location1, location2)
    (self.location_to_vertical_cut_edge_path_key_list_dict)[location2].remove(path_key)
  # remove for location #2
  # returns True if a horizontal cut-edge was found and removed, 
  # returns False if a vertical cut-edge was found and removed, 
  # or None if no edge was found or removed
  def _idempotentRemoveCutEdgePathKey(self, location1, location2):
    path_key = Surface.getPathKey(location1, location2)
    if path_key in self.getHorizontalCutEdgePathKeys(location2):
      self._removeHorizontalCutEdgePathKey(location1, location2)
      return True
    elif path_key in self.getVerticalCutEdgePathKeys(location2):
      self._removeVerticalCutEdgePathKey(location1, location2)
      return False
    else:
      return None
  # add a vertex to the grid
  def addVertex(self, id_value, row1, col1, path_end_id_value, base_num_connections, non_base_num_connections):
    vertex = Vertex(id_value, row1, col1, path_end_id_value, base_num_connections, non_base_num_connections)
    (self.vertex_rows)[row1][col1] = vertex
    (self.id_to_vertex_dict)[id_value] = vertex
    location1 = (row1, col1)
    location2 = idToLocation(path_end_id_value, self.getWidth() + 1, self.getHeight() + 1)
    return vertex
  def getVertex(self, row, col):
    return (self.vertex_rows)[row][col]
  def getVertexUsingIDValue(self, id_value):
    return (self.id_to_vertex_dict)[id_value]
  def getPathEndNode(self, row, col):
    vertex = self.getVertex(row, col)
    path_end_id_value = vertex.getPathEndIDValue()
    path_end_node = self.getVertexUsingIDValue(path_end_id_value)
    return path_end_node
  @staticmethod
  def getPathKey(location1, location2):
    if location1 <= location2:
      return (location1, location2)
    elif location1 > location2:
      return (location2, location1)
  # set partner of node at (row1, col1) to be node at (row2, col2)
  def setPathEnd(self, row1, col1, row2, col2):
    vertex1 = self.getVertex(row1, col1)
    vertex2 = self.getVertex(row2, col2)
    id_value1 = vertex1.getIDValue()
    id_value2 = vertex2.getIDValue()
    old_partner_id = vertex1.getPathEndIDValue()
    old_partner_location = idToLocation(old_partner_id, self.getWidth() + 1, self.getHeight() + 1)
    path_end_id_value = vertex2.getIDValue()
    vertex1.setPathEndIDValue(path_end_id_value)
    location1 = (row1, col1)
    location2 = (row2, col2)
  def setNumConnections(self, row, col, val):
    vertex = self.getVertex(row, col)
    vertex.setNumConnections(val)
  def getNumConnections(self, row, col):
    vertex = self.getVertex(row, col)
    result = vertex.getNumConnections()
    return result
  def getCurrRowIndex(self):
    return self.curr_row_index
  def setCurrRowIndex(self, curr_row_index):
    self.curr_row_index = curr_row_index
  def _getLocationToHorizontalCutEdgePathKeyListDict(self):
    return self.location_to_horizontal_cut_edge_path_key_list_dict
  def _getLocationToVerticalCutEdgePathKeyListDict(self):
    return self.location_to_horizontal_cut_edge_path_key_list_dict
  @staticmethod
  def formKeyOriginal(grid):
    vertex_rows = grid.vertex_rows
    W = grid.getWidth()
    H = grid.getHeight()
    curr_row_index = grid.getCurrRowIndex()
    lthcepkld = grid._getLocationToHorizontalCutEdgePathKeyListDict()
    ltvcepkld = grid._getLocationToVerticalCutEdgePathKeyListDict()
    lthcepkld_components = []
    ltvcepkld_components = []
    for item in lthcepkld.items():
      location, path_key_list = item
      next_items = [(location, x) for x in path_key_list]
      lthcepkld_components += next_items
    lthcepkld_components.sort()
    for item in ltvcepkld.items():
      location, path_key_list = item
      next_items = [(location, x) for x in path_key_list]
      ltvcepkld_components += next_items
    ltvcepkld_components.sort()
    next_lthcepkld_components = tuple(lthcepkld_components)
    next_ltvcepkld_components = tuple(ltvcepkld_components)
    vertices = []
    for vertex_row in vertex_rows.values():
      vertices += vertex_row.values()
    vertex_keys = [Vertex.formKey(x) for x in vertices]
    keys = [W, H, curr_row_index, next_lthcepkld_components, next_ltvcepkld_components] + vertex_keys
    result = tuple(keys)
    return result
  # use keys for saving work
  # has to be unique enough so that we don't merge unrelated branches
  # cannot be too unique; otherwise, we don't save work
  @staticmethod
  def formKey(grid, row, col):
    return Surface.formKeyNext(grid, row, col)
  # we assume we are considering location (row, col) after a move there
  @staticmethod
  def formKeyNext(grid, row, col):
    W = grid.getWidth()
    H = grid.getHeight()
    num_vertical_components = W + 1
    vertical_components = []
    horizontal_component = None
    id_value = 1
    path_key_to_id_dict = {}
    for curr_col in xrange(num_vertical_components):
      far_vertex_location = None
      # have not moved yet for current time
      if curr_col <= col:
        far_vertex_location = (row + 1, curr_col)
      else:
        far_vertex_location = (row, curr_col)
      curr_id_value = None
      if grid.getVerticalCutEdgeExists(far_vertex_location) == True:
        path_keys = grid.getVerticalCutEdgePathKeys(far_vertex_location)
        path_key = path_keys[0]
        if path_key in path_key_to_id_dict:
          curr_id_value = path_key_to_id_dict[path_key]
        else:
          curr_id_value = id_value
          path_key_to_id_dict[path_key] = curr_id_value
          id_value += 1
      else:
        curr_id_value = 0
      vertical_components.append(curr_id_value)
    far_vertex_location = (row, col + 1)
    curr_id_value = None
    if grid.getHorizontalCutEdgeExists(far_vertex_location) == True:
      path_keys = grid.getHorizontalCutEdgePathKeys(far_vertex_location)
      path_key = path_keys[0]
      if path_key in path_key_to_id_dict:
        curr_id_value = path_key_to_id_dict[path_key]
      else:
        curr_id_value = id_value
        path_key_to_id_dict[path_key] = curr_id_value
        id_value += 1
    else:
      curr_id_value = 0
    horizontal_component = curr_id_value
    components = vertical_components + [horizontal_component]
    key = tuple(components)
    return key
  @staticmethod
  def formFromKeyOld(key):
    W = key[0]
    H = key[1]
    curr_row_index = key[2]
    next_lthcepkld_components = list(key[3])
    next_ltvcepkld_components = list(key[4])
    vertex_keys = key[5 : ]
    grid = Surface(W, H, curr_row_index)
    for item in next_lthcepkld_components:
      location, path_key = item
      l1, l2 = path_key
      location1 = location
      location2 = l1 if l2 == location else l2
      grid._addHorizontalCutEdgePathKey(location1, location2)
    for item in next_ltvcepkld_components:
      location, path_key = item
      l1, l2 = path_key
      location1 = location
      location2 = l1 if l2 == location else l2
      grid._addVerticalCutEdgePathKey(location1, location2)
    for vertex_key in vertex_keys:
      vertex = Vertex.formFromKey(vertex_key)
      id_value = vertex.getIDValue()
      row1 = vertex.getRow()
      col1 = vertex.getCol()
      path_end_id_value = vertex.getPathEndIDValue()
      base_num_connections = vertex.getBaseNumConnections()
      non_base_num_connections = vertex.getNonBaseNumConnections()
      grid.addVertex(id_value, row1, col1, path_end_id_value, base_num_connections, non_base_num_connections)
    return grid
  # get vertices to be stored - not all vertices
  # specifically, nodes where it or its partner is in three rows of interest
  # note that curr. row index should be set to center row index
  def getVertices(self):
    vertex_rows = self.vertex_rows
    H = self.getHeight()
    curr_row_index = self.getCurrRowIndex()
    vertices = []
    for i in xrange(max(curr_row_index - 1, 0), curr_row_index + 2):
      vertex_row = vertex_rows[i]
      next_vertex_row = vertex_row.values()
      vertices += next_vertex_row
    next_vertices = set(vertices)
    for vertex in vertices:
      location = vertex.getLocation()
      row, col = location
      path_end = self.getPathEndNode(row, col)
      next_vertices |= set([path_end])
    next_next_vertices = list(next_vertices)
    return next_next_vertices
  def clone(self):
    W = self.getWidth()
    H = self.getHeight()
    curr_row_index = self.getCurrRowIndex()
    surface = Surface(W, H, curr_row_index)
    lthcepkld = defaultdict(lambda: [])
    for item in self.location_to_horizontal_cut_edge_path_key_list_dict.items():
      location, path_key_list = item
      if len(path_key_list) != 0:
        lthcepkld[location] = path_key_list[ : ]
    ltvcepkld = defaultdict(lambda: [])
    for item in self.location_to_vertical_cut_edge_path_key_list_dict.items():
      location, path_key_list = item
      if len(path_key_list) != 0:
        ltvcepkld[location] = path_key_list[ : ]
    surface.location_to_horizontal_cut_edge_path_key_list_dict = lthcepkld
    surface.location_to_vertical_cut_edge_path_key_list_dict = ltvcepkld
    vertices = self.getVertices()
    for vertex in vertices:
      id_value = vertex.getIDValue()
      path_end_id_value = vertex.getPathEndIDValue()
      base_num_connections = vertex.getBaseNumConnections()
      non_base_num_connections = vertex.getNonBaseNumConnections()
      location = vertex.getLocation()
      row, col = location
      surface.addVertex(id_value, row, col, path_end_id_value, base_num_connections, non_base_num_connections)
    return surface
  # keep a vertex if it or its partner is in three rows of interest
  def _advanceOneRow(self, reference_full_grid):
    curr_row_index = self.getCurrRowIndex()
    next_row_index = curr_row_index + 1
    prev_row_index = curr_row_index - 1
    # update curr. row index
    self.setCurrRowIndex(curr_row_index + 1)
    have_prev_row = (curr_row_index - 1) >= 0
    next_next_row = reference_full_grid.getVertexRow(curr_row_index + 2)
    # note that next row will not be present in vertices returned from getVertices()
    next_next_row_safe = [x.clone() for x in next_next_row]
    safe_vertices = self.getVertices() + next_next_row_safe
    safe_vertices_set = set(safe_vertices)
    # keep partners of previously mentioned vertices
    # throw out one row, selectively
    lthcepkld = self.location_to_horizontal_cut_edge_path_key_list_dict
    ltvcepkld = self.location_to_vertical_cut_edge_path_key_list_dict
    if have_prev_row == True:
      vertices = (self.vertex_rows)[prev_row_index].values()
      for i in xrange(len(vertices)):
        vertex = vertices[i]
        id_value = vertex.getIDValue()
        location = vertex.getLocation()
        if vertex not in safe_vertices_set:
          (self.vertex_rows)[prev_row_index].pop(i)
          (self.id_to_vertex_dict).pop(id_value)
          if location in lthcepkld:
            lthcepkld.pop(location)
          if location in ltvcepkld:
            ltvcepkld.pop(location)
      if len((self.vertex_rows)[prev_row_index]) == 0:
        (self.vertex_rows).pop(prev_row_index)
    # bring over one row from reference full grid
    for vertex in next_next_row_safe:
      id_value = vertex.getIDValue()
      path_end_id_value = vertex.getPathEndIDValue()
      base_num_connections = vertex.getBaseNumConnections()
      non_base_num_connections = vertex.getNonBaseNumConnections()
      location = vertex.getLocation()
      row, col = location
      self.addVertex(id_value, row, col, path_end_id_value, base_num_connections, non_base_num_connections)
    # assume that we don't have to add items to lthcepkld or ltvcepkld for the added vertices
class Vertex:
  def __init__(self, id_value, row, col, path_end_id_value, base_num_connections, non_base_num_connections):
    self.id_value = id_value
    self.path_end_id_value = path_end_id_value
    self.base_num_connections = base_num_connections
    self.non_base_num_connections = non_base_num_connections
    self.row = row
    self.col = col
  def getIDValue(self):
    return self.id_value
  def getRow(self):
    return self.row
  def getCol(self):
    return self.col
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
  def getLocation(self):
    return (self.row, self.col)
  def toLocationString(self):
    return str(self.getLocation())
  def toString(self):
    node1 = self
    node2 = self.getPathEnd()
    node_str1 = node1.toLocationString()
    node_str2 = node2.toLocationString()
    result = "(" + node_str1 + ", " + node_str2 + ")"
    return result
  def getPathEndIDValue(self):
    return self.path_end_id_value
  def setPathEndIDValue(self, path_end_id_value):
    self.path_end_id_value = path_end_id_value
  @staticmethod
  def formKey(vertex):
    id_value = vertex.getIDValue()
    path_end_id_value = vertex.getPathEndIDValue()
    base_num_connections = vertex.base_num_connections
    non_base_num_connections = vertex.non_base_num_connections
    location = vertex.getLocation()
    components = [id_value, location, path_end_id_value, base_num_connections, non_base_num_connections]
    next_components = tuple(components)
    return next_components
  @staticmethod
  def formFromKey(key):
    id_value, location, path_end_id_value, base_num_connections, non_base_num_connections = key
    row1, col1 = location
    vertex = Vertex(id_value, row1, col1, path_end_id_value, base_num_connections, non_base_num_connections)
    return vertex
  def clone(self):
    key = Vertex.formKey(self)
    vertex = Vertex.formFromKey(key)
    return vertex
class Connection:
  def __init__(self):
    self.connected = None
    self.room = None
    self.neighbor = None
    self.room_partner = None
    self.neighbor_partner = None
  # connect location #1 to location #2
  def connect(self, location1, location2, full_grid, is_for_horizontal_cut_edge):
    row1, col1 = location1
    row2, col2 = location2
    vertex_a = full_grid.getVertex(row1, col1)
    vertex_b = full_grid.getVertex(row2, col2)
    room = vertex_a
    neighbor = vertex_b
    connected = False
    num_connections1 = full_grid.getNumConnections(room.getRow(), room.getCol())
    num_connections2 = full_grid.getNumConnections(neighbor.getRow(), neighbor.getCol())
    room_partner = None
    neighbor_partner = None
    # there must be room for the connections
    if num_connections1 != 2 and num_connections2 != 2:
      # avoid forming a cycle
      if room != full_grid.getPathEndNode(neighbor.getRow(), neighbor.getCol()):
        # room partner is far end on room's side
        room_partner = full_grid.getPathEndNode(room.getRow(), room.getCol())
        # neighbor partner is far end on neighbor's side
        neighbor_partner = full_grid.getPathEndNode(neighbor.getRow(), neighbor.getCol())
        assert(full_grid.getPathEndNode(room_partner.getRow(), room_partner.getCol()) == room)
        assert(full_grid.getPathEndNode(neighbor_partner.getRow(), neighbor_partner.getCol()) == neighbor)
        connected = True
        full_grid.setPathEnd(room_partner.getRow(), room_partner.getCol(), neighbor_partner.getRow(), neighbor_partner.getCol())
        full_grid.setPathEnd(neighbor_partner.getRow(), neighbor_partner.getCol(), room_partner.getRow(), room_partner.getCol())
        full_grid.setNumConnections(room.getRow(), room.getCol(), room.getNumConnections() + 1)
        full_grid.setNumConnections(neighbor.getRow(), neighbor.getCol(), neighbor.getNumConnections() + 1)
        # outer locations are protruding
        was_horizontal1 = full_grid._idempotentRemoveCutEdgePathKey(room.getLocation(), room_partner.getLocation())
        full_grid._idempotentRemoveCutEdgePathKey(room_partner.getLocation(), room.getLocation())
        was_horizontal2 = full_grid._idempotentRemoveCutEdgePathKey(neighbor.getLocation(), neighbor_partner.getLocation())
        full_grid._idempotentRemoveCutEdgePathKey(neighbor_partner.getLocation(), neighbor.getLocation())
        if was_horizontal1 == True or (was_horizontal1 == None and is_for_horizontal_cut_edge == True):
          full_grid._addHorizontalCutEdgePathKey(neighbor_partner.getLocation(), room_partner.getLocation())
        elif was_horizontal1 == False or (was_horizontal1 == None and is_for_horizontal_cut_edge == False):
          full_grid._addVerticalCutEdgePathKey(neighbor_partner.getLocation(), room_partner.getLocation())
        if was_horizontal2 == True or (was_horizontal2 == None and is_for_horizontal_cut_edge == True):
          full_grid._addHorizontalCutEdgePathKey(room_partner.getLocation(), neighbor_partner.getLocation())
        elif was_horizontal2 == False or (was_horizontal2 == None and is_for_horizontal_cut_edge == False):
          full_grid._addVerticalCutEdgePathKey(room_partner.getLocation(), neighbor_partner.getLocation())
    self.connected = connected
    self.room = room
    self.neighbor = neighbor
    self.room_partner = room_partner
    self.neighbor_partner = neighbor_partner
  def successfullyConnected(self):
    return self.connected
  @staticmethod
  def formKey(connection):
    connected = connection.connected
    room = connection.room
    neighbor = connection.neighbor
    room_partner = connection.room_partner
    neighbor_partner = connection.neighbor_partner
    components = [connected, room.getLocation(), neighbor.getLocation(), room_partner.getLocation(), neighbor_partner.getLocation()]
    next_components = tuple(components)
    return next_components
  @staticmethod
  def formFromKey(key, location_to_vertex_dict):
    connected, location1, location2, location3, location4 = key
    room = location_to_vertex_dict[location1]
    neighbor = location_to_vertex_dict[location2]
    room_partner = location_to_vertex_dict[location3]
    neighbor_partner = location_to_vertex_dict[location4]
    connection = Connection()
    connection.connected = connected
    connection.room = room
    connection.neighbor = neighbor
    connection.room_partner = room_partner
    connection.neighbor_partner = neighbor_partner
    return connection
class SolutionCounter:
  def __init__(self, count = 0):
    self.count = count
  def getCount(self):
    return self.count
  def setCount(self, count):
    self.count = count
  def increment(self):
    self.count += 1
  def incrementBy(self, val):
    self.count += val
def solve(full_grid, grid, counter):
  W = grid.getWidth()
  H = grid.getHeight()
  curr_grid_key_to_count_dict = defaultdict(lambda: 0)
  curr_grid_key_to_surface_dict = {}
  initial_surface = grid
  initial_key = tuple([0] * (W + 2))
  curr_grid_key_to_count_dict[initial_key] = 1
  curr_grid_key_to_surface_dict[initial_key] = initial_surface
  next_grid_key_to_count_dict = defaultdict(lambda: 0)
  next_grid_key_to_surface_dict = {}
  for row in xrange(H):
    for col in xrange(W):
      grid_key_count_pairs = curr_grid_key_to_count_dict.items()
      for grid_key_count_pair in grid_key_count_pairs:
        grid_key, count = grid_key_count_pair
        surface = curr_grid_key_to_surface_dict[grid_key].clone()
        if row > 0 and col == 0:
          surface._advanceOneRow(full_grid)
        vertex = surface.getVertex(row, col)
        vertex_right = surface.getVertex(row + 1, col)
        vertex_down = surface.getVertex(row, col + 1)
        num_connections = surface.getNumConnections(row, col)
        if num_connections == 2:
          next_surface_key = Surface.formKey(surface, row, col)
          next_grid_key_to_count_dict[next_surface_key] += count
          next_grid_key_to_surface_dict[next_surface_key] = surface
          continue
        elif num_connections == 0:
          c1 = Connection()
          c2 = Connection()
          c1.connect(vertex.getLocation(), vertex_right.getLocation(), surface, False)
          c2.connect(vertex.getLocation(), vertex_down.getLocation(), surface, True)
          if c1.successfullyConnected() and c2.successfullyConnected():
            next_surface_key = Surface.formKey(surface, row, col)
            next_grid_key_to_count_dict[next_surface_key] += count
            next_grid_key_to_surface_dict[next_surface_key] = surface
          continue
        elif num_connections == 1:
          surface1 = surface
          surface2 = surface1.clone()
          c1 = Connection()
          c1.connect(vertex.getLocation(), vertex_right.getLocation(), surface1, False)
          if c1.successfullyConnected() == True:
            next_surface_key1 = Surface.formKey(surface1, row, col)
            next_grid_key_to_count_dict[next_surface_key1] += count
            next_grid_key_to_surface_dict[next_surface_key1] = surface1
          c2 = Connection()
          c2.connect(vertex.getLocation(), vertex_down.getLocation(), surface2, True)
          if c2.successfullyConnected() == True:
            next_surface_key2 = Surface.formKey(surface2, row, col)
            next_grid_key_to_count_dict[next_surface_key2] += count
            next_grid_key_to_surface_dict[next_surface_key2] = surface2
      curr_grid_key_to_count_dict = next_grid_key_to_count_dict
      next_grid_key_to_count_dict = defaultdict(lambda: 0)
      curr_grid_key_to_surface_dict = next_grid_key_to_surface_dict
      next_grid_key_to_surface_dict = {}
  grid_key_counts = curr_grid_key_to_count_dict.values()
  count = sum(grid_key_counts)
  counter.incrementBy(count)
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
full_grid = FullGrid(W, H)
grid2 = Surface(W, H, 0)
id_value = 0
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
    vertex = grid2.addVertex(id_value, i, j, id_value, base_num_connections, 0)
    full_grid.addVertex(id_value, i, j, id_value, base_num_connections, 0)
    id_value += 1
counter = SolutionCounter()
solve(full_grid, grid2, counter)
num_solutions = counter.getCount()
print num_solutions
