# 2016-01-08

# for given question text, label using most appropriate topic id values

# multi-label learning

# have up to 250 distinct labels

# use logistic regression with one-versus-rest (also known as binary relevance method)

# use tf-idf metric

# have k-best feature selection using chi-squared test

# filter away topic id values that don't appear for any question

# use word-count over-/under-shooting relative to word count average

# use inquisitive first word existence

# use average word length

# inspired by mike koltsov

import sys, string
from sklearn.pipeline import Pipeline
from sklearn.feature_selection import SelectKBest, chi2
import re
stream = sys.stdin
# stream = open("tests/official/input00.txt")
# stream = open("tests/official/input_a.txt")
line = stream.readline()
line = line.rstrip("\n")
args = line.split()
args = [string.atol(x) for x in args]
T = int(args[0])
E = int(args[1])
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.multiclass import OneVsRestClassifier
import numpy as np
import scipy.sparse as sp
vectorizer1 = TfidfVectorizer(ngram_range = (1, 1), analyzer = 'word', max_df = 0.8, sublinear_tf = False, lowercase = True, norm = None)
questions = []
NUM_LABELS = 250
target = []
seen_topics = set([])
for i in xrange(T):
  question_dict = {}
  line = stream.readline()
  line = line.rstrip("\n")
  args = line.split()
  args = [int(x) for x in args]
  # first value describes how many topic id values we have
  topic_id_list = args[1 : ]
  line = stream.readline()
  line = line.rstrip("\n")
  question_text = line
  question_dict["topic_id_list"] = topic_id_list
  question_dict["question_text"] = question_text
  questions.append(question_dict)
  target.append(topic_id_list)
  seen_topics = seen_topics | set(topic_id_list)
  # print topic_id_list, question_text
seen_topic_list = sorted(list(seen_topics))
unseen_topic_list = [x for x in list(set(xrange(NUM_LABELS))) if x not in seen_topic_list]
# print unseen_topic_list
num_seen_topics = len(seen_topic_list)
topic_id_to_transformed_topic_id_dict = {}
transformed_topic_id_to_topic_id_dict = {}
for i in xrange(num_seen_topics):
  topic_id = seen_topic_list[i]
  transformed_topic_id = i
  topic_id_to_transformed_topic_id_dict[topic_id] = transformed_topic_id
  transformed_topic_id_to_topic_id_dict[transformed_topic_id] = topic_id
  # print topic_vector
next_target = []
for topic_id_list in target:
  topic_vector = [0] * num_seen_topics
  for topic_id in topic_id_list:
    transformed_topic_id = topic_id_to_transformed_topic_id_dict[topic_id]
    topic_vector[transformed_topic_id] = 1
  next_target.append(topic_vector)
next_target = sp.csr_matrix(next_target, dtype='d')
# print target
def getWithoutPunctuation(curr_str):
  PUNCTUATION_RE = r"[^\w ]"
  m = re.compile(PUNCTUATION_RE)
  next_str = m.sub("", curr_str)
  return next_str
def getInLowerCase(curr_str):
  return curr_str.lower()
def getCoarseWords(curr_str):
  next_str = getWithoutPunctuation(getInLowerCase(curr_str))
  words = next_str.split(" ")
  return words
def getDocuments(questions):
  documents = [x["question_text"] for x in questions]
  return documents
docs1 = getDocuments(questions)
vectorizer1.fit(docs1)
mat1 = vectorizer1.transform(docs1)
def getWordCountUnderOvershootMat(reference_questions, questions):
  question_text_list = [x["question_text"] for x in reference_questions]
  word_count_list = [getWordCount(x) for x in question_text_list]
  average_word_count = sum(word_count_list) / (1.0 * len(word_count_list))
  next_question_text_list = [x["question_text"] for x in questions]
  next_word_count_list = [getWordCount(x) for x in next_question_text_list]
  overshoot_values = [max(0, x - average_word_count) for x in next_word_count_list]
  undershoot_values = [max(0, average_word_count - x) for x in next_word_count_list]
  documents = [[undershoot_values[i], overshoot_values[i]] for i in xrange(len(questions))]
  result_mat = sp.csr_matrix(documents)
  return result_mat
def getWordCount(curr_str):
  words = getCoarseWords(curr_str)
  num_words = len(words)
  return num_words
mat3 = getWordCountUnderOvershootMat(questions, questions)
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
# word will be in lower-case
def getFirstWord(curr_str):
  words = getCoarseWords(curr_str)
  first_word = words[0]
  return first_word
def getInquisitiveWordMat(questions):
  question_text_list = [x["question_text"] for x in questions]
  begins_with_inquisitive_word_list = [beginsWithInquisitiveWord(x) for x in question_text_list]
  result_mat = sp.csr_matrix([[x] for x in begins_with_inquisitive_word_list])
  return result_mat
def getAverageWordLength(curr_str):
  words = getCoarseWords(curr_str)
  word_lengths = [len(x) for x in words]
  num_words = len(words)
  return sum(word_lengths) / (1.0 * num_words)
def getAverageWordLengthMat(questions):
  question_text_list = [x["question_text"] for x in questions]
  avg_word_length_list = [getAverageWordLength(x) / (1.0 * 10.25) for x in question_text_list]
  documents = [[x * 2] for x in avg_word_length_list]
  result_mat = sp.csr_matrix(documents)
  return result_mat
mat4 = getInquisitiveWordMat(questions)
mat5 = getAverageWordLengthMat(questions)
# concatenate tf-idf vectorizer output with other feature matrices
mat = sp.hstack((mat1, mat3, mat4, mat5))
from sklearn.preprocessing import normalize
mat = normalize(mat, copy = False)
train = mat
clf = LogisticRegression(C = 5.0)
# 14,426 features
selector = SelectKBest(chi2, k=14400)
clf = Pipeline([('sel', selector), ('logr', clf)])
clf = OneVsRestClassifier(clf)
model = clf
model.fit(train, next_target)
test_questions = []
for i in xrange(E):
  question_dict = {}
  line = stream.readline()
  line = line.rstrip("\n")
  question_text = line
  # print question_text
  question_dict["question_text"] = question_text
  test_questions.append(question_dict)
test_docs = getDocuments(test_questions)
mat1 = vectorizer1.transform(test_docs)
mat3 = getWordCountUnderOvershootMat(questions, test_questions)
mat4 = getInquisitiveWordMat(test_questions)
mat5 = getAverageWordLengthMat(test_questions)
mat = sp.hstack((mat1, mat3, mat4, mat5))
mat = normalize(mat, copy = False)
test = mat
pred = model.predict_proba(test)
for topic_prob_vector in pred:
  topic_prob_list = list(topic_prob_vector)
  transformed_topic_id_prob_pair_list = [(i, topic_prob_list[i]) for i in xrange(len(topic_prob_list))]
  # print transformed_topic_id_prob_pair_list
  prob_sorted_transformed_topic_id_prob_pair_list = sorted(transformed_topic_id_prob_pair_list, key = lambda x: x[1], reverse = True)
  # print prob_sorted_transformed_topic_id_prob_pair_list
  prob_sorted_transformed_topic_id_list = [x[0] for x in prob_sorted_transformed_topic_id_prob_pair_list]
  culled_transformed_topic_id_list = prob_sorted_transformed_topic_id_list[ : 10]
  culled_topic_id_list = [transformed_topic_id_to_topic_id_dict[x] for x in culled_transformed_topic_id_list]
  topic_id_str_list = [str(x) for x in culled_topic_id_list]
  # topic_id_str_list = topic_id_str_list[0 : 2]
  topic_id_str_list = [topic_id_str_list[0]]
  topic_id_str = string.join(topic_id_str_list, " ")
  # print culled_topic_id_list
  print topic_id_str
