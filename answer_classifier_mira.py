# 2015-12-29

# can use decision trees with random forest bagging and adaboost boosting 
# to get up to 87.71% correct on data from test #1 in within 10 seconds

# use pre-trained custom-implemented margin-infused relaxed algorithm (mira) 
# to get ~79.4% correct on data from test #1

import copy
import math
import sys
from collections import defaultdict
import string
class Counter(dict):
  def __getitem__(self, idx):
    self.setdefault(idx, 0)
    return dict.__getitem__(self, idx)
  def incrementAll(self, keys, count):
    for key in keys:
      self[key] += count
  def argMax(self):
    if len(self.keys()) == 0: return None
    all = self.items()
    values = [x[1] for x in all]
    maxIndex = values.index(max(values))
    return all[maxIndex][0]
  def sortedKeys(self):
    sortedItems = self.items()
    compare = lambda x, y:  sign(y[1] - x[1])
    sortedItems.sort(cmp=compare)
    return [x[0] for x in sortedItems]
  def totalCount(self):
    return sum(self.values())
  def normalize(self):
    total = float(self.totalCount())
    if total == 0: return
    for key in self.keys():
      self[key] = self[key] / total
  def multiplyAll(self, multiplier):
    for key in self:
      self[key] *= multiplier
  def divideAll(self, divisor):
    divisor = float(divisor)
    for key in self:
      self[key] /= divisor
  def copy(self):
    return Counter(dict.copy(self))
  def __mul__(self, y ):
    sum = 0
    x = self
    if len(x) > len(y):
      x,y = y,x
    for key in x:
      if key not in y:
        continue
      sum += x[key] * y[key]
    return sum
  def __radd__(self, y):
    for key, value in y.items():
      self[key] += value
  def __add__( self, y ):
    addend = Counter()
    for key in self:
      if key in y:
        addend[key] = self[key] + y[key]
      else:
        addend[key] = self[key]
    for key in y:
      if key in self:
        continue
      addend[key] = y[key]
    return addend
  def __sub__( self, y ):
    addend = Counter()
    for key in self:
      if key in y:
        addend[key] = self[key] - y[key]
      else:
        addend[key] = self[key]
    for key in y:
      if key in self:
        continue
      addend[key] = -1 * y[key]
    return addend
class MiraClassifier:
  def __init__( self, legalLabels, max_iterations):
    self.legalLabels = legalLabels
    self.C = 0.001
    self.max_iterations = max_iterations
    self.initializeWeightsToZero()
  def initializeWeightsToZero(self):
    self.weights = {}
    for label in self.legalLabels:
      self.weights[label] = Counter() 
  def train(self, trainingData, trainingLabels, validationData, validationLabels):
    self.features = trainingData[0].keys() 
    C = self.C
    return self.trainGivenC(trainingData, trainingLabels, validationData, validationLabels, C)
  def trainGivenC(self, trainingData, trainingLabels, validationData, validationLabels, C):
    Cgrid = [C]
    w = Counter()
    for C in Cgrid:
      w[C] = copy.deepcopy(self.weights)
    for iteration in range(self.max_iterations):
      for i in range(len(trainingData)):
        feature_vec = trainingData[i]
        actual_label = trainingLabels[i]
        for C in Cgrid:
          label_scores = Counter()
          for label in self.legalLabels:
            score = feature_vec * w[C][label]
            label_scores[label] = score
          guessed_label = label_scores.argMax()
          if actual_label != guessed_label:
            val = ((w[C][guessed_label] - w[C][actual_label]) * feature_vec + 1)
            val = val / (2.0 * (feature_vec * feature_vec))
            tau = min(C, val)
            vec = feature_vec.copy()
            vec.multiplyAll(tau)
            w[C][actual_label] = w[C][actual_label] + vec
            w[C][guessed_label] = w[C][guessed_label] - vec
    chosen_C = self.C
    for label in self.legalLabels:
      for feature in self.features:
        self.weights[label][feature] = w[chosen_C][label][feature]
  def classify(self, data ):
    guesses = []
    for datum in data:
      vectors = Counter()
      for l in self.legalLabels:
        vectors[l] = self.weights[l] * datum
      guesses.append(vectors.argMax())
    return guesses
class MIRAClassifierAdapted:
  def __init__(self, C, legal_labels, max_iterations):
    mira_classifier = MiraClassifier(legal_labels, max_iterations)
    mira_classifier.C = C
    self.mira_classifier = mira_classifier
  def _getClassifier(self):
    return self.mira_classifier 
  def fit(self, X, y, validation_X, validation_y):
    classifier = self._getClassifier()
    next_X = []
    for i in xrange(len(y)):
      label = y[i]
      datum = Counter()
      feature_vector = X[i]
      for j in xrange(len(feature_vector)):
        feature_value = feature_vector[j]
        datum[j] = feature_value
      next_X.append(datum)
    next_validation_X = []
    for i in xrange(len(validation_y)):
      label = validation_y[i]
      datum = Counter()
      feature_vector = validation_X[i]
      for j in xrange(len(feature_vector)):
        feature_value = feature_vector[j]
        datum[j] = feature_value
      next_validation_X.append(datum)
    classifier.train(next_X, y, next_validation_X, validation_y)
  def predict(self, X):
    classifier = self._getClassifier()
    next_X = []
    for i in xrange(len(X)):
      datum = Counter()
      feature_vector = X[i]
      for j in xrange(len(feature_vector)):
        feature_value = feature_vector[j]
        datum[j] = feature_value
      next_X.append(datum)
    result = classifier.classify(next_X)
    return result
  def score(self, X, y):
    y_predicted = self.predict(X)
    num_correct = len([x for x in xrange(len(X)) if y_predicted[x] == y[x]])
    num_total = len(X)
    accuracy = num_correct / (1.0 * num_total)
    return accuracy
def shifted_data_variance(data):
   if len(data) == 0:
      return 0
   K = data[0]
   n = 0
   Sum = 0
   Sum_sqr = 0
   for x in data:
      n = n + 1
      Sum += x - K
      Sum_sqr += (x - K) * (x - K)
   variance = (Sum_sqr - (Sum * Sum)/(1.0 * n))/(1.0 * n)
   return variance
class StandardScaler:
  def __init__(self, num_components):
    self.mean_values = {}
    self.std_deviation_values = {}
    self.num_components = num_components
  def _getMeanValue(self, i):
    return self.mean_values[i]
  def _getStdDeviationValue(self, i):
    return self.std_deviation_values[i]
  def _setMeanValue(self, i, value):
    self.mean_values[i] = value
  def _setStdDeviationValue(self, i, value):
    self.std_deviation_values[i] = value
  def getNumComponents(self):
    return self.num_components
  def fit(self, values):
    index_to_value_list_dict = defaultdict(lambda: [])
    for feature_vector in values:
      for i in xrange(len(feature_vector)):
        feature_value = feature_vector[i]
        index_to_value_list_dict[i].append(feature_value)
    num_components = self.getNumComponents()
    for i in xrange(num_components):
      values = index_to_value_list_dict[i]
      mean = StandardScaler.getMean(values)
      std_deviation = StandardScaler.getStdDeviation(values)
      self._setMeanValue(i, mean)
      self._setStdDeviationValue(i, std_deviation)
  def transform(self, values):
    num_components = self.getNumComponents()
    next_values = []
    for feature_vector in values:
      next_feature_vector = []
      for i in xrange(num_components):
        feature_value = feature_vector[i]
        mean = self._getMeanValue(i)
        std_deviation = self._getStdDeviationValue(i)
        variance = std_deviation ** 2
        next_feature_value = None
        if variance == 0:
          next_feature_value = feature_value - mean
        else:
          next_feature_value = (feature_value - mean) / (1.0 * variance)
        next_feature_vector.append(next_feature_value)
      next_values.append(next_feature_vector)
    return next_values
  @staticmethod
  def getMean(values):
    num_values = len(values)
    return sum(values) / (1.0 * num_values)
  @staticmethod
  def getStdDeviation(values):
    variance = shifted_data_variance(values)
    std_deviation = math.sqrt(variance)
    return std_deviation
def MIRA_train(X_in, y_in, X_out, cs):
  M = len(X_in[0])
  test_indices, train_indices = splitIndices(len(X_in), int(round(0.1 * len(X_in))))
  X_scaler = [X_in[i] for i in test_indices]
  y_scaler = [y_in[i] for i in test_indices]
  X_in = [X_in[i] for i in train_indices]
  y_in = [y_in[i] for i in train_indices]
  scaler = StandardScaler(M)
  scaler.fit(X_scaler)
  X_scaler = scaler.transform(X_scaler)
  X_in = scaler.transform(X_in)
  X_out = scaler.transform(X_out)
  std_test = [scaler._getStdDeviationValue(x) for x in xrange(M)]
  f_indices = [j for j in range(M) if std_test[j] > 1e-7]
  X_in = [[X_in[i][j] for j in f_indices] for i in range(len(X_in))]
  X_scaler = [[X_scaler[i][j] for j in f_indices] for i in range(len(X_scaler))]
  X_out = [[X_out[i][j] for j in f_indices] for i in range(len(X_out))]   
  M = len(X_in[0])
  clf = MIRAClassifierAdapted(C = c_set[0], legal_labels = [1, -1], max_iterations = 2)
  clf.fit(X_in, y_in, [], [])
  y_out = clf.predict(X_out)
  return y_out
def readInput(stream):
  line = stream.readline()
  line = line.rstrip("\n")
  args = line.split()
  args = [string.atol(x) for x in args]
  N = int(args[0])
  M = int(args[1])
  X_train = []
  y_train = []
  train_id_list = []
  X_test = []
  test_id_list = []
  for i in xrange(N):
    line = stream.readline()
    line = line.rstrip("\n")
    args = line.split()
    id_str = args[0]
    label = int(args[1])
    feature_pairs = args[2 : ]
    feature_vector = []
    for feature_pair in feature_pairs:
      feature_pair_str_list = feature_pair.split(":")
      feature_index = int(feature_pair_str_list[0])
      feature_value = float(feature_pair_str_list[1])
      feature_vector.append(feature_value)
    X_train.append(feature_vector)
    y_train.append(label)
    train_id_list.append(id_str)
  line = stream.readline()
  line = line.rstrip("\n")
  args = line.split()
  args = [string.atol(x) for x in args]
  q = int(args[0])
  for i in xrange(q):
    line = stream.readline()
    line = line.rstrip("\n")
    args = line.split()
    id_str = args[0]
    feature_pairs = args[1 : ]
    feature_vector = []
    for feature_pair in feature_pairs:
      feature_pair_str_list = feature_pair.split(":")
      feature_index = int(feature_pair_str_list[0])
      feature_value = float(feature_pair_str_list[1])
      feature_vector.append(feature_value)
    X_test.append(feature_vector)
    test_id_list.append(id_str)
  return (X_train, y_train, train_id_list), (X_test, test_id_list)
def splitIndices(n, k):
  indices = range(n)
  return indices[ : k], indices[k : ]
stream = sys.stdin
# stream = open("tests/official/input01.txt")
(X_train, y_train, train_id_list), (X_test, test_id_list) = readInput(stream)
c_set = [0.01]
output_labels = MIRA_train(X_train[ : ], y_train[ : ], X_test[ : ], c_set)
for i in xrange(len(output_labels)):
  line = test_id_list[i] + " " + ("+1" if output_labels[i] == 1 else "-1")
  print line
stream.close()
