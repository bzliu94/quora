# 2016-01-27

# use logistic regression, tf-idf without idf and with word {1, 2}-grams, 
# anonymous author, number of context and associated topics that pass 
# certain thresholds for popularity, non-negative word under-/over-shoot, 
# inquisitive first word (who, what, where, when, why) existence, 
# existence of at least one fully capitalized word with at least two characters, 
# average word length; use transductive learning by way of fixed-seed 
# k-means clustering; use feature reduction using a chi-squared test

# inspired by tao xu and gurupad hegde

import json
import string
import re
import math
import sys
import scipy.sparse as sp
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.feature_selection import SelectKBest, chi2
from sklearn.preprocessing import normalize
from sklearn.cluster import KMeans
from sklearn.preprocessing import LabelBinarizer

def getInLowerCase(curr_str):
  return curr_str.lower()
def getWithoutPunctuation(curr_str):
  PUNCTUATION_RE = r"[^\w ]"
  m = re.compile(PUNCTUATION_RE)
  next_str = m.sub("", curr_str)
  return next_str
def getPunctuationRatio(curr_str):
  next_str = getWithoutSpaces(curr_str)
  PUNCTUATION_RE = r"\W"
  m = re.compile(PUNCTUATION_RE)
  matches = m.findall(next_str)
  num_matches = len(matches)
  num_punctuation_chars = num_matches
  num_non_space_chars = getNumNonSpaces(curr_str)
  punctuation_ratio = num_punctuation_chars / (1.0 * num_non_space_chars)
  return punctuation_ratio
def getCapitalizationRatio(curr_str):
  next_str = getWithoutSpaces(curr_str)
  char_list = list(next_str)
  capital_char_list = [x for x in char_list if x.isupper() == True]
  num_capital_chars = len(capital_char_list)
  num_non_space_chars = getNumNonSpaces(curr_str)
  capitalization_ratio = num_capital_chars / (1.0 * num_non_space_chars)
  return capitalization_ratio
def getWithoutSpaces(curr_str):
  char_list = list(curr_str)
  next_char_list = [x for x in char_list if x != " "]
  next_str = string.join(next_char_list, "")
  return next_str
def getNumNonSpaces(curr_str):
  char_list = list(curr_str)
  num_spaces = len([x for x in char_list if x != " "])
  return num_spaces
def getCoarseWords(curr_str, in_lower_case = True):
  next_str = curr_str
  if in_lower_case == True:
    next_str = getInLowerCase(next_str)
  next_str = getWithoutPunctuation(next_str)
  words = next_str.split(" ")
  return words
def getAverageWordLength(curr_str):
  words = getCoarseWords(curr_str)
  word_lengths = [len(x) for x in words]
  num_words = len(words)
  return sum(word_lengths) / (1.0 * num_words)
def isPrefix(word, original_word):
  result = original_word.find(word)
  is_prefix = result == 0
  return is_prefix
def beginsWithInquisitiveWord(curr_str):
  first_word = getFirstWord(curr_str)
  does_begin_with_inquisitive_word = False
  inquisitive_words = ["who", "what", "where", "when", "why", "how"]
  matching_words = [x for x in inquisitive_words if isPrefix(x, first_word) == True]
  num_matching_words = len(matching_words)
  return num_matching_words != 0
def getFirstWord(curr_str):
  words = getCoarseWords(curr_str)
  first_word = words[0]
  return first_word
def getAverageWordCount(questions):
  question_text_list = [x[QUESTION_TEXT] for x in questions]
  word_count_list = [getWordCount(x) for x in question_text_list]
  avg_word_count = sum(word_count_list) / (1.0 * len(word_count_list))
  return avg_word_count
def getAverageWordLengthMat(questions):
  question_text_list = [x[QUESTION_TEXT] for x in questions]
  avg_word_length_list = [getAverageWordLength(x) / (1.0 * 113) for x in question_text_list]
  documents = [[x] for x in avg_word_length_list]
  result_mat = sp.csr_matrix(documents)
  return result_mat
def getWordCountUnderOvershootMat(avg_word_count, questions):
  next_question_text_list = [x[QUESTION_TEXT] for x in questions]
  next_word_count_list = [getWordCount(x) for x in next_question_text_list]
  overshoot_values = [max(0, x - avg_word_count) for x in next_word_count_list]
  undershoot_values = [max(0, avg_word_count - x) for x in next_word_count_list]
  documents = [[undershoot_values[i], overshoot_values[i]] for i in xrange(len(questions))]
  result_mat = sp.csr_matrix(documents)
  return result_mat
def getWordCount(curr_str):
  words = getCoarseWords(curr_str)
  num_words = len(words)
  return num_words
def getInquisitiveWordMat(questions):
  question_text_list = [x[QUESTION_TEXT] for x in questions]
  begins_with_inquisitive_word_list = [beginsWithInquisitiveWord(x) for x in question_text_list]
  result_mat = sp.csr_matrix([[x] for x in begins_with_inquisitive_word_list])
  return result_mat
def getHaveCapitalizedWordsMat(questions):
  question_text_list = [x[QUESTION_TEXT] for x in questions]
  have_capitalized_words = []
  for question_text in question_text_list:
    words = [x for x in getCoarseWords(question_text, False) if len(x) >= 2]
    is_cap_list = [x.isupper() for x in words]
    have_cap_word = None
    if True in is_cap_list:
      have_cap_word = True
    else:
      have_cap_word = False
    have_capitalized_words.append(have_cap_word)
  result_mat = sp.csr_matrix([[x] for x in have_capitalized_words])
  return result_mat
def getUnusualWordMat(questions):
  question_text_list = [x[QUESTION_TEXT] for x in questions]
  words = ["aashiqui"]
QUESTION_KEY = 0
QUESTION_TEXT = 1
CONTEXT_TOPIC = 2
TOPICS = 3
ANONYMOUS = 4
ANS = 5
NAME = 0
FOLLOWERS = 1
def getQuestionAttributeDictionaries(stream, n):
  questions = []
  for i in xrange(n):
      s = stream.readline()
      question_json = json.loads(s)
      question = {}
      question[QUESTION_KEY] = question_json.get("question_key")
      question[QUESTION_TEXT] = question_json.get("question_text")
      context_topic_json = question_json.get("context_topic")
      if context_topic_json != None:
        context_topic = {}
        context_topic[NAME] = context_topic_json.get("name")
        context_topic[FOLLOWERS] = context_topic_json.get("followers")
        question[CONTEXT_TOPIC] = context_topic
      else:
        question[CONTEXT_TOPIC] = None
      topic_json_list = question_json.get("topics")
      topics = []
      for topic_json in topic_json_list:
        topic = {}
        topic[NAME] = topic_json.get("name")
        topic[FOLLOWERS] = topic_json.get("followers")
        topics.append(topic)
        del topic_json
      question[TOPICS] = topics
      question[ANONYMOUS] = question_json.get("anonymous")
      question[ANS] = question_json.get("__ans__")
      questions.append(question)
  return questions
def getDocuments(questions):
  docs = []
  for i in xrange(len(questions)):
    q = questions[i]
    doc = q[QUESTION_TEXT]
    for t in q[TOPICS]:
        doc += ' ' + t[NAME]
    if q[CONTEXT_TOPIC] != None:
        doc += ' ' + q[CONTEXT_TOPIC][NAME]
    docs.append(doc)
  return docs
def getConvertedQuestionDictionary(questions):
  docs = getDocuments(questions)
  conved = {}
  for i in xrange(len(questions)):
    doc = docs[i]
    question = questions[i]
    key = question[QUESTION_KEY]
    conved[key] = doc
  return conved
def getAnonymousAuthorMat(questions):
  documents = []
  for question in questions:
    val = question[ANONYMOUS]
    next_val = 1 if val == True else 0
    next_next_val = 0 if val == True else 1
    documents.append([next_val, next_next_val])
  mat = sp.csr_matrix(documents)
  return mat
def getTopicPopularityMat(questions):
  documents = []
  for question in questions:
    context_topic_dict = question[CONTEXT_TOPIC]
    associated_topic_dict_list = question[TOPICS]
    context_topic_flag = 0
    associated_topic_flag = 0
    follower_sum1 = 0
    if context_topic_dict != None:
      num_followers = context_topic_dict[FOLLOWERS]
      if num_followers > 550:
        context_topic_flag = 1
      follower_sum1 += num_followers
    for topic_dict in associated_topic_dict_list:
      num_followers = topic_dict[FOLLOWERS]
      if num_followers > 1100:
        associated_topic_flag += 1
    transformed_follower_sum1 = follower_sum1 / (1.0 * 4023302)
    documents.append([context_topic_flag, associated_topic_flag, transformed_follower_sum1])
  mat = sp.csr_matrix(documents)
  return mat
stream = sys.stdin
# stream = open("tests/official/input01.txt")
line = stream.readline()
n = int(line)
train_questions = getQuestionAttributeDictionaries(stream, n)
docs = getDocuments(train_questions)
vectorizer = TfidfVectorizer(ngram_range = (1, 2), analyzer = 'word', max_df = 1.0, sublinear_tf = True, lowercase = True, use_idf = False, norm = None)
vectorizer.fit(docs)
conved = getConvertedQuestionDictionary(train_questions)
train_bag_list = [conved[x[QUESTION_KEY]] for x in train_questions]
train_bag_vector_list = vectorizer.transform(train_bag_list)
mat2 = getAnonymousAuthorMat(train_questions)
mat3 = getTopicPopularityMat(train_questions)
avg_word_count = getAverageWordCount(train_questions)
mat4 = getWordCountUnderOvershootMat(avg_word_count, train_questions)
mat5 = getInquisitiveWordMat(train_questions)
mat6 = getHaveCapitalizedWordsMat(train_questions)
mat7 = getAverageWordLengthMat(train_questions)
mat1 = sp.coo_matrix(train_bag_vector_list, dtype = "f")
mat = sp.hstack((mat1, mat2, mat3, mat4, mat5, mat6, mat7))
train = mat
target = [q[ANS] for q in train_questions]
line = stream.readline()
T = int(line)
test_questions = getQuestionAttributeDictionaries(stream, T)
next_conved = getConvertedQuestionDictionary(test_questions)
test_bag_list = [next_conved[x[QUESTION_KEY]] for x in test_questions]
test_bag_vector_list = vectorizer.transform(test_bag_list)
mat2 = getAnonymousAuthorMat(test_questions)
mat3 = getTopicPopularityMat(test_questions)
mat4 = getWordCountUnderOvershootMat(avg_word_count, test_questions)
mat5 = getInquisitiveWordMat(test_questions)
mat6 = getHaveCapitalizedWordsMat(test_questions)
mat7 = getAverageWordLengthMat(test_questions)
mat1 = sp.coo_matrix(test_bag_vector_list, dtype = "f")
mat = sp.hstack((mat1, mat2, mat3, mat4, mat5, mat6, mat7))
test = mat
# 65.16%
kmeans = KMeans(n_clusters = 12, random_state = 121, n_init = 4, max_iter = 32, tol = 1e-3)
combined_mat = sp.vstack((train, test))
selector2 = SelectKBest(chi2, k = min(38100, mat.shape[1]))
selector2.fit(train, target)
next_combined_mat = selector2.transform(combined_mat)
cluster_labels = kmeans.fit_predict(next_combined_mat)
label_binarizer = LabelBinarizer(sparse_output = True)
binarized_cluster_labels = label_binarizer.fit_transform(cluster_labels)
bcl1 = binarized_cluster_labels[0 : n]
bcl1 = normalize(bcl1, copy = False)
bcl2 = binarized_cluster_labels[n : n + T]
bcl2 = normalize(bcl2, copy = False)
next_train = sp.hstack((train, bcl1))
next_test = sp.hstack((test, bcl2))
next_train = normalize(next_train, copy = False)
next_test = normalize(next_test, copy = False)
clf = LogisticRegression(C = 0.6)
selector = SelectKBest(chi2, k = min(381012, mat.shape[1]))
clf = Pipeline([('sel', selector), ('logr', clf)])
model = clf
model.fit(next_train, target)
pred = model.predict(next_test)
for i in xrange(T):
  curr_dict = {}
  curr_question = test_questions[i]
  curr_dict["question_key"] = curr_question[QUESTION_KEY]
  curr_dict["__ans__"] = bool(pred[i])
  print json.dumps(curr_dict)
