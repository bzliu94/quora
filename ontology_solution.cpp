// 2015-11-02

/*

have a binary persistent tree

have O(M) trees, have O(N) items per tree

have a d-ary topic tree and have a binary topic tree made to be balanced

don't explicitly store prefixes

phase #1

- takes O(N) time

- determine a tour-enter value and a tour-leave value for all topics in O(N) time
by using "euler tour technique" (i.e. use pre-order values) for tree

phase #2

- takes O(M * log(M)) time

- create a collection of questions sorted by question string in O(M * log(M)) time

phase #3

- takes O(N + M * log(N)) time

- create initial tree with zero as values for all topics in O(N) time

- create an additional version of persistent tree by considering question_0 to question_i in O(M * log(N)) time

- meanwhile, modifying and memoizing counts for a topic for a version of persistent tree using topic for current question (during modify())

query phase

- takes O(K * log(N)) time

- find start and end index for query string using lower_bound() in O(log(N)) time

- traverse appropriate tree to get sum of in-group item count values in O(log(N)) time

- take difference of sums associated with at query string and after query string and output

- an option for sum() is to have it take O(log(N)) time for each call as it involves finding interior and two boundaries; for interior, memoized sum is used, and this case can be considered to take O(1) time for each level that the interior can be found on; the two boundaries follow paths that take O(log(N)) time to traverse

overall:

- takes O(N + M * (log(M) + log(N)) + K * log(N)) time

*/

// no parent pointers for binary tree to simplify persistent aspect of tree

// uses a persistent tree

// avoid using new/delete

// inspired by vova bondar

#ifndef QSTIPCOMPARE_H_
#define QSTIPCOMPARE_H_
#include <tuple>
#include <iostream>
namespace ontology {
typedef std::tuple<std::string, int> QSTIP;
class QSTIPCompare {
public:
 bool operator()(QSTIP &qstip1, QSTIP &qstip2);
 static int compare(QSTIP &qstip1, QSTIP &qstip2);
protected:
 QSTIPCompare();
 virtual ~QSTIPCompare();
};
}
#endif
#ifndef PREORDERNODECOUNTCONTAINER_H_
#define PREORDERNODECOUNTCONTAINER_H_
namespace ontology {
class PreorderNodeCountContainer {
public:
 int count;
 PreorderNodeCountContainer(int count);
 int getCount();
 void setCount(int count);
 virtual ~PreorderNodeCountContainer();
};
}
#endif
#ifndef UTIL_H_
#define UTIL_H_
#include <unordered_map>
#include <string>
#include <deque>
#include <stack>
#include <vector>
#include <sstream>
#include <iostream>
namespace ontology {
typedef int BT_ID;
typedef int BTN_ID;
typedef int DAT_ID;
typedef int DATN_ID;
typedef int N_ID;
typedef int Topic_ID;
typedef int Question_ID;
typedef int T_ID;
typedef std::tuple<BTN_ID, bool, int, int, bool> build_tuple;
typedef std::tuple<int, int, int, BTN_ID,
  BTN_ID, int, bool, bool> modify_tuple_a;
typedef std::tuple<BTN_ID> modify_tuple_b;
typedef std::tuple<DATN_ID, bool> explore_tuple;
typedef std::unordered_map<std::string, Topic_ID> NTTID;
typedef std::pair<std::string, Topic_ID> query_str_topic_pair;
class Util {
public:
 static int lowerBound(std::vector<QSTIP> &items, QSTIP &value);
 static std::vector<std::string> split(std::string &line);
 static std::string join(std::vector<std::string> &parts);
protected:
 Util();
 static int lowerBoundHelper(std::vector<QSTIP> &items,
   int l, int r, QSTIP &value);
 static int distance(int l, int r);
 virtual ~Util();
};
}
#endif
#ifndef ITEMCONTAINER_H_
#define ITEMCONTAINER_H_
#include <vector>
namespace ontology {
class BinaryTree;
class BinaryTreeNode;
class DAryTree;
class DAryTreeNode;
class Topic;
class Question;
class ItemContainer {
public:
 std::vector<BinaryTreeNode> *btn_id_to_btn_vec;
 std::vector<Topic> *topic_id_to_topic_vec;
 std::vector<Question> *question_id_to_question_vec;
 std::vector<DAryTreeNode> *datn_id_to_datn_vec;
 std::vector<BinaryTree> *bt_id_to_bt_vec;
 std::vector<DAryTree> *dat_id_to_dat_vec;
 NTTID *name_to_topic_id_dict;
 std::vector<BinaryTreeNode> *getBTNIDToBTNVec();
 std::vector<Topic> *getTopicIDToTopicVec();
 std::vector<Question> *getQuestionIDToQuestionVec();
 std::vector<DAryTreeNode> *getDATNIDToDATNVec();
 std::vector<BinaryTree> *getBTIDToBTVec();
 std::vector<DAryTree> *getDATIDToDATVec();
 NTTID *getNameToTopicIDDict();
 ItemContainer(std::vector<BinaryTreeNode> *btn_id_to_btn_vec,
   std::vector<Topic> *topic_id_to_topic_vec,
   std::vector<Question> *question_id_to_question_vec,
   std::vector<DAryTreeNode> *datn_id_to_datn_vec,
   std::vector<BinaryTree> *bt_id_to_bt_vec,
   std::vector<DAryTree> *dat_id_to_dat_vec,
   NTTID *name_to_topic_id_dict);
 virtual ~ItemContainer();
};
}
#endif
#ifndef QUESTIONCOMPARE_H_
#define QUESTIONCOMPARE_H_
namespace ontology {
class ItemContainer;
class QuestionCompare {
public:
 ItemContainer *item_container;
 QuestionCompare(ItemContainer *item_container);
 bool operator()(Question_ID q_id1, Question_ID q_id2);
 virtual ~QuestionCompare();
protected:
 ItemContainer *getItemContainer();
};
}
#endif
#ifndef QUESTION_H_
#define QUESTION_H_
#include <string>
namespace ontology {
class Question {
public:
 Topic_ID topic_id;
 Question_ID id;
 std::string question_str;
 Question(Topic_ID topic, Question_ID id, std::string question_str);
 Topic_ID getTopic();
 std::string getQuestionString();
 Question_ID getID();
 virtual ~Question();
};
}
#endif
#ifndef NODE_H_
#define NODE_H_
#include <string>
namespace ontology {
template <typename E>
class Node {
public:
 E element;
 int nilb, nirb;
 Node(E element, int nilb, int nirb);
 E getElement();
 void setNodeIndexLeftBoundary(int value);
 void setNodeIndexRightBoundary(int value);
 int getNodeIndexLeftBoundary();
 int getNodeIndexRightBoundary();
 virtual std::vector<N_ID> getChildren();
 virtual std::string toString();
 virtual ~Node();
};
}
#endif
#ifndef NODE_T_H_
#define NODE_T_H_
namespace ontology {
template <typename E>
Node<E>::Node(E element, int nilb, int nirb) {
 this->element = element;
 this->nilb = nilb;
 this->nirb = nirb;
}
template <typename E>
E Node<E>::getElement() {
 return this->element;
}
template <typename E>
void Node<E>::setNodeIndexLeftBoundary(int value) {
 this->nilb = value;
}
template <typename E>
void Node<E>::setNodeIndexRightBoundary(int value) {
 this->nirb = value;
}
template <typename E>
int Node<E>::getNodeIndexLeftBoundary() {
 return this->nilb;
}
template <typename E>
int Node<E>::getNodeIndexRightBoundary() {
 return this->nirb;
}
template <typename E>
std::vector<N_ID> Node<E>::getChildren() {
 return std::vector<N_ID>();
}
template <typename E>
std::string Node<E>::toString() {
 return "";
}
template <typename E>
Node<E>::~Node() {
}
}
#endif
#ifndef TOPIC_H_
#define TOPIC_H_
#include <string>
namespace ontology {
class Topic {
public:
 std::string name;
 Topic_ID id;
 Topic(std::string name, int id);
 std::string getName();
 Topic_ID getID();
 virtual ~Topic();
};
}
#endif
#ifndef TREE_H_
#define TREE_H_
#include <string>
#include <stack>
#include <vector>
#include <algorithm>
#include <iostream>
namespace ontology {
class ItemContainer;
template <typename T>
class Tree {
public:
 N_ID root;
 ItemContainer *item_container;
 Tree(ItemContainer *item_container);
 virtual N_ID createNode(T element);
 N_ID getRoot();
 void setRoot(N_ID node);
 std::vector<N_ID> toPreorderNodeList();
 std::string toString();
 virtual bool isBinaryTree();
 virtual bool isDAryTree();
 ItemContainer *getItemContainer();
 virtual Node<T> *getNodeForID(N_ID id);
 virtual ~Tree();
protected:
 void toPreorderNodeListHelper(std::stack<N_ID> node_stack_a,
   std::vector<N_ID> *node_list);
 std::string toStringHelper(N_ID node_id);
};
}
#endif
#ifndef TREE_T_H_
#define TREE_T_H_
namespace ontology {
template <typename T>
Tree<T>::Tree(ItemContainer *item_container) {
 this->item_container = item_container;
}
template <typename T>
N_ID Tree<T>::createNode(T element) {
 return -1;
}
template <typename T>
N_ID Tree<T>::getRoot() {
 return this->root;
}
template <typename T>
void Tree<T>::setRoot(N_ID node) {
 this->root = node;
}
template <typename T>
std::vector<N_ID> Tree<T>::toPreorderNodeList() {
 N_ID root_id = this->getRoot();
 std::stack<N_ID> node_stack_a = std::stack<N_ID>();
 node_stack_a.push(root_id);
 std::vector<N_ID> node_list = std::vector<N_ID>();
 this->toPreorderNodeListHelper(node_stack_a, &node_list);
 return node_list;
}
template <typename T>
std::string Tree<T>::toString() {
 N_ID root_id = this->getRoot();
 return this->toStringHelper(root_id);
}
template <typename T>
void Tree<T>::toPreorderNodeListHelper(std::stack<N_ID> node_stack_a,
  std::vector<N_ID> *node_list) {
 while (node_stack_a.size() != 0) {
  N_ID curr_node_id = node_stack_a.top();
  node_stack_a.pop();
  node_list->push_back(curr_node_id);
  Node<T> *curr_node = this->getNodeForID(curr_node_id);
  std::vector<N_ID> children_ids = curr_node->getChildren();
  std::vector<N_ID> next_children_ids = std::vector<N_ID>(children_ids);
  std::reverse(next_children_ids.begin(), next_children_ids.end());
  for (N_ID child_id : next_children_ids) {
   node_stack_a.push(child_id);
  }
 }
}
template <typename T>
std::string Tree<T>::toStringHelper(N_ID node_id) {
 std::vector<std::string> result_str_components =
   std::vector<std::string>();
 Node<T> *node = this->getNodeForID(node_id);
 std::string curr_node_str = node->toString();
 result_str_components.push_back(curr_node_str);
 for (N_ID child_id : node->getChildren()) {
  std::string child_str = this->toStringHelper(child_id);
  result_str_components.push_back(child_str);
 }
 std::string result_str = Util::join(result_str_components);
 std::string next_result_str = "(" + result_str + ")";
 return next_result_str;
}
template <typename T>
bool Tree<T>::isBinaryTree() {
 return false;
}
template <typename T>
bool Tree<T>::isDAryTree() {
 return false;
}
template <typename T>
ItemContainer *Tree<T>::getItemContainer() {
 return this->item_container;
}
template <typename T>
Node<T> *Tree<T>::getNodeForID(N_ID id) {
 return NULL;
}
template <typename T>
Tree<T>::~Tree() {
}
}
#endif
#ifndef DARYTREENODE_H_
#define DARYTREENODE_H_
#include <string>
#include <vector>
namespace ontology {
class DAryTreeNode : public Node<std::string> {
public:
 DATN_ID parent;
 std::vector<DATN_ID> children;
 DATN_ID id;
 DAryTreeNode(DATN_ID parent, std::string element,
   std::vector<DATN_ID> children, DATN_ID id);
 DATN_ID getParent();
 void setParent(DATN_ID parent);
 virtual std::vector<DATN_ID> getChildren() override;
 virtual std::string toString() override;
 void addChild(DATN_ID node);
 DATN_ID getID();
 virtual ~DAryTreeNode();
};
}
#endif
#ifndef DARYTREE_H_
#define DARYTREE_H_
#include <string>
namespace ontology {
class DAryTree : public Tree<std::string> {
public:
 DAT_ID id;
 DAryTree(DAT_ID id, ItemContainer *item_container);
 virtual DATN_ID createNode(std::string element) override;
 void explore();
 static DAT_ID parseTokens(std::vector<std::string> token_list, ItemContainer *item_container);
 DAT_ID getID();
 virtual bool isDAryTree() override;
 virtual Node<std::string> *getNodeForID(N_ID id) override;
 virtual ~DAryTree();
protected:
 void exploreHelper(std::stack<explore_tuple> node_stack_a,
   PreorderNodeCountContainer *count_container);
 static DAT_ID parseTokensHelper(DAT_ID tree,
   std::deque<std::string> token_deque,
   std::stack<std::vector<DATN_ID>> stack,
   ItemContainer *item_container);
};
}
#endif
#ifndef BINARYTREENODE_H_
#define BINARYTREENODE_H_
#include <vector>
namespace ontology {
class BinaryTreeNode : public Node<Topic_ID> {
public:
 BTN_ID left_child, right_child;
 int question_count;
 BTN_ID id;
 ItemContainer *item_container;
 BinaryTreeNode(Topic_ID element, BTN_ID left_child,
   BTN_ID right_child, int question_count,
   int nilb, int nirb, BTN_ID id,
   ItemContainer *item_container);
 BTN_ID getLeftChild();
 BTN_ID getRightChild();
 void setLeftChild(BTN_ID node);
 void setRightChild(BTN_ID node);
 int getQuestionCount();
 void setQuestionCount(int count);
 BTN_ID getID();
 virtual std::vector<BTN_ID> getChildren() override;
 virtual std::string toString() override;
 virtual ~BinaryTreeNode();
protected:
 ItemContainer *getItemContainer();
};
}
#endif
#ifndef BINARYTREE_H_
#define BINARYTREE_H_
#include <unordered_map>
#include <stack>
#include <vector>
#include <utility>
#include <deque>
namespace ontology {
class ItemContainer;
class Topic;
class BinaryTree : public Tree<Topic_ID> {
public:
 BT_ID id;
 BinaryTree(ItemContainer *item_container, BT_ID tree_id);
 virtual BTN_ID createNode(Topic_ID element) override;
 BTN_ID createTrackedNode(Topic_ID element,
   BTN_ID left_child,
   BTN_ID right_child,
   int question_count, int nilb, int nirb);
 static BT_ID build(DAT_ID tree_id, ItemContainer *ic);
 BT_ID modify(int l, int r, int idx, int val);
 int getSum(int l, int r, int ql, int qr);
 std::vector<BTN_ID> toInorderNodeList();
 BTN_ID cloneNode(BTN_ID node_id);
 BT_ID getID();
 virtual bool isBinaryTree() override;
 virtual Node<Topic_ID> *getNodeForID(N_ID id) override;
 virtual ~BinaryTree();
protected:
 static BTN_ID buildHelper(BT_ID tree_id,
   std::vector<DATN_ID> node_ids,
   std::stack<build_tuple> tuple_stack_a,
   ItemContainer *item_container);
 BTN_ID modifyHelper(std::stack<modify_tuple_a> tuple_stack_a,
   std::stack<modify_tuple_b> tuple_stack_b);
 void toInorderNodeListHelper(std::stack<BTN_ID> node_id_stack_a,
   std::vector<BTN_ID> node_id_list);
 void getPathToNode(int leaf_idx,
   int l, int r, BinaryTreeNode *root,
   std::deque<BinaryTreeNode *> *out_node_list);
 void getPathToNodeHelper(int leaf_idx, int l, int r, BinaryTreeNode *node,
   std::deque<BinaryTreeNode *> *path_list);
 BinaryTreeNode *getLCAGivenPath(std::deque<BinaryTreeNode *> *node_list1,
   std::deque<BinaryTreeNode *> *node_list2);
 BinaryTreeNode *getLCAGivenPathHelper(std::deque<BinaryTreeNode *> *node_list1,
   std::deque<BinaryTreeNode *> *node_list2,
   BinaryTreeNode *prev_node, int i);
 int getSumGivenLCAAndPaths(std::deque<BinaryTreeNode *> *node_list1,
   std::deque<BinaryTreeNode *> *node_list2,
   BinaryTreeNode *lca_node);
 int getSumGivenLCAAndPathsHelperA(BinaryTreeNode *lca_node);
 int getSumGivenLCAAndPathsHelperB(std::deque<BinaryTreeNode *> *node_list,
   BinaryTreeNode *lca_node);
 int getSumGivenLCAAndPathsHelperC(std::deque<BinaryTreeNode *> *excluding_lca_node_list,
   BinaryTreeNode *parent, bool left_is_keep_side, int i);
};
}
#endif
#ifndef SOLUTION_H_
#define SOLUTION_H_
class Solution {
public:
 Solution();
 virtual ~Solution();
};
#endif
namespace ontology {
QuestionCompare::QuestionCompare(ItemContainer *item_container) {
 this->item_container = item_container;
}
bool QuestionCompare::operator()(Question_ID q_id1, Question_ID q_id2) {
 ItemContainer *item_container = this->getItemContainer();
 std::vector<Question> *qitqv = item_container->getQuestionIDToQuestionVec();
 Question &q1 = (*qitqv)[q_id1];
 Question &q2 = (*qitqv)[q_id2];
 std::string q_str1, q_str2;
 int topic_id1, topic_id2;
 q_str1 = q1.getQuestionString();
 q_str2 = q2.getQuestionString();
 topic_id1 = q1.getTopic();
 topic_id2 = q2.getTopic();
 int comp = q_str1.compare(q_str2);
 if (comp < 0) {
  return true;
 } else if (comp > 0) {
  return false;
 } else {
  if (topic_id1 < topic_id2) {
   return true;
  } else if (topic_id1 > topic_id2) {
   return false;
  } else {
   return false;
  }
 }
}
ItemContainer *QuestionCompare::getItemContainer() {
 return this->item_container;
}
QuestionCompare::~QuestionCompare() {
}
}
namespace ontology {
bool QSTIPCompare::operator()(QSTIP &qstip1, QSTIP &qstip2) {
 int result = QSTIPCompare::compare(qstip1, qstip2);
 return result;
}
int QSTIPCompare::compare(QSTIP &qstip1, QSTIP &qstip2) {
 std::string question_str1, question_str2;
 int topic_id1, topic_id2;
 std::tie(question_str1, topic_id1) = qstip1;
 std::tie(question_str2, topic_id2) = qstip2;
 int cmp = question_str1.compare(question_str2);
 if (cmp < 0) {
  return -1;
 } else if (cmp > 0) {
  return 1;
 } else {
  // cmp == 0
  if (topic_id1 < topic_id2) {
   return -1;
  } else if (topic_id1 > topic_id2) {
   return 1;
  } else {
   return 0;
  }
 }
}
QSTIPCompare::QSTIPCompare() {
}
QSTIPCompare::~QSTIPCompare() {
}
}
namespace ontology {
ItemContainer::ItemContainer(std::vector<BinaryTreeNode> *btn_id_to_btn_vec,
  std::vector<Topic> *topic_id_to_topic_vec,
  std::vector<Question> *question_id_to_question_vec,
  std::vector<DAryTreeNode> *datn_id_to_datn_vec,
  std::vector<BinaryTree> *bt_id_to_bt_vec,
  std::vector<DAryTree> *dat_id_to_dat_vec,
  NTTID *name_to_topic_id_dict) {
 this->btn_id_to_btn_vec = btn_id_to_btn_vec;
 this->topic_id_to_topic_vec = topic_id_to_topic_vec;
 this->question_id_to_question_vec = question_id_to_question_vec;
 this->datn_id_to_datn_vec = datn_id_to_datn_vec;
 this->bt_id_to_bt_vec = bt_id_to_bt_vec;
 this->dat_id_to_dat_vec = dat_id_to_dat_vec;
 this->name_to_topic_id_dict = name_to_topic_id_dict;
}
std::vector<BinaryTreeNode> *ItemContainer::getBTNIDToBTNVec() {
 return this->btn_id_to_btn_vec;
}
std::vector<Topic> *ItemContainer::getTopicIDToTopicVec() {
 return this->topic_id_to_topic_vec;
}
std::vector<Question> *ItemContainer::getQuestionIDToQuestionVec() {
 return this->question_id_to_question_vec;
}
std::vector<DAryTreeNode> *ItemContainer::getDATNIDToDATNVec() {
 return this->datn_id_to_datn_vec;
}
std::vector<BinaryTree> *ItemContainer::getBTIDToBTVec() {
 return this->bt_id_to_bt_vec;
}
std::vector<DAryTree> *ItemContainer::getDATIDToDATVec() {
 return this->dat_id_to_dat_vec;
}
NTTID *ItemContainer::getNameToTopicIDDict() {
 return this->name_to_topic_id_dict;
}
ItemContainer::~ItemContainer() {
}
}
namespace ontology {
PreorderNodeCountContainer::PreorderNodeCountContainer(int count) {
 this->count = count;
}
int PreorderNodeCountContainer::getCount() {
 return this->count;
}
void PreorderNodeCountContainer::setCount(int count) {
 this->count = count;
}
PreorderNodeCountContainer::~PreorderNodeCountContainer() {
}
}
namespace ontology {
Util::Util() {
}
int Util::lowerBound(std::vector<QSTIP> &items, QSTIP &value) {
 int l = 0;
 int r = items.size() - 1;
 return Util::lowerBoundHelper(items, l, r, value);
}
int Util::lowerBoundHelper(std::vector<QSTIP> &items,
  int l, int r, QSTIP &value) {
 int it;
 int count = distance(l, r);
 int step;
 while (count > 0) {
  it = l;
  step = count / 2;
  it += step;
  int comparison = QSTIPCompare::compare(items[it], value);
  if (comparison < 0) {
   l = it + 1;
   it += 1;
   count -= step + 1;
  } else {
   count = step;
  }
 }
 return l;
}
int Util::distance(int l, int r) {
 return r - l + 1;
}
std::vector<std::string> Util::split(std::string &line) {
 std::vector<std::string> result =
   std::vector<std::string>();
 std::istringstream s(line);
 std::string curr_str;
 while (s >> curr_str) {
  result.push_back(curr_str);
 }
 return result;
}
std::string Util::join(std::vector<std::string> &parts) {
 if (parts.size() == 0) {
  return "";
 } else {
  std::string first_part = parts.front();
  std::string result_str = first_part;
  for (int i = 0; i < parts.size() - 1; i++) {
   std::string curr_part = parts[i + 1];
   result_str += " " + curr_part;
  }
  return result_str;
 }
}
Util::~Util() {
}
}
namespace ontology {
Question::Question(Topic_ID topic_id, Question_ID id, std::string question_str) {
 this->topic_id = topic_id;
 this->id = id;
 this->question_str = question_str;
}
Topic_ID Question::getTopic() {
 return this->topic_id;
}
std::string Question::getQuestionString() {
 return this->question_str;
}
Question_ID Question::getID() {
 return this->id;
}
Question::~Question() {
}
}
namespace ontology {
Topic::Topic(std::string name, Topic_ID id) {
 this->name = name;
 this->id = id;
}
std::string Topic::getName() {
 return this->name;
}
Topic_ID Topic::getID() {
 return this->id;
}
Topic::~Topic() {
}
}
namespace ontology {
DAryTreeNode::DAryTreeNode(DATN_ID parent, std::string element,
  std::vector<DATN_ID> children, DATN_ID id)
 : Node<std::string>(element, -1, -1) {
 this->parent = parent;
 this->children = children;
 this->id = id;
}
DATN_ID DAryTreeNode::getParent() {
 return this->parent;
}
void DAryTreeNode::setParent(DATN_ID parent) {
 this->parent = parent;
}
std::vector<DATN_ID> DAryTreeNode::getChildren() {
 return this->children;
}
std::string DAryTreeNode::toString() {
 std::string element_str = this->getElement();
 int nilb = this->getNodeIndexLeftBoundary();
 int nirb = this->getNodeIndexRightBoundary();
 std::string nilb_str = std::to_string(nilb);
 std::string nirb_str = std::to_string(nirb);
 std::string result_str = element_str + " " +
   nilb_str + " " + nirb_str;
 return result_str;
}
void DAryTreeNode::addChild(DATN_ID node) {
 (this->children).push_back(node);
}
DAryTreeNode::~DAryTreeNode() {
}
}
namespace ontology {
DAryTree::DAryTree(DAT_ID id, ItemContainer *item_container)
 : Tree<std::string>(item_container) {
 this->id = id;
 N_ID root_id = this->createNode("");
 this->root = root_id;
}
DATN_ID DAryTree::createNode(std::string element) {
 ItemContainer *item_container = this->getItemContainer();
 std::vector<DAryTreeNode> *datnitdatnv = item_container->getDATNIDToDATNVec();
 int num_items = datnitdatnv->size();
 DATN_ID node_id = num_items;
 DAryTreeNode node = DAryTreeNode(-1, element,
   std::vector<DATN_ID>(), node_id);
 datnitdatnv->push_back(node);
 return node_id;
}
void DAryTree::explore() {
 DATN_ID root_id = this->getRoot();
 int preorder_node_count = -1;
 PreorderNodeCountContainer count_container =
   PreorderNodeCountContainer(preorder_node_count);
 DATN_ID node_id = root_id;
 bool is_pre = true;
 explore_tuple tuple1 = explore_tuple(node_id, is_pre);
 std::stack<explore_tuple> node_stack_a =
   std::stack<explore_tuple>();
 node_stack_a.push(tuple1);
 this->exploreHelper(node_stack_a, &count_container);
}
void DAryTree::exploreHelper(std::stack<explore_tuple> node_stack_a,
  PreorderNodeCountContainer *count_container) {
 ItemContainer *item_container = this->getItemContainer();
 std::vector<DAryTreeNode> *datnitdatnv = item_container->getDATNIDToDATNVec();
 while (node_stack_a.size() != 0) {
  explore_tuple curr_tuple = node_stack_a.top();
  node_stack_a.pop();
  DATN_ID curr_node_id;
  bool is_pre;
  std::tie(curr_node_id, is_pre) = curr_tuple;
  DAryTreeNode &curr_node = (*datnitdatnv)[curr_node_id];
  if (is_pre == true) {
   explore_tuple next_tuple = explore_tuple(curr_node_id, false);
   node_stack_a.push(next_tuple);
   count_container->setCount(count_container->getCount() + 1);
   int node_index_left_boundary = count_container->getCount();
   curr_node.setNodeIndexLeftBoundary(node_index_left_boundary);
   std::vector<DATN_ID> children =
     curr_node.getChildren();
   std::vector<DATN_ID> next_children =
     std::vector<DATN_ID>(children);
   std::reverse(next_children.begin(), next_children.end());
   for (DATN_ID child_id : next_children) {
    explore_tuple next_next_tuple = explore_tuple(child_id, true);
    node_stack_a.push(next_next_tuple);
   }
  } else {
   int node_index_right_boundary = count_container->getCount();
   curr_node.setNodeIndexRightBoundary(node_index_right_boundary);
  }
 }
}
DAT_ID DAryTree::parseTokens(std::vector<std::string> token_list,
  ItemContainer *item_container) {
 std::vector<DAryTree> *datitdatv = item_container->getDATIDToDATVec();
 int num_trees = datitdatv->size();
 DAT_ID tree_id = num_trees;
 DAryTree tree = DAryTree(tree_id, item_container);
 datitdatv->push_back(tree);
 std::stack<std::vector<DATN_ID>> stack =
   std::stack<std::vector<DATN_ID>>();
 std::deque<std::string> token_deque =
   std::deque<std::string>();
 std::for_each(token_list.begin(), token_list.end(),
   [&] (std::string token) { token_deque.push_back(token); });
 token_deque.push_front("(");
 token_deque.push_back(")");
 DAT_ID result =
   DAryTree::parseTokensHelper(tree_id,
     token_deque, stack, item_container);
 return result;
}
DAT_ID DAryTree::parseTokensHelper(DAT_ID tree_id,
  std::deque<std::string> token_deque,
  std::stack<std::vector<DATN_ID>> stack,
  ItemContainer *item_container) {
 std::vector<DAryTreeNode> *datnitdatnv = item_container->getDATNIDToDATNVec();
 std::vector<DAryTree> *datitdatv = item_container->getDATIDToDATVec();
 DAryTree &tree = (*datitdatv)[tree_id];
 DATN_ID root_node_id;
 while (token_deque.size() != 0) {
  std::string next_token = token_deque.front();
  token_deque.pop_front();
  if (next_token.compare("(") == 0) {
   std::vector<DATN_ID> children_ids =
     std::vector<DATN_ID>();
   stack.push(children_ids);
  } else if (next_token.compare(")") == 0) {
   std::vector<DATN_ID> children_ids =
     stack.top();
   stack.pop();
   DATN_ID parent_id = -1;
   DAryTreeNode *parent = NULL;
   if (stack.size() != 0) {
    std::vector<DATN_ID> &node_ids = stack.top();
    parent_id = node_ids.back();
    parent = &(*datnitdatnv)[parent_id];
   } else {
    root_node_id = children_ids.front();
   }
   for (DATN_ID child_id : children_ids) {
    DAryTreeNode &child = (*datnitdatnv)[child_id];
    child.setParent(parent_id);
    if (parent_id != -1) {
     parent->addChild(child_id);
    }
   }
  } else {
   std::string topic_str = next_token;
   std::vector<DATN_ID> &children_ids = stack.top();
   int num_items = datnitdatnv->size();
   DATN_ID node_id = num_items;
   DAryTreeNode node =
     DAryTreeNode(-1, topic_str,
       std::vector<DATN_ID>(), node_id);
   datnitdatnv->push_back(node);
   children_ids.push_back(node_id);
  }
 }
 tree.setRoot(root_node_id);
 return tree_id;
}
DAT_ID DAryTree::getID() {
 return this->id;
}
bool DAryTree::isDAryTree() {
 return true;
}
Node<std::string> *DAryTree::getNodeForID(N_ID id) {
 ItemContainer *item_container = this->getItemContainer();
 std::vector<DAryTreeNode> *datnitdatnv = item_container->getDATNIDToDATNVec();
 DAryTreeNode *node = &(*datnitdatnv)[id];
 return node;
}
DAryTree::~DAryTree() {
}
}
namespace ontology {
BinaryTreeNode::BinaryTreeNode(Topic_ID element, BTN_ID left_child,
  BTN_ID right_child, int question_count, int nilb, int nirb,
  int id, ItemContainer *item_container)
  : Node<Topic_ID>(element, nilb, nirb) {
 this->left_child = left_child;
 this->right_child = right_child;
 this->question_count = question_count;
 this->id = id;
 this->item_container = item_container;
}
BTN_ID BinaryTreeNode::getLeftChild() {
 return this->left_child;
}
BTN_ID BinaryTreeNode::getRightChild() {
 return this->right_child;
}
void BinaryTreeNode::setLeftChild(BTN_ID node) {
 this->left_child = node;
}
void BinaryTreeNode::setRightChild(BTN_ID node) {
 this->right_child = node;
}
int BinaryTreeNode::getQuestionCount() {
 return this->question_count;
}
void BinaryTreeNode::setQuestionCount(int count) {
 this->question_count = count;
}
BTN_ID BinaryTreeNode::getID() {
 return this->id;
}
std::vector<BTN_ID> BinaryTreeNode::getChildren() {
 std::vector<BTN_ID> children =
   std::vector<BTN_ID>();
 BTN_ID left_child = this->left_child;
 BTN_ID right_child = this->right_child;
 if (left_child != -1) {
  children.push_back(left_child);
 }
 if (right_child != -1) {
  children.push_back(right_child);
 }
 return children;
}
std::string BinaryTreeNode::toString() {
 Topic_ID topic_id = this->getElement();
 std::string topic_str;
 if (topic_id == -1) {
  topic_str = "None";
 } else {
  ItemContainer *item_container = this->getItemContainer();
  std::vector<Topic> *tittv = item_container->getTopicIDToTopicVec();
  Topic &topic = (*tittv)[topic_id];
  topic_str = topic.getName();
 }
 int question_count = this->getQuestionCount();
 std::string question_count_str = std::to_string(question_count);
 int nilb = this->getNodeIndexLeftBoundary();
 int nirb = this->getNodeIndexRightBoundary();
 std::string nilb_str = std::to_string(nilb);
 std::string nirb_str = std::to_string(nirb);
 std::string result = topic_str + " " +
   question_count_str + " " + nilb_str + " " + nirb_str;
 return result;
}
BinaryTreeNode::~BinaryTreeNode() {
}
ItemContainer *BinaryTreeNode::getItemContainer() {
 return this->item_container;
}
}
namespace ontology {
BinaryTree::BinaryTree(ItemContainer *item_container, BT_ID tree_id)
 : Tree<Topic_ID>(item_container) {
 this->id = tree_id;
 N_ID root_id = this->createNode(-1);
 this->root = root_id;
}
BTN_ID BinaryTree::createNode(Topic_ID element) {
 ItemContainer *item_container = this->getItemContainer();
 std::vector<BinaryTreeNode> *btnitbtnv =
   item_container->getBTNIDToBTNVec();
 int num_items = btnitbtnv->size();
 BTN_ID node_id = num_items;
 BTN_ID left_child = -1;
 BTN_ID right_child = -1;
 int question_count = 0;
 BinaryTreeNode node =
   BinaryTreeNode(element, left_child, right_child,
     question_count, -1, -1, -1, this->getItemContainer());
 btnitbtnv->push_back(node);
 return node_id;
}
BTN_ID BinaryTree::createTrackedNode(Topic_ID element,
  BTN_ID left_child, BTN_ID right_child,
  int question_count, int nilb, int nirb) {
 ItemContainer *item_container = this->getItemContainer();
 std::vector<BinaryTreeNode> *btnitbtnv = item_container->getBTNIDToBTNVec();
 int num_nodes = btnitbtnv->size();
 int id = num_nodes;
 BinaryTreeNode node =
   BinaryTreeNode(element, left_child, right_child,
     question_count, nilb, nirb, id, item_container);
 btnitbtnv->push_back(node);
 return id;
}
BTN_ID BinaryTree::build(DAT_ID tree_id, ItemContainer *item_container) {
 std::vector<DAryTree> *datitdatv = item_container->getDATIDToDATVec();
 DAryTree curr_tree = (*datitdatv)[tree_id];
 std::vector<DATN_ID> node_ids = curr_tree.toPreorderNodeList();
 std::vector<BinaryTree> *btitbtv = item_container->getBTIDToBTVec();
 BT_ID next_tree_id = btitbtv->size();
 BinaryTree next_tree = BinaryTree(item_container, next_tree_id);
 btitbtv->push_back(next_tree);
 BinaryTree &next_next_tree = (*btitbtv)[next_tree_id];
 build_tuple tuple1 = build_tuple(-1, false, 0, node_ids.size() - 1, true);
 std::stack<build_tuple> tuple_stack_a = std::stack<build_tuple>();
 tuple_stack_a.push(tuple1);
 BTN_ID root =
   BinaryTree::buildHelper(next_tree_id, node_ids,
     tuple_stack_a, item_container);
 next_next_tree.setRoot(root);
 return next_tree_id;
}
BTN_ID BinaryTree::buildHelper(BT_ID tree_id,
  std::vector<DATN_ID> node_ids,
  std::stack<build_tuple> tuple_stack_a,
  ItemContainer *item_container) {
 std::vector<DAryTreeNode> *datnitdatnv = item_container->getDATNIDToDATNVec();
 NTTID *name_to_topic_id_dict = item_container->getNameToTopicIDDict();
 std::vector<Topic> *tittv = item_container->getTopicIDToTopicVec();
 std::vector<BinaryTreeNode> *btnitbtnv = item_container->getBTNIDToBTNVec();
 std::vector<BinaryTree> *btitbtv = item_container->getBTIDToBTVec();
 BinaryTree &tree = (*btitbtv)[tree_id];
 BTN_ID root_id;
 while (tuple_stack_a.size() != 0) {
  build_tuple curr_tuple = tuple_stack_a.top();
  tuple_stack_a.pop();
  BTN_ID parent_id;
  bool is_left_child, is_for_root;
  int l, r;
  std::tie(parent_id, is_left_child, l, r, is_for_root) = curr_tuple;
  BTN_ID next_node_id;
  if (l == r) {
   DATN_ID node_id = node_ids[l];
   DAryTreeNode &node = (*datnitdatnv)[node_id];
   std::string topic_str = node.getElement();
   Topic_ID id = (*name_to_topic_id_dict)[topic_str];
   Topic element = (*tittv)[id];
   int nilb = node.getNodeIndexLeftBoundary();
   int nirb = node.getNodeIndexRightBoundary();
   next_node_id = tree.createTrackedNode(id, -1, -1, 0, nilb, nirb);
  } else {
   int m = (l + r) / 2;
   int topic_id = -1;
   int question_count = 0;
   int nilb = -1;
   int nirb = -1;
   next_node_id = tree.createTrackedNode(-1, -1, -1, question_count, nilb, nirb);
   build_tuple tuple1 = build_tuple(next_node_id, true, l, m, false);
   build_tuple tuple2 = build_tuple(next_node_id, false, m + 1, r, false);
   tuple_stack_a.push(tuple1);
   tuple_stack_a.push(tuple2);
  }
  if (is_for_root == true) {
   root_id = next_node_id;
  } else {
   BinaryTreeNode &parent = (*btnitbtnv)[parent_id];
   if (is_left_child == true) {
    parent.setLeftChild(next_node_id);
   } else {
    parent.setRightChild(next_node_id);
   }
  }
 }
 return root_id;
}
BT_ID BinaryTree::modify(int l, int r, int idx, int val) {
 int node_id = this->getRoot();
 ItemContainer *item_container = this->getItemContainer();
 std::vector<BinaryTreeNode> *btnitbtnv = item_container->getBTNIDToBTNVec();
 std::vector<BinaryTree> *btitbtv = item_container->getBTIDToBTVec();
 BinaryTreeNode &node = (*btnitbtnv)[node_id];
 BTN_ID parent_id = -1;
 modify_tuple_a tuple1 =
   modify_tuple_a(l, r, idx, val, node_id, parent_id, false, true);
 std::stack<modify_tuple_a> tuple_stack_a =
   std::stack<modify_tuple_a>();
 tuple_stack_a.push(tuple1);
 std::stack<modify_tuple_b> tuple_stack_b =
   std::stack<modify_tuple_b>();
 BTN_ID root_id = BinaryTree::modifyHelper(tuple_stack_a, tuple_stack_b);
 BT_ID next_tree_id = btitbtv->size();
 BinaryTree tree = BinaryTree(item_container, next_tree_id);
 tree.setRoot(root_id);
 btitbtv->push_back(tree);
 return next_tree_id;
}
BTN_ID BinaryTree::modifyHelper(std::stack<modify_tuple_a> tuple_stack_a,
  std::stack<modify_tuple_b> tuple_stack_b) {
 BTN_ID root_id;
 ItemContainer *item_container = this->getItemContainer();
 std::vector<BinaryTreeNode> *btnitbtnv = item_container->getBTNIDToBTNVec();
 while (tuple_stack_a.size() != 0) {
  modify_tuple_a curr_tuple = tuple_stack_a.top();
  tuple_stack_a.pop();
  int l, r, idx, val;
  BTN_ID node_id, parent_id;
  bool is_left_child, is_for_root;
  std::tie(l, r, idx, val, node_id, parent_id,
    is_left_child, is_for_root) = curr_tuple;
  modify_tuple_b next_tuple;
  BTN_ID next_node_id;
  BinaryTreeNode &node = (*btnitbtnv)[node_id];
  if (l == r) {
   next_node_id = this->cloneNode(node_id);
   int question_count = node.getQuestionCount();
   int next_question_count = question_count + val;
   BinaryTreeNode &next_node = (*btnitbtnv)[next_node_id];
   next_node.setQuestionCount(next_question_count);
  } else {
   int m = (l + r) / 2;
   if (idx <= m) {
    BTN_ID left_child_id = node.getLeftChild();
    next_node_id = this->cloneNode(node_id);
    modify_tuple_a tuple1 =
      modify_tuple_a(l, m, idx, val,
        left_child_id, next_node_id, true, false);
    tuple_stack_a.push(tuple1);
   } else {
    BTN_ID right_child_id = node.getRightChild();
    next_node_id = this->cloneNode(node_id);
    modify_tuple_a tuple1 =
      modify_tuple_a(m + 1, r, idx, val,
        right_child_id, next_node_id, false, false);
    tuple_stack_a.push(tuple1);
   }
  }
  next_tuple = modify_tuple_b(next_node_id);
  tuple_stack_b.push(next_tuple);
  if (is_for_root == true) {
   root_id = next_node_id;
  } else {
   BinaryTreeNode &parent = (*btnitbtnv)[parent_id];
   if (is_left_child == true) {
    parent.setLeftChild(next_node_id);
   } else {
    parent.setRightChild(next_node_id);
   }
  }
 }
 while (tuple_stack_b.size() != 0) {
  modify_tuple_b curr_tuple = tuple_stack_b.top();
  tuple_stack_b.pop();
  BTN_ID next_node_id;
  std::tie(next_node_id) = curr_tuple;
  BinaryTreeNode &next_node = (*btnitbtnv)[next_node_id];
  BTN_ID left_child_id = next_node.getLeftChild();
  BTN_ID right_child_id = next_node.getRightChild();
  int s;
  if (left_child_id == -1 && right_child_id == -1) {
   s = next_node.getQuestionCount();
  } else {
   int s1, s2;
   if (left_child_id != -1) {
    BinaryTreeNode &left_child = (*btnitbtnv)[left_child_id];
    s1 = left_child.getQuestionCount();
   } else {
    s1 = 0;
   }
   if (right_child_id != -1) {
    BinaryTreeNode &right_child = (*btnitbtnv)[right_child_id];
    s2 = right_child.getQuestionCount();
   } else {
    s2 = 0;
   }
   s = s1 + s2;
  }
  next_node.setQuestionCount(s);
 }
 return root_id;
}
int BinaryTree::getSum(int l, int r, int ql, int qr) {
 ItemContainer *item_container = this->getItemContainer();
 BTN_ID root_id = this->getRoot();
 std::vector<BinaryTreeNode> *btnitbtnv = item_container->getBTNIDToBTNVec();
 BinaryTreeNode &root = (*btnitbtnv)[root_id];
 std::deque<BinaryTreeNode *> node_list1 =
   std::deque<BinaryTreeNode *>();
 BinaryTree::getPathToNode(ql, l, r, &root, &node_list1);
 std::deque<BinaryTreeNode *> node_list2 =
   std::deque<BinaryTreeNode *>();
 BinaryTree::getPathToNode(qr, l, r, &root, &node_list2);
 BinaryTreeNode *lca_node = BinaryTree::getLCAGivenPath(&node_list1, &node_list2);
 int sum_value = BinaryTree::getSumGivenLCAAndPaths(&node_list1, &node_list2, lca_node);
 return sum_value;
}
void BinaryTree::getPathToNode(int leaf_idx,
  int l, int r, BinaryTreeNode *root,
  std::deque<BinaryTreeNode *> *out_node_list) {
 BinaryTree::getPathToNodeHelper(leaf_idx, l, r, root, out_node_list);
}
void BinaryTree::getPathToNodeHelper(int leaf_idx, int l, int r, BinaryTreeNode *node,
  std::deque<BinaryTreeNode *> *path_list) {
 path_list->push_back(node);
 if (l == r) {
  return;
 }
 int m = (l + r) / 2;
 if (leaf_idx <= m) {
  BTN_ID left_child_id = node->getLeftChild();
  BinaryTreeNode *left_child = static_cast<BinaryTreeNode *>(this->getNodeForID(left_child_id));
  BinaryTree::getPathToNodeHelper(leaf_idx, l, m, left_child, path_list);
  return;
 } else {
  BTN_ID right_child_id = node->getRightChild();
  BinaryTreeNode *right_child = static_cast<BinaryTreeNode *>(this->getNodeForID(right_child_id));
  BinaryTree::getPathToNodeHelper(leaf_idx, m + 1, r, right_child, path_list);
  return;
 }
}
BinaryTreeNode *BinaryTree::getLCAGivenPath(std::deque<BinaryTreeNode *> *node_list1,
  std::deque<BinaryTreeNode *> *node_list2) {
 if (node_list1->size() == 0 || node_list2->size() == 0) {
  throw "no common ancestor";
 } else {
  BinaryTreeNode *root = node_list1->front();
  return BinaryTree::getLCAGivenPathHelper(node_list1, node_list2, root, 0);
 }
}
BinaryTreeNode *BinaryTree::getLCAGivenPathHelper(std::deque<BinaryTreeNode *> *node_list1,
  std::deque<BinaryTreeNode *> *node_list2,
  BinaryTreeNode *prev_node, int i) {
 if (i >= node_list1->size() || i >= node_list2->size()) {
  return prev_node;
 } else {
  BinaryTreeNode *curr_node1 = (*node_list1)[i];
  BinaryTreeNode *curr_node2 = (*node_list2)[i];
  if (curr_node1 == curr_node2) {
   return BinaryTree::getLCAGivenPathHelper(node_list1, node_list2, curr_node1, i + 1);
  } else {
   return prev_node;
  }
 }
}
int BinaryTree::getSumGivenLCAAndPaths(std::deque<BinaryTreeNode *> *node_list1,
  std::deque<BinaryTreeNode *> *node_list2,
  BinaryTreeNode *lca_node) {
 int sum1 = BinaryTree::getSumGivenLCAAndPathsHelperA(lca_node);
 int lca_i = BinaryTree::getSumGivenLCAAndPathsHelperB(node_list1, lca_node);
 int sum2 = BinaryTree::getSumGivenLCAAndPathsHelperC(node_list1, NULL, false, lca_i + 1);
 int sum3 = BinaryTree::getSumGivenLCAAndPathsHelperC(node_list2, NULL, true, lca_i + 1);
 int total_sum = sum1 + sum2 + sum3;
 return total_sum;
}
int BinaryTree::getSumGivenLCAAndPathsHelperA(BinaryTreeNode *lca_node) {
 int score = 0;
 if (lca_node->getLeftChild() == -1 and lca_node->getRightChild() == -1) {
  score += lca_node->getQuestionCount();
 }
 return score;
}
int BinaryTree::getSumGivenLCAAndPathsHelperB(std::deque<BinaryTreeNode *> *node_list,
  BinaryTreeNode *lca_node) {
 int lca_i;
 for (int i = 0; i < node_list->size(); i++) {
  BinaryTreeNode *node = (*node_list)[i];
  if (node == lca_node) {
   lca_i = i;
   break;
  }
 }
 return lca_i;
}
int BinaryTree::getSumGivenLCAAndPathsHelperC(std::deque<BinaryTreeNode *> *excluding_lca_node_list,
  BinaryTreeNode *parent, bool left_is_keep_side, int i) {
 if (i >= excluding_lca_node_list->size()) {
  return 0;
 } else {
  BinaryTreeNode *curr_node = (*excluding_lca_node_list)[i];
  int partial_score = 0;
  if (parent != NULL) {
   BTN_ID left_child_id = parent->getLeftChild();
   BTN_ID right_child_id = parent->getRightChild();
   BinaryTreeNode *left_child, *right_child;
   if (left_child_id != -1) {
    left_child = static_cast<BinaryTreeNode *>(this->getNodeForID(left_child_id));
   }
   if (right_child_id != -1) {
    right_child = static_cast<BinaryTreeNode *>(this->getNodeForID(right_child_id));
   }
   if (left_child_id != -1 and curr_node == left_child and left_is_keep_side == false) {
    partial_score += right_child->getQuestionCount();
   } else if (right_child_id != -1 and curr_node == right_child and left_is_keep_side == true) {
    partial_score += left_child->getQuestionCount();
   }
  }
  if (curr_node->getLeftChild() == -1 and curr_node->getRightChild() == -1) {
   partial_score += curr_node->getQuestionCount();
  }
  return partial_score + BinaryTree::getSumGivenLCAAndPathsHelperC(excluding_lca_node_list, curr_node, left_is_keep_side, i + 1);
 }
}
std::vector<BTN_ID> BinaryTree::toInorderNodeList() {
 BTN_ID root_id = this->getRoot();
 std::stack<BTN_ID> node_stack_a =
   std::stack<BTN_ID>();
 node_stack_a.push(root_id);
 std::vector<BTN_ID> node_list =
   std::vector<BTN_ID>();
 this->toInorderNodeListHelper(node_stack_a, node_list);
 return node_list;
}
void BinaryTree::toInorderNodeListHelper(std::stack<BTN_ID> node_stack_a,
  std::vector<BTN_ID> node_list) {
 bool done = false;
 BTN_ID curr_node_id = node_stack_a.top();
 node_stack_a.pop();
 ItemContainer *item_container = this->getItemContainer();
 std::vector<BinaryTreeNode> *btnitbtnv = item_container->getBTNIDToBTNVec();
 while (done == false) {
  if (curr_node_id != -1) {
   BinaryTreeNode &curr_node = (*btnitbtnv)[curr_node_id];
   node_stack_a.push(curr_node_id);
   curr_node_id = curr_node.getLeftChild();
  } else {
   if (node_stack_a.size() != 0) {
    curr_node_id = node_stack_a.top();
    node_stack_a.pop();
    BinaryTreeNode &curr_node = (*btnitbtnv)[curr_node_id];
    curr_node_id = curr_node.getRightChild();
   } else {
    done = true;
   }
  }
 }
}
BTN_ID BinaryTree::cloneNode(BTN_ID node_id) {
 ItemContainer *item_container = this->getItemContainer();
 std::vector<BinaryTreeNode> *btnitbtnv = item_container->getBTNIDToBTNVec();
 BinaryTreeNode &node = (*btnitbtnv)[node_id];
 Topic_ID element = node.getElement();
 BTN_ID left_child = node.getLeftChild();
 BTN_ID right_child = node.getRightChild();
 int question_count = node.getQuestionCount();
 int nilb = node.getNodeIndexLeftBoundary();
 int nirb = node.getNodeIndexRightBoundary();
 BTN_ID next_node_id = this->createTrackedNode(element, left_child,
   right_child, question_count, nilb, nirb);
 return next_node_id;
}
bool BinaryTree::isBinaryTree() {
 return true;
}
Node<Topic_ID> *BinaryTree::getNodeForID(N_ID id) {
 ItemContainer *item_container = this->getItemContainer();
 std::vector<BinaryTreeNode> *btnitbtnv = item_container->getBTNIDToBTNVec();
 BinaryTreeNode *node = &(*btnitbtnv)[id];
 return node;
}
BinaryTree::~BinaryTree() {
}
}
#include <iostream>
#include <list>
#include <cstdlib>
#include <map>
#include <string>
#include <fstream>
#include <sstream>
#include <vector>
#include <algorithm>
using namespace std;
int main() {
 ios_base::sync_with_stdio(false);
 // istream *infile = new ifstream("src/tests/official/input99.txt");
 // istream *infile = new ifstream("src/tests/official/input45.txt");
 // istream *infile = new ifstream("src/tests/official/input61.txt");
 // istream *infile = new ifstream("src/tests/official/input79.txt");
 // istream *infile = new ifstream("src/tests/official/input93.txt");
 istream *infile = &cin;
 string line;
 getline(*infile, line);
 istringstream iss(line);
 int N;
 iss >> N;
 string topic_tree_line;
 getline(*infile, topic_tree_line);
 vector<string> tokens = ontology::Util::split(topic_tree_line);
 vector<string> topic_tokens = vector<string>(tokens);
 topic_tokens.erase(remove_if(topic_tokens.begin(), topic_tokens.end(),
   [&] (string a) { return a.compare("(") == 0 || a.compare(")") == 0; }),
   topic_tokens.end());
 auto btn_id_to_btn_vec = vector<ontology::BinaryTreeNode>();
 auto topic_id_to_topic_vec = vector<ontology::Topic>();
 auto question_id_to_question_vec = vector<ontology::Question>();
 auto datn_id_to_datn_vec = vector<ontology::DAryTreeNode>();
 auto bt_id_to_bt_vec = vector<ontology::BinaryTree>();
 auto dat_id_to_dat_vec = vector<ontology::DAryTree>();
 auto name_to_topic_id_dict = ontology::NTTID();
 // vector element addresses are not reliable
 // if allow the vector to be resized;
 // thus, we pre-allocate space for them,
 // hoping that we do not have more space ever required
 int max1 = 1e5 * 34;
 int max2 = 1e5;
 int max3 = 1e5;
 int max4 = 1e5;
 int max5 = 1e5;
 int max6 = 1;
 btn_id_to_btn_vec.reserve(max1);
 topic_id_to_topic_vec.reserve(max2);
 question_id_to_question_vec.reserve(max3);
 datn_id_to_datn_vec.reserve(max4);
 bt_id_to_bt_vec.reserve(max5);
 dat_id_to_dat_vec.reserve(max6);
 ontology::ItemContainer item_container =
   ontology::ItemContainer(&btn_id_to_btn_vec,
     &topic_id_to_topic_vec,
     &question_id_to_question_vec,
     &datn_id_to_datn_vec,
     &bt_id_to_bt_vec,
     &dat_id_to_dat_vec,
     &name_to_topic_id_dict);
 ontology::DAT_ID d_ary_tree_id =
   ontology::DAryTree::parseTokens(tokens, &item_container);
 vector<ontology::DAryTree> *datitdatv = item_container.getDATIDToDATVec();
 ontology::DAryTree &topic_tree = (*datitdatv)[d_ary_tree_id];
 vector<ontology::DATN_ID> topic_tree_nodes =
   topic_tree.toPreorderNodeList();
 for (int i = 0; i < N; i++) {
  string topic_name = topic_tokens[i];
  ontology::Topic_ID id = i;
  ontology::Topic topic = ontology::Topic(topic_name, id);
  name_to_topic_id_dict.insert(make_pair(topic_name, id));
  topic_id_to_topic_vec.push_back(topic);
 }
 unordered_map<ontology::Topic_ID, ontology::DATN_ID> topic_id_to_node_id_dict =
   unordered_map<ontology::Topic_ID, ontology::DATN_ID>();
 for (ontology::DATN_ID datn_id : topic_tree_nodes) {
  ontology::DAryTreeNode &topic_node =
    datn_id_to_datn_vec[datn_id];
  string topic_str = topic_node.getElement();
  ontology::Topic_ID topic_id = name_to_topic_id_dict[topic_str];
  topic_id_to_node_id_dict[topic_id] = datn_id;
 }
 int M;
 getline(*infile, line);
 iss.str(line);
 iss.seekg(0);
 iss >> M;
 vector<ontology::Question_ID> question_ids =
   vector<ontology::Question_ID>();
 for (int i = 0; i < M; i++) {
  string topic_str;
  getline(*infile, topic_str, ' ');
  string next_topic_str = topic_str.substr(0, topic_str.size() - 1);
  string question_str;
  getline(*infile, question_str);
  ontology::Topic_ID topic_id = name_to_topic_id_dict[next_topic_str];
  ontology::Question_ID question_id = i;
  ontology::Question question =
    ontology::Question(topic_id, question_id, question_str);
  question_id_to_question_vec.push_back(question);
  question_ids.push_back(question_id);
 }
 ontology::QuestionCompare question_compare =
   ontology::QuestionCompare(&item_container);
 sort(question_ids.begin(), question_ids.end(), question_compare);
 getline(*infile, line);
 iss.str(line);
 iss.seekg(0);
 int K;
 iss >> K;
 vector<ontology::query_str_topic_pair> query_str_topic_pair_list =
   vector<ontology::query_str_topic_pair>();
 for (int i = 0; i < K; i++) {
  string topic_str;
  getline(*infile, topic_str, ' ');
  string query_str;
  getline(*infile, query_str);
  ontology::Topic_ID topic_id = name_to_topic_id_dict[topic_str];
  ontology::query_str_topic_pair curr_pair =
    ontology::query_str_topic_pair(query_str, topic_id);
  query_str_topic_pair_list.push_back(curr_pair);
 }
 topic_tree.explore();
 ontology::BT_ID next_topic_tree_id =
   ontology::BinaryTree::build(d_ary_tree_id, &item_container);
 ontology::BinaryTree &next_topic_tree =
   bt_id_to_bt_vec[next_topic_tree_id];
 vector<ontology::BTN_ID> node_ids =
   next_topic_tree.toInorderNodeList();
 vector<ontology::BT_ID> topic_tree_ids =
   vector<ontology::BT_ID>();
 topic_tree_ids.push_back(next_topic_tree_id);
 for (int i = 0; i < M; i++) {
  ontology::BT_ID prev_topic_tree_id = i;
  ontology::BinaryTree &prev_topic_tree =
    bt_id_to_bt_vec[prev_topic_tree_id];
  int l = 0;
  int r = N - 1;
  ontology::Question_ID question_id = question_ids[i];
  ontology::Question &question = question_id_to_question_vec[question_id];
  ontology::Topic_ID topic_id = question.getTopic();
  ontology::Topic &topic = topic_id_to_topic_vec[topic_id];
  int idx = topic_id;
  int val = 1;
  ontology::BT_ID curr_topic_tree_id =
    prev_topic_tree.modify(l, r, idx, val);
  topic_tree_ids.push_back(curr_topic_tree_id);
 }
 vector<ontology::QSTIP> question_str_topic_id_pairs =
   vector<ontology::QSTIP>();
 for_each(question_ids.begin(), question_ids.end(),
   [&] (ontology::Question_ID a)
   { ontology::Question &question =
     question_id_to_question_vec[a];
     ontology::QSTIP qstip =
     ontology::QSTIP(question.getQuestionString(),
     question.getTopic());
     question_str_topic_id_pairs.push_back(qstip); });
 for (ontology::query_str_topic_pair curr_query_str_topic_pair :
   query_str_topic_pair_list) {
  string query_str;
  ontology::Topic_ID topic_id;
  tie(query_str, topic_id) = curr_query_str_topic_pair;
  string &query_str1 = query_str;
  string query_str2 = query_str + char(200);
  ontology::QSTIP val1 = ontology::QSTIP(query_str1, -1);
  ontology::QSTIP val2 = ontology::QSTIP(query_str2, -1);
  int index1 = ontology::Util::lowerBound(question_str_topic_id_pairs, val1);
  int index2 = ontology::Util::lowerBound(question_str_topic_id_pairs, val2);
  ontology::DATN_ID topic_node_id = topic_id_to_node_id_dict[topic_id];
  ontology::DAryTreeNode &topic_node = datn_id_to_datn_vec[topic_node_id];
  int nilb = topic_node.getNodeIndexLeftBoundary();
  int nirb = topic_node.getNodeIndexRightBoundary();
  ontology::BinaryTree &topic_tree1 = bt_id_to_bt_vec[index1];
  ontology::BinaryTree &topic_tree2 = bt_id_to_bt_vec[index2];
  int count1 = topic_tree1.getSum(0, N - 1, nilb, nirb);
  int count2 = topic_tree2.getSum(0, N - 1, nilb, nirb);
  int difference = count2 - count1;
  cout << difference << endl;
 }
 delete infile;
}

