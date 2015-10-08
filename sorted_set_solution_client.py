# 2015-10-08

from multiprocessing import Process, Queue
import math
from struct import pack, unpack
class SortedSet:
  def __init__(self, id_value):
    self.id_value = id_value
  def getIDValue(self):
    return self.id_value
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
  def toCommandData(self):
    return None
  def handleReturnMessage(self, sock, header):
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
  def toCommandData(self):
    set_id = self.getSetIDValue()
    key = self.getKey()
    score = self.getScore()
    data = [4, 1, set_id, key, score]
    return data
  def handleReturnMessage(self, sock, header):
    message_length = header
    return [message_length]
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
  def toCommandData(self):
    set_id = self.getSetIDValue()
    key = self.getKey()
    data = [3, 2, set_id, key]
    return data
  def handleReturnMessage(self, sock, header):
    message_length = header
    return [message_length]
class GetSizeEvent(Event):
  def __init__(self, set_id):
    self.set_id = set_id
  def isGetSizeEvent(self):
    return True
  def getSetIDValue(self):
    return self.set_id
  def toCommandData(self):
    set_id = self.getSetIDValue()
    data = [2, 3, set_id]
    return data
  def handleReturnMessage(self, sock, header):
    message_length = header
    size = unpack('!I', sock.recv(4))[0]
    parts = [message_length, size]
    return parts
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
  def toCommandData(self):
    set_id = self.getSetIDValue()
    key = self.getKey()
    data = [3, 4, set_id, key]
    return data
  def handleReturnMessage(self, sock, header):
    message_length = header
    score = unpack('!I', sock.recv(4))[0]
    parts = [message_length, score]
    return parts
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
  def toCommandData(self):
    set_id_values = self.getSetIDValues()
    lower_value = self.getLowerValue()
    upper_value = self.getUpperValue()
    num_sets = len(set_id_values)
    num_arguments = num_sets + 4
    data = [num_arguments, 5] + set_id_values + [0, lower_value, upper_value]
    return data
  def handleReturnMessage(self, sock, header):
    message_length = header
    K = message_length
    pair_count = K / 2
    pairs = []
    for i in xrange(pair_count):
      curr_key = unpack('!I', sock.recv(4))[0]
      curr_score = unpack('!I', sock.recv(4))[0]
      pair = (curr_key, curr_score)
      pairs.append(pair)
    non_flattened_pairs = map(lambda x: [x[0], x[1]], pairs)
    flattened_pairs = reduce(lambda x, y: x + y, non_flattened_pairs, [])
    parts = [K] + flattened_pairs
    return parts
class DisconnectEvent(Event):
  def __init__(self):
    pass
  def isDisconnectEvent(self):
    return True
  def toCommandData(self):
    data = [1, 6]
    return data
  def handleReturnMessage(self, sock, header):
    return None
from collections import defaultdict
id_to_set_dict = defaultdict(lambda: None)
import sys
import string
stream = open("tests/official/input08.txt")
event_list = []
line = stream.readline()
line = line.rstrip("\n")
args = line.split(" ")
args = [string.atol(x) for x in args]
N = int(args[0])
for i in xrange(N):
  line = stream.readline()
  line = line.rstrip("\n")
  args = line.split(" ")
  args = [string.atol(x) for x in args]
  command_type = args[0]
  command_argument_list = []
  if command_type == 1:
    set_id = int(args[1])
    key = int(args[2])
    score = int(args[3])
    event = AddScoreEvent(set_id, key, score)
    event_list.append(event)
  elif command_type == 2:
    set_id = int(args[1])
    key = int(args[2])
    event = RemoveKeyEvent(set_id, key)
    event_list.append(event)
  elif command_type == 3:
    set_id = int(args[1])
    event = GetSizeEvent(set_id)
    event_list.append(event)
  elif command_type == 4:
    set_id = int(args[1])
    key = int(args[2])
    event = GetKeyValueEvent(set_id, key)
    event_list.append(event)
  elif command_type == 5:
    num_sets = len(args) - 4
    set_id_values = args[1 : 1 + num_sets]
    lower_value = int(args[num_sets + 2])
    upper_value = int(args[num_sets + 3])
    event = GetRangeEvent(set_id_values, lower_value, upper_value)
    event_list.append(event)
import socket
import sys
def connect():
  sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
  server_address = './socket'
  try:
    sock.connect(server_address)
  except socket.error, msg:
    sys.exit(1)
  return sock
def disconnect(sock):
  event = DisconnectEvent()
  data = event.toCommandData()
  for n in data:
    sock.send(pack('!I', n))
  sock.close()
def slaveThreadStart(thread_id, inbox_queue, outbox_queue, event_count):
  sock = connect()
  num_seen_events = 0
  while num_seen_events < event_count:
    event = inbox_queue.get()
    data = event.toCommandData()
    result = None
    for n in data:
      sock.send(pack('!I', n))
    else:
      header = unpack('!I', sock.recv(4))[0]
      message_length = header
      result = event.handleReturnMessage(sock, header)
    outbox_queue.put(result)
    num_seen_events += 1
  disconnect(sock)
thread_id_to_inbox_queue_dict = {}
thread_id_to_outbox_queue_dict = {}
thread_id_to_process_dict = {}
thread_id_to_event_count_dict = {}
for i in xrange(8):
  inbox_queue = Queue()
  outbox_queue = Queue()
  thread_id = i
  thread_id_to_inbox_queue_dict[thread_id] = inbox_queue
  thread_id_to_outbox_queue_dict[thread_id] = outbox_queue
  num_events = len(event_list)
  event_count = int(math.floor(num_events / 8)) + (1 if (num_events % 8) >= (i + 1) else 0)
  thread_id_to_event_count_dict[thread_id] = event_count
  p = Process(target = slaveThreadStart, args = (thread_id, inbox_queue, outbox_queue, event_count))
  thread_id_to_process_dict[thread_id] = p
  p.start()
result_list = []
for i in xrange(len(event_list)):
  thread_id = i % 8
  inbox_queue = thread_id_to_inbox_queue_dict[thread_id]
  outbox_queue = thread_id_to_outbox_queue_dict[thread_id]
  event = event_list[i]
  inbox_queue.put(event)
  result = outbox_queue.get()
  result_list.append(result)
for result in result_list:
  if result != None:
    parts = result
    for part in parts:
      print part
for i in xrange(8):
  thread_id = i
  process = thread_id_to_process_dict[thread_id]
  process.join()
