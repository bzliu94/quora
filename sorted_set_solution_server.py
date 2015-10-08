# 2015-10-08

# have messages sent serially across eight different threads

# have a single mut. exclusion lock for handleReturnMessage()

# "get range" command can work if we assume that sets 
# don't have to exist to be referenced

from struct import pack, unpack
from multiprocessing import Process, Lock, Manager
def within(value, lower_value, upper_value):
  return value >= lower_value and value <= upper_value
def keyScorePairComp(key_score_pair1, key_score_pair2):
  key1, score1 = key_score_pair1
  key2, score2 = key_score_pair2
  if key1 < key2:
    return -1
  elif key1 > key2:
    return 1
  else:
    if score1 < score2:
      return -1
    elif score1 > score2:
      return 1
    elif score1 == score2:
      return 0
class SortedSet:
  def __init__(self, id_value):
    self.id_value = id_value
    self.values = {}
  def getIDValue(self):
    return self.id_value
  def getValues(self):
    return self.values
  def getLock(self):
    return self.lock
  def addScore(self, key, score):
    self.values[key] = score
  def containsKey(self, key):
    return key in self.values
  def removeKey(self, key):
    self.values.pop(key)
  def getSize(self):
    return len(self.values)
  def getValueForKey(self, key):
    return self.values[key]
  @staticmethod
  def getRange(sets, lower_value, upper_value):
    value_dict_list = [x.getValues() for x in sets]
    key_score_list_list = [x.items() for x in value_dict_list]
    key_score_list = reduce(lambda x, y: x + y, key_score_list_list, [])
    filtered_key_score_list = [x for x in key_score_list if within(x[1], lower_value, upper_value)]
    sorted_filtered_key_score_list = sorted(filtered_key_score_list, cmp = keyScorePairComp)
    return sorted_filtered_key_score_list
  def toString(self):
    return str(self.values)
manager = Manager()
lock = manager.Lock()
class Event:
  def __init__(self):
    pass
  def isAddScoreEvent(self):
    return False
  def isRemoveKeyEvent(self):
    return False
  def isGetSizeEvent(self):
    return False
  def isGetKeyValueEvent(self):
    return False
  def isGetRangeEvent(self):
    return False
  def isDisconnectEvent(self):
    return False
  def handleReturnMessage(self, connection):
    pass
class AddScoreEvent(Event):
  def __init__(self, set_id, key, score):
    self.set_id = set_id
    self.key = key
    self.score = score
  def isAddScoreEvent(self):
    return True
  def getSetIDValue(self):
    return self.set_id
  def getKey(self):
    return self.key
  def getScore(self):
    return self.score
  def handleReturnMessage(self, connection):
    # add a score
    lock.acquire()
    set_id = self.getSetIDValue()
    if set_id not in id_to_set_dict:
      id_to_set_dict[set_id] = SortedSet(set_id)
    associated_set = id_to_set_dict[set_id]
    key = self.getKey()
    score = self.getScore()
    associated_set.addScore(key, score)
    # re-assign as dict. value may be out of sync
    id_to_set_dict[set_id] = associated_set
    lock.release()
    data = [0]
    return data
class RemoveKeyEvent(Event):
  def __init__(self, set_id, key):
    self.set_id = set_id
    self.key = key
  def isRemoveKeyEvent(self):
    return True
  def getSetIDValue(self):
    return self.set_id
  def getKey(self):
    return self.key
  def handleReturnMessage(self, connection):
    # remove a key
    lock.acquire()
    set_id = self.getSetIDValue()
    key = self.getKey()
    if set_id in id_to_set_dict:
      associated_set = id_to_set_dict[set_id]
      if associated_set.containsKey(key):
        associated_set.removeKey(key)
        # re-assign as dict. value may be out of sync
        id_to_set_dict[set_id] = associated_set
    lock.release()
    data = [0]
    return data
class GetSizeEvent(Event):
  def __init__(self, set_id):
    self.set_id = set_id
  def isGetSizeEvent(self):
    return True
  def getSetIDValue(self):
    return self.set_id
  def handleReturnMessage(self, connection):
    # get size of a set
    lock.acquire()
    set_id = self.getSetIDValue()
    size = None
    if set_id in id_to_set_dict:
      associated_set = id_to_set_dict[set_id]
      size = associated_set.getSize()
    else:
      size = 0
    lock.release()
    data = [1, size]
    return data
class GetKeyValueEvent(Event):
  def __init__(self, set_id, key):
    self.set_id = set_id
    self.key = key
  def isGetKeyValueEvent(self):
    return True
  def getSetIDValue(self):
    return self.set_id
  def getKey(self):
    return self.key
  def handleReturnMessage(self, connection):
    # get key-value pair from a set
    lock.acquire()
    set_id = self.getSetIDValue()
    key = self.getKey()
    score = None
    if set_id in id_to_set_dict:
      associated_set = id_to_set_dict[set_id]
      if associated_set.containsKey(key):
        score = associated_set.getValueForKey(key)
      else:
        score = 0
    else:
      score = 0
    lock.release()
    data = [1, score]
    return data
class GetRangeEvent(Event):
  def __init__(self, set_id_values, lower_value, upper_value):
    self.set_id_values = set_id_values
    self.lower_value = lower_value
    self.upper_value = upper_value
  def isGetRangeEvent(self):
    return True
  def getSetIDValues(self):
    return self.set_id_values
  def getLowerValue(self):
    return self.lower_value
  def getUpperValue(self):
    return self.upper_value
  def handleReturnMessage(self, connection):
    # get items within a "range" from a collection of sets
    lock.acquire()
    set_id_values = self.getSetIDValues()
    lower_value = self.getLowerValue()
    upper_value = self.getUpperValue()
    associated_sets = []
    for set_id_value in set_id_values:
      if set_id_value in id_to_set_dict:
        associated_set = id_to_set_dict[set_id_value]
        associated_sets.append(associated_set)
    key_score_pair_list = SortedSet.getRange(associated_sets, lower_value, upper_value)
    K = len(key_score_pair_list) * 2
    flattened_key_score_pair_list = []
    for pair in key_score_pair_list:
      key, score = pair
      flattened_key_score_pair_list.append(key)
      flattened_key_score_pair_list.append(score)
    lock.release()
    data = [K] + flattened_key_score_pair_list
    return data
class DisconnectEvent(Event):
  def __init__(self):
    pass
  def isDisconnectEvent(self):
    return True
  def handleReturnMessage(self, connection):
    # close connection
    connection.close()
from collections import defaultdict
import socket
import sys
import os
server_address = './socket'
try:
    os.unlink(server_address)
except OSError:
    if os.path.exists(server_address):
        raise
sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
sock.bind(server_address)
sock.listen(1)
ADD_SCORE = 1
REMOVE_KEY = 2
GET_SIZE = 3
GET_KEY_VALUE = 4
GET_RANGE = 5
DISCONNECT = 6
id_to_set_dict = manager.dict()
def slaveThreadStart(thread_id, connection):
  while True:
    header = unpack('!I', connection.recv(4))[0]
    n = header
    message_parts = []
    for i in xrange(n):
      message_part = unpack('!I', connection.recv(4))[0]
      message_parts.append(message_part)
    command_type = message_parts[0]
    event = None
    if command_type == ADD_SCORE:
      set_id = int(message_parts[1])
      key = int(message_parts[2])
      score = int(message_parts[3])
      event = AddScoreEvent(set_id, key, score)
    elif command_type == REMOVE_KEY:
      set_id = int(message_parts[1])
      key = int(message_parts[2])
      event = RemoveKeyEvent(set_id, key)
    elif command_type == GET_SIZE:
      set_id = int(message_parts[1])
      event = GetSizeEvent(set_id)
    elif command_type == GET_KEY_VALUE:
      set_id = int(message_parts[1])
      key = int(message_parts[2])
      event = GetKeyValueEvent(set_id, key)
    elif command_type == GET_RANGE:
      num_sets = len(message_parts) - 4
      set_id_values = message_parts[1 : 1 + num_sets]
      lower_value = int(message_parts[num_sets + 2])
      upper_value = int(message_parts[num_sets + 3])
      event = GetRangeEvent(set_id_values, lower_value, upper_value)
    elif command_type == DISCONNECT:
      event = DisconnectEvent()
    data = event.handleReturnMessage(connection)
    if event.isDisconnectEvent() == True:
      break
    for n in data:
      connection.send(pack('!I', n))
thread_id_to_process_dict = {}
thread_id = 0
while True:
    connection, client_address = sock.accept()
    try:
        p = Process(target = slaveThreadStart, args = (thread_id, connection))
        thread_id_to_process_dict[thread_id] = p
        thread_id += 1
        p.start()
    finally:
        pass
