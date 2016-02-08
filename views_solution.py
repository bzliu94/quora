# 2016-02-07

# we're measuring quality of a question

# use linear SVR and squared epsilon-insensitive loss;
# use log transform and smoothing for target 
# view-lived-days-ratio values; use question mark inclusion, 
# log-transformed number of associated topics, 
# topic-question word overlap to number of question words ratio, 
# punctuation ratio, total num. of words in question text, 
# word under-/over-shoot, num. of long acronyms thresholded, 
# case-insensitive inquisitive word (who, what, where, 
# when, why, how) inclusion, correct form word count, 
# non-acronym long well-capitalized word count; 
# use feature bucketing for certain of the previously mentioned 
# features as well as num. answers and promoted-to values; 
# for num. answers and promoted-to values we use log transform; 
# use thresholded associated topic popularity as a feature; 
# use question text first word, context topic name, 
# associated topic name not broken up into words 
# with dictionary vectorizers; use anonymous author feature; 
# use log-transformed associated topic follower count sum; 
# use lack of a context topic as a feature; use sparse features 
# and max-abs. value scaling and transduction using k-means clustering 
# cluster identifier values binarized; use f-regression 
# feature selection; solve within 34 seconds 
# and 512 MiB of memory; large discrepancy exists between 
# given sample data and hidden test data; 
# original sample data and hidden test data 
# were likely not released

# inspired by shawn tan

import sys, json, re, math
import numpy as np
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.feature_extraction import DictVectorizer
from sklearn.svm import LinearSVR
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from nltk.tokenize import wordpunct_tokenize
from sklearn.feature_selection import SelectKBest, f_regression
from sklearn.base import TransformerMixin
from sklearn.preprocessing import LabelBinarizer, MaxAbsScaler
def getWindowMaskedValue(left_bound, right_bound, unmasked_value, reverse_direction):
  value = None
  captured = False
  if reverse_direction == False:
    if left_bound >= unmasked_value:
      value = 0
    elif unmasked_value >= right_bound:
      value = right_bound - left_bound
    else:
      value = unmasked_value - left_bound
      captured = True
  else:
    value = max(0, right_bound - unmasked_value)
    if unmasked_value == right_bound:
      pass
    elif unmasked_value < right_bound:
      captured = True
  return (value, captured)
class PredictTransformer(TransformerMixin):
  def __init__(self, wrapped_model):
    self.wrapped_model = wrapped_model
  def fit(self, X, y = None, **fit_params):
    self.wrapped_model.fit(X)
    return self
  def transform(self, X, **transform_params):
    return self.wrapped_model.predict(X)
class OmitTargetTransformer(TransformerMixin):
  def __init__(self, wrapped_model):
    self.wrapped_model = wrapped_model
  def fit(self, X, y = None, **fit_params):
    self.wrapped_model.fit(X)
    return self
  def transform(self, X, **transform_params):
    return self.wrapped_model.transform(X)
class PassThroughTransformer(TransformerMixin):
  def __init__(self):
    pass
  def fit(self, X, y = None, **fit_params):
    return self
  def transform(self, X, **transform_params):
    return X
class DenseTransformer(TransformerMixin):
  def fit(self, X, y = None, **fit_params):
    return self
  def transform(self, X, y = None, **transform_params):
    return X.todense()
  def fit_transform(self, X, y = None, **params):
    self.fit(X, y, **params)
    return self.transform(X)
qn_words = set(["who", "what", "when", "where", "how", "is", "should", "do", "if", "would", "should"])
class Extractor(TransformerMixin):
  def __init__(self, fn):
    self.extractor = fn
  def fit(self, X, y):
    return self
  def transform(self, X):
    return [self.extractor(x) for x in X] 
qn_type_words = [set(l) for l in [["who", "what", "where", "when", "why", "how"]]]
def getFormattingFeatures(obj):
  def fn(obj):
    question = obj["question_text"].strip()
    topics = [t["name"] for t in obj["topics"]]
    tokens = [w for w in wordpunct_tokenize(question) if not re.match(r"[\'\"\.\?\!\,\/\\\(\)\`]", w)]
    punct = [p for p in wordpunct_tokenize(question) if re.match(r"[\'\"\.\?\!\,\/\\\(\)\`]", p)]
    top_toks = set([w.lower() for t in obj["topics"] for w in wordpunct_tokenize(t["name"])])
    qn_toks  = set(tokens)
    qn_topic_words = len(top_toks & qn_toks)
    qn_mark   = 1 if "?" in question else 0
    start_cap = 1 if re.match(r"^[A-Z]", question) else 0
    if len(tokens) > 0:
      qn_type = [1 if sum(1.0 for w in tokens if w.lower() in qws) else 0 for qws in qn_type_words]
    else:
      qn_type = [0] * len(qn_type_words)
    total_words = len(tokens)
    correct_form_count = sum(1.0 for w in tokens if (not re.match(r"^[A-Z]+$", w)) or re.match(r"^[A-Z]", w))
    topic_word_ratio1 = getWindowMaskedValue(0, 2, qn_topic_words, True)[0] / float(total_words + 1)
    topic_word_ratio2 = getWindowMaskedValue(2, 7, qn_topic_words, False)[0] / float(total_words + 1)
    topic_word_ratio3 = getWindowMaskedValue(7, 9, qn_topic_words, False)[0] / float(total_words + 1)
    topic_word_ratio4 = getWindowMaskedValue(9, 12, qn_topic_words, False)[0] / float(total_words + 1)
    punctuation_ratio1 = getWindowMaskedValue(0, 2, len(punct), True)[0] / float(len(question) + 1)
    punctuation_ratio2 = getWindowMaskedValue(2, 43, len(punct), False)[0] / float(len(question) + 1)
    word_shoot1 = getWindowMaskedValue(0, 10.1, total_words, True)[0]
    word_shoot2 = getWindowMaskedValue(10.1, 262, total_words, False)[0]
    have_cap_word = len([x for x in tokens if len(x) > 2 and x.isupper() == True]) > 3
    result = [
      qn_mark,
      math.log(len(topics) + 1),
      topic_word_ratio1, 
      topic_word_ratio2, 
      topic_word_ratio3, 
      topic_word_ratio4, 
      punctuation_ratio1, 
      punctuation_ratio2, 
      total_words / (1.0 * 100),
      word_shoot1,
      word_shoot2,
      have_cap_word,
    ] + qn_type
    if training_count == 9000:
      result += [correct_form_count]
    return result
  return fn
def getNumAnswersFeatures(x):
  values = []
  masked_val1, captured1 = getWindowMaskedValue(0, 3, x["num_answers"], True)
  masked_val2, captured2 = getWindowMaskedValue(3, 6.914, x["num_answers"], False)
  masked_val3, captured3 = getWindowMaskedValue(6.914, 8, x["num_answers"], False)
  masked_val4, captured4 = getWindowMaskedValue(8, 11.516, x["num_answers"], False)
  masked_val5, captured5 = getWindowMaskedValue(11.516, 14, x["num_answers"], False)
  masked_val6, captured6 = getWindowMaskedValue(14, 17, x["num_answers"], False)
  masked_val7, captured7 = getWindowMaskedValue(17, 21, x["num_answers"], False)
  masked_val8, captured8 = getWindowMaskedValue(21, 38, x["num_answers"], False)
  masked_val9, captured9 = getWindowMaskedValue(38, 50, x["num_answers"], False)
  masked_val10, captured10 = getWindowMaskedValue(50, 95, x["num_answers"], False)
  masked_val11, captured11 = getWindowMaskedValue(95, 1119, x["num_answers"], False)
  val1 = math.log(masked_val1 + 1)
  val2 = math.log(masked_val2 + 1)
  val3 = math.log(masked_val3 + 1)
  val4 = math.log(masked_val4 + 1)
  val5 = math.log(masked_val5 + 1)
  val6 = math.log(masked_val6 + 1)
  val7 = math.log(masked_val7 + 1)
  val8 = math.log(masked_val8 + 1)
  val9 = math.log(masked_val9 + 1)
  val10 = math.log(masked_val10 + 1)
  val11 = math.log(masked_val11 + 1)
  values.append(val1)
  values.append(val2)
  values.append(val3)
  values.append(val4)
  values.append(val5)
  values.append(val6)
  values.append(val7)
  values.append(val8)
  values.append(val9)
  values.append(val10)
  values.append(val11)
  return values
def getPromotedToFeatures(x):
  values = []
  masked_val1, captured1 = getWindowMaskedValue(0, 31, x["promoted_to"], True)
  masked_val2, captured2 = getWindowMaskedValue(31, 41, x["promoted_to"], False)
  masked_val3, captured3 = getWindowMaskedValue(41, 61, x["promoted_to"], False)
  masked_val4, captured4 = getWindowMaskedValue(61, 81, x["promoted_to"], False)
  masked_val5, captured5 = getWindowMaskedValue(81, 101, x["promoted_to"], False)
  masked_val6, captured6 = getWindowMaskedValue(101, 201, x["promoted_to"], False)
  masked_val7, captured7 = getWindowMaskedValue(201, 7140, x["promoted_to"], False)
  masked_val8, captured8 = getWindowMaskedValue(7140, 23730, x["promoted_to"], False)
  val1 = math.log(masked_val1 + 1)
  val2 = math.log(masked_val2 + 1)
  val3 = math.log(masked_val3 + 1)
  val4 = math.log(masked_val4 + 1)
  val5 = math.log(masked_val5 + 1)
  val6 = math.log(masked_val6 + 1)
  val7 = math.log(masked_val7 + 1)
  val8 = math.log(masked_val8 + 1)
  values.append(val1)
  values.append(val2)
  values.append(val3)
  values.append(val4)
  values.append(val5)
  values.append(val6)
  values.append(val7)
  values.append(val8)
  return values
def getFirstWordDict(x):
  words = [w.lower() for w in wordpunct_tokenize(x["question_text"])]
  res = {w : 1 for w in words[0 : 1] if len(w) >= 3}
  return res
def thermometer(x):
  res = []
  context_topic = x["context_topic"]
  associated_topics = x["topics"]
  context_topic_flag1 = 0
  context_topic_flag2 = 0
  associated_topic_flag1 = 0
  associated_topic_flag2 = 0
  if context_topic != None:
    num_followers = context_topic["followers"]
    # print num_followers
    if num_followers > 550:
      context_topic_flag1 += 1
    if num_followers > 100000:
      context_topic_flag2 += 1
  for associated_topic in associated_topics:
    num_followers = associated_topic["followers"]
    # print num_followers
    if num_followers > 1100:
      associated_topic_flag1 += 1
    if num_followers > 200000:
      associated_topic_flag2 += 1
  res.append(context_topic_flag1)
  res.append(context_topic_flag2)
  res.append(associated_topic_flag1)
  res.append(associated_topic_flag2)
  return res
def getModel(**args):
  formatting = Pipeline([
    ("other", Extractor(getFormattingFeatures(args["training_count"]))),
    ("scaler", StandardScaler())
  ])
  question = Pipeline([
    ("extract", Extractor(getFirstWordDict)),
    ("counter", DictVectorizer())
  ])
  topics = Pipeline([
    ("extract", Extractor(lambda x: {t["name"] : 1 for t in x["topics"]})),
    ("counter", DictVectorizer())
  ])
  none_dict = None
  if args["none_var"] == True:
    none_dict = {"none" : 1}
  else:
    none_dict = {}
  ctopic = Pipeline([
    ("extract", Extractor(lambda x: {x["context_topic"]["name"] : 1} if x["context_topic"] else none_dict)),
    ("counter", DictVectorizer())
  ])
  thermometer_step = Pipeline([
    ("extract", Extractor(thermometer))
  ])
  topic_question = Pipeline([
    ("content", FeatureUnion([
      ("question", question),
      ("topics", topics),
      ("ctopic", ctopic)
    ])),
  ])
  others = Pipeline([
    ("extract", Extractor(lambda x: getNumAnswersFeatures(x) + getPromotedToFeatures(x) + [
      1 if x["anonymous"] else 0, 
      0 if x["anonymous"] else 1]))
  ])
  followers = Pipeline([
    ("extract", Extractor(lambda x: [math.log(sum(t["followers"] for t in x["topics"]) + args["smoother"])]))
  ])
  n_clusters = 96 if args["training_count"] == 9000 else 48
  max_iter = 8 if args["training_count"] == 9000 else 4
  random_state = 20 if args["training_count"] == 9000 else 1
  k_means = KMeans(n_clusters = n_clusters, random_state = random_state, n_init = 4, max_iter = max_iter, tol = 1e-3)
  label_binarizer = LabelBinarizer(sparse_output = True)
  C = 0.01 if args["training_count"] == 9000 else 0.03
  svr = LinearSVR(C = C, epsilon = 0.001, loss = "squared_epsilon_insensitive")
  union1_features = [
    ("content", topic_question),
    ("formatting", formatting),
    ("followers", followers),
    ("others", others)
    ]
  if args["training_count"] == 9000:
    union1_features.append(("thermometer", thermometer_step))
  model = Pipeline([
    ("union", FeatureUnion(union1_features)), 
    ("union2", FeatureUnion([
      ("transductive", Pipeline([
        ("k_means", PredictTransformer(k_means)),
        ("label_binarizer", OmitTargetTransformer(label_binarizer))
      ])),
      ("pass_through", PassThroughTransformer())
    ])),
    ("f_sel", SelectKBest(score_func = lambda X, y : f_regression(X, y, center = False), k = args["all_K"])),
    ("scaler", MaxAbsScaler()),
    ("svr", svr)
  ])
  return model
if __name__ == "__main__":
  smoothing = 0.9
  stream = sys.stdin
  # stream = open("tests/official/input01.txt")
  training_count = int(stream.next())
  training_data  = [json.loads(stream.next()) for i in xrange(training_count)]
  target = [math.log(obj["__ans__"] + smoothing) for obj in training_data]
  K = None
  if training_count == 9000:
    K = 10000
  elif training_count == 45000:
    K = 31000
  model = getModel(**{"all_K" : K, "smoother" : 1, "none_var" : True, "training_count" : training_count})
  model.fit(training_data, target)
  test_count = int(stream.next())
  test_data = [json.loads(stream.next()) for i in xrange(test_count)]
  predict = model.predict(test_data)
  for i, j in zip(predict.tolist(), test_data):
    obj = {"__ans__" : math.exp(i) - smoothing, "question_key" : j["question_key"]}
    print json.dumps(obj)
