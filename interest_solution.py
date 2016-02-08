# 2016-02-07

# we're measuring quality of a question

# use linear SVR and squared epsilon-insensitive loss; 
# use log transform and smoothing for target 
# viewer-follower-ratio values; use capitalized first letter, 
# penalizing for having no word tokens, punctuation ratio, 
# log-transformed number of associated topics, topic-question 
# word overlap to number of question words ratio, 
# word under-/over-shoot, lower-case inquisitive word 
# (who, what, where, when, why, how) inclusion; 
# use question text first word, context topic name, 
# and associated topic name not broken up into words 
# with dictionary vectorizers; use log-transformed 
# associated topic follower count sum; use sparse features 
# and standardization for features not related to one-hot encoding 
# (question text, context topic and associated topic names); 
# we use transduction using k-means clustering 
# cluster identifier values binarized; use f-regression 
# feature selection; solve within 34 seconds 
# and 512 MiB of memory

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
from sklearn.preprocessing import LabelBinarizer

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
  question = obj["question_text"].strip()
  topics = [t["name"] for t in obj["topics"]]
  tokens = [w for w in wordpunct_tokenize(question) if not re.match(r"[\'\"\.\?\!\,\/\\\(\)\`]", w)]
  punct = [p for p in wordpunct_tokenize(question) if re.match(r"[\'\"\.\?\!\,\/\\\(\)\`]", p)]
  top_toks = set([w.lower() for t in obj["topics"] for w in wordpunct_tokenize(t["name"])])
  qn_toks  = set(tokens)
  qn_topic_words = len(top_toks & qn_toks)
  start_cap = 1 if re.match(r"^[A-Z]", question) else 0
  if len(tokens) > 0:
    qn_type = [1 if sum(1.0 for w in tokens if w in qws) else 0 for qws in qn_type_words]
  else:
    # penalize having no token words
    qn_type = [-1.0] * len(qn_type_words)
  total_words = len(tokens)
  correct_form_count = sum(1.0 for w in tokens if (not re.match(r"^[A-Z]+$", w)) or re.match(r"^[A-Z]", w))
  topic_word_ratio1  = max(0, qn_topic_words - 2) / float(total_words + 1)
  topic_word_ratio2  = max(0, 2 - qn_topic_words) / float(total_words + 1)
  topic_word_ratio   = qn_topic_words / float(total_words + 1)
  punctuation_ratio  = len(punct) / float(total_words + 1)
  word_overshoot = max(0, total_words - 10.1)
  word_undershoot = max(0, 10.1 - total_words)
  result = [
    start_cap,
    punctuation_ratio,
    math.log(len(topics) + 1),
    topic_word_ratio1,
    topic_word_ratio2,
    topic_word_ratio,
    word_overshoot,
    word_undershoot,
   ] + qn_type
  return result
def getFirstWordDict(x):
  words = [w.lower() for w in wordpunct_tokenize(x["question_text"])]
  res = {w : 1 for w in words[0 : 1] if len(w) >= 3}
  return res
def getModel(**args):
  formatting = Pipeline([
    ("other", Extractor(getFormattingFeatures)),
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
  topic_question = Pipeline([
    ("content", FeatureUnion([
      ("question", question),
      ("topics", topics),
      ("ctopic", ctopic)
    ])),
  ])
  """
  others = Pipeline([
    ("extract", Extractor(lambda x: [1 if x["anonymous"] else 0])),
    ("scaler",  StandardScaler())
  ])
  """
  followers = Pipeline([
    ("extract", Extractor(lambda x: [math.log(sum(t["followers"] for t in x["topics"]) + args["smoother"])])),
    ("scaler", StandardScaler())
  ])
  k_means = KMeans(n_clusters = 96, random_state = 20, n_init = 3, max_iter = 8, tol = 1e-3)
  label_binarizer = LabelBinarizer(sparse_output = True)
  svr = LinearSVR(C = 0.04, loss = "squared_epsilon_insensitive")
  model = Pipeline([
    ("union", FeatureUnion([
      ("content", topic_question),
      ("formatting", formatting),
      ("followers", followers)
    ])),
    ("union2", FeatureUnion([
      ("transductive", Pipeline([
        ("k_means", PredictTransformer(k_means)),
        ("label_binarizer", OmitTargetTransformer(label_binarizer))
      ])),
      ("pass_through", PassThroughTransformer())
    ])),
    ("f_sel", SelectKBest(score_func = lambda X, y : f_regression(X, y, center = False), k = args["all_K"])),
    ("svr", svr)
  ])
  return model
if __name__ == "__main__":
  stream = sys.stdin
  # stream = open("tests/official/input01.txt")
  training_count = int(stream.next())
  training_data  = [json.loads(stream.next()) for i in xrange(training_count)]
  target = [math.log(obj["__ans__"] + 0.9) for obj in training_data]
  model = getModel(**{"all_K" : 3800, "smoother" : 1, "none_var" : False})
  model.fit(training_data, target)
  test_count = int(stream.next())
  test_data = [json.loads(stream.next()) for i in xrange(test_count)]
  predict = model.predict(test_data)
  for i, j in zip(predict.tolist(), test_data):
    obj = {"__ans__" : math.exp(i) - 0.9, "question_key" : j["question_key"]}
    print json.dumps(obj)

