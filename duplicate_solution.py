# 2016-01-08

# use cosine dissimilarity

# use feature selection

# scipy.sparse hstack, bmat are low-memory use for coo-type matrix in scipy 0.16.1

# inspired by mike koltsov

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import numpy as np
import scipy.sparse as sp
import math
# cosine dissimilarity, which respects sparsity
def getSimilarityMetricValue1(tf_idf_mat1, tf_idf_mat2, row_index):
  tf_idf_arr1 = tf_idf_mat1.toarray()[0]
  tf_idf_arr2 = tf_idf_mat2.toarray()[0]
  dot_product1 = np.dot(tf_idf_arr1, tf_idf_arr2)
  norm1 = np.linalg.norm(tf_idf_arr1)
  norm2 = np.linalg.norm(tf_idf_arr2)
  similarity_metric = None
  if norm1 == 0 or norm2 == 0:
    similarity_metric1 = 1
  else:
    similarity_metric1 = dot_product1 / (1.0 * norm1 * norm2)
  difference = 1.0 - (math.acos(similarity_metric1) / math.pi)
  return [difference]
import re
INTEGER_RE = r'(\d+)'
QUOTED_TEXT_RE = r'"([^"\\]*(?:\\.[^"\\]*)*)"'
KEY_TEXT_RE = QUOTED_TEXT_RE
PAIR_SEPARATOR_RE = r'(?:\s*:\s*)'
SEPARATOR_RE = r'\s*,\s*'
VIEW_COUNT_RE = r'(?:"view_count"' + PAIR_SEPARATOR_RE + INTEGER_RE + r')'
QUESTION_TEXT_RE = r'(?:"question_text"' + PAIR_SEPARATOR_RE + QUOTED_TEXT_RE + r')'
FOLLOWERS_RE = r'(?:"followers"' + PAIR_SEPARATOR_RE + INTEGER_RE + r')'
NAME_RE = r'(?:"name"' + PAIR_SEPARATOR_RE + QUOTED_TEXT_RE + r')'
FOLLOW_COUNT_RE = r'(?:"follow_count"' + PAIR_SEPARATOR_RE + INTEGER_RE + r')'
QUESTION_KEY_RE = r'(?:"question_key"' + PAIR_SEPARATOR_RE + KEY_TEXT_RE + r')'
AGE_RE = r'(?:"age"' + PAIR_SEPARATOR_RE + INTEGER_RE + r')'
TOPIC_COMPONENT_COMPONENT_RE = r'(?:(?:' + FOLLOWERS_RE + r')|(?:' + NAME_RE + r'))'
TOPIC_COMPONENT_RE = r'\{(?:' + TOPIC_COMPONENT_COMPONENT_RE + r'(?:' + SEPARATOR_RE + TOPIC_COMPONENT_COMPONENT_RE + r')*)?\}'
CONTEXT_TOPIC_RE = r'(?:"context_topic"' + PAIR_SEPARATOR_RE + r'(' + TOPIC_COMPONENT_RE + r'|' + r'(null)))'
TOPICS_RE = r'(?:"topics"' + PAIR_SEPARATOR_RE + r'\[(?:' + TOPIC_COMPONENT_RE + r'(?:' + SEPARATOR_RE + TOPIC_COMPONENT_RE + r')*)?\])'
COMPONENT_RE = r'(?:' + VIEW_COUNT_RE + r'|' + QUESTION_TEXT_RE + r'|' + CONTEXT_TOPIC_RE + r'|'  + TOPICS_RE + r'|' + FOLLOW_COUNT_RE + r'|' + QUESTION_KEY_RE + r'|' + AGE_RE + r')'
QUESTION_RE = r'(?:\{(?:' + COMPONENT_RE + r'(?:' + SEPARATOR_RE + COMPONENT_RE + r')*)\})'
QUESTION_KEY = 0
QUESTION_TEXT = 1
TOPICS = 2
VIEW_COUNT = 3
AGE = 4
FOLLOW_COUNT = 5
# CONTEXT_TOPIC = 6
NAME = 0
FOLLOWERS = 1
def parse(line):
  json_dict = [None] * 6
  regex = re.compile(VIEW_COUNT_RE)
  m = regex.search(line)
  key = m.group(1)
  json_dict[VIEW_COUNT] = int(key)
  regex = re.compile(QUESTION_TEXT_RE)
  m = regex.search(line)
  key = m.group(1)
  json_dict[QUESTION_TEXT] = key.decode("unicode_escape")
  # not dealing with context topic
  """
  context_topic_dict = [None] * 2
  regex = re.compile(CONTEXT_TOPIC_RE)
  m = regex.search(line)
  key = m.group(1)
  context_topic_str = key
  if key == "null":
    json_dict[CONTEXT_TOPIC] = None
  else:
    regex = re.compile(NAME_RE)
    m = regex.search(context_topic_str)
    key = m.group(1)
    context_topic_dict[NAME] = key.decode("unicode_escape")
    regex = re.compile(FOLLOWERS_RE)
    m = regex.search(context_topic_str)
    key = m.group(1)
    context_topic_dict[FOLLOWERS] = int(key)
    json_dict[CONTEXT_TOPIC] = context_topic_dict
  """
  regex = re.compile(TOPICS_RE)
  m = regex.search(line)
  key = m.group(0)
  topics_str = key
  regex = re.compile(TOPIC_COMPONENT_RE)
  m = regex.finditer(topics_str)
  key = [curr_m.group(0) for curr_m in m]
  topic_component_str_list = key
  topics = [None] * len(topic_component_str_list)
  for i in xrange(len(topic_component_str_list)):
    topic_component_str = topic_component_str_list[i]
    topic_component = [None] * 2
    regex = re.compile(NAME_RE)
    m = regex.search(topic_component_str)
    key = m.group(1)
    topic_component[NAME] = key.decode("unicode_escape")
    regex = re.compile(FOLLOWERS_RE)
    m = regex.search(topic_component_str)
    key = m.group(1)
    topic_component[FOLLOWERS] = int(key)
    # not appending; pre-allocate space
    # topics.append(topic_component)
    topics[i] = topic_component
  json_dict[TOPICS] = topics
  regex = re.compile(FOLLOW_COUNT_RE)
  m = regex.search(line)
  key = m.group(1)
  json_dict[FOLLOW_COUNT] = int(key)
  regex = re.compile(QUESTION_KEY_RE)
  m = regex.search(line)
  key = m.group(1)
  json_dict[QUESTION_KEY] = key.decode("unicode_escape")
  regex = re.compile(AGE_RE)
  m = regex.search(line)
  key = m.group(1)
  json_dict[AGE] = int(key)
  return json_dict
class JSONObject:
  def __init__(self, json_dict):
    self.json_dict = json_dict
  def get(self, key):
    return (self.json_dict)[key]
import gc
def getQuestionAttributeDictionaries(stream, n):
  questions = []
  for i in xrange(n):
      s = stream.readline()
      question_dict = parse(s)
      questions.append(question_dict)
      del s
  return questions
def getDocuments(questions):
  docs = []
  for i in xrange(len(questions)):
    q = questions[i]
    doc = q[QUESTION_TEXT]
    docs.append(doc)
  topics = set()
  counts = set()
  for q in questions:
      counts.add(q[VIEW_COUNT])
      counts.add(q[FOLLOW_COUNT])
      counts.add(q[AGE])
      for t in q[TOPICS]:
          topics.add(t[NAME])
  docs.extend(list(topics))
  docs.extend(map(str, counts))
  return docs
def getConvertedQuestionDictionary(questions):
  conved = dict()
  for i in xrange(len(questions)):
      q = questions[i]
      topics = sorted(q[TOPICS], key = lambda t: -t[FOLLOWERS])
      topics = ' '.join([t[NAME] for t in topics])
      topics += ' ' + q[QUESTION_TEXT]
      topics += ' ' + str(q[VIEW_COUNT]) + ' ' + str(q[FOLLOW_COUNT]) + ' ' + str(q[AGE])
      conved[q[QUESTION_KEY]] = topics
  return conved
def lowMemoryHStack(c2, c3):
  result_mat = sp.hstack((c2, c3), format = "coo")
  return result_mat
import sys
def main():
  stream = sys.stdin
  # stream = open("tests/official/input00.txt")
  line = stream.readline()
  n = int(line)
  questions = getQuestionAttributeDictionaries(stream, n)
  key_to_question_dict = {}
  for question in questions:
    key = question[QUESTION_KEY]
    key_to_question_dict[key] = question
  gc.collect()
  docs = getDocuments(questions)
  gc.collect()
  vectorizer = TfidfVectorizer(ngram_range = (1, 3), analyzer = 'char', max_df = 0.5, sublinear_tf = True, lowercase = True)
  vectorizer.fit(docs)
  del docs
  question_keys = [q[QUESTION_KEY] for q in questions]
  conved = getConvertedQuestionDictionary(questions)
  del questions
  gc.collect()
  line = stream.readline()
  d = int(line)
  train = []
  pre_train_list1 = np.array([None] * d)
  pre_train_list2 = np.array([None] * d)
  pre_train_bag_list = np.array([None] * d)
  target = []
  questions1 = []
  questions2 = []
  for i in xrange(d):
      line = stream.readline()
      x, y, z = line.split()
      pre_train_bag_list[i] = conved[x] + " " + conved[y]
      pre_train1 = conved[x]
      pre_train2 = conved[y]
      pre_train_list1[i] = pre_train1
      pre_train_list2[i] = pre_train2
      target.append(int(z))
      q1 = key_to_question_dict[x]
      q2 = key_to_question_dict[y]
      questions1.append(q1)
      questions2.append(q2)
  tf_idf_vectors1 = vectorizer.transform(pre_train_list1, copy = False)
  tf_idf_vectors2 = vectorizer.transform(pre_train_list2, copy = False)
  vectors1 = tf_idf_vectors1
  vectors2 = tf_idf_vectors2
  c1 = [getSimilarityMetricValue1(vectors1[x], vectors2[x], x) for x in xrange(vectors1.shape[0])]
  del pre_train_list1
  del pre_train_list2
  del vectors1
  del vectors2
  del tf_idf_vectors1
  del tf_idf_vectors2
  gc.collect()
  tf_idf_bag_vector_list = vectorizer.transform(pre_train_bag_list, copy = False)
  del pre_train_bag_list
  # this could be a csr matrix
  c2 = sp.coo_matrix(tf_idf_bag_vector_list, dtype = "f")
  c3 = c1
  h = lowMemoryHStack(c2, c3)
  del c1, c2, c3
  del tf_idf_bag_vector_list
  gc.collect()
  train = h
  from sklearn.pipeline import Pipeline
  from sklearn.feature_selection import SelectKBest, chi2
  clf = LogisticRegression(C = 2.0)
  # 25,877 features
  selector = SelectKBest(chi2, k=24000)
  clf = Pipeline([('sel', selector), ('logr', clf)])
  model = clf
  model.fit(train, target)
  line = stream.readline()
  need = int(line)
  pred_bag_list = np.array([None] * need)
  pred_list1 = np.array([None] * need)
  pred_list2 = np.array([None] * need)
  legend = []
  questions1 = []
  questions2 = []
  for i in xrange(need):
      line = stream.readline()
      x, y = line.split()
      legend.append((x, y))
      pred_bag_list[i] = conved[x] + " " + conved[y]
      pred1 = conved[x]
      pred2 = conved[y]
      pred_list1[i] = pred1
      pred_list2[i] = pred2
      q1 = key_to_question_dict[x]
      q2 = key_to_question_dict[y]
      questions1.append(q1)
      questions2.append(q2)
  tf_idf_vectors1 = vectorizer.transform(pred_list1, copy = False)
  tf_idf_vectors2 = vectorizer.transform(pred_list2, copy = False)
  del pred_list1
  del pred_list2
  gc.collect()
  vectors1 = tf_idf_vectors1
  vectors2 = tf_idf_vectors2
  tf_idf_bag_vector_list = vectorizer.transform(pred_bag_list, copy = False)
  del pred_bag_list
  c1 = [getSimilarityMetricValue1(vectors1[x], vectors2[x], x) for x in xrange(vectors1.shape[0])]
  del vectors1
  del vectors2
  del tf_idf_vectors1
  del tf_idf_vectors2
  gc.collect()
  c2 = sp.coo_matrix(tf_idf_bag_vector_list, dtype = "f")
  c3 = c1
  h = sp.hstack((c2, c3), format = "coo")
  pred = h
  pred = model.predict(pred)
  del c1, c2, c3
  del tf_idf_bag_vector_list
  gc.collect()
  for i in xrange(need):
      print legend[i][0], legend[i][1], pred[i]
main()
