# quora
A collection of challenge solutions.

Started: Aug. 28, 2015  
Finished: Nov. 29, 2016

1. nearby (10/10) - python - 8/28/2015

   We use STR-bulk-loaded R-tree with Hjaltason/Samet best-first k-nearest-neighbor search.

2. feed optimizer (10/10) - java - 9/13/2015

   We use dynamic programming with two stacks for online knapsack.

3. upvotes (30/30) - python - 9/15/2015

   We use a moving window and memoizing.

4. schedule (100/100) - python - 9/15/2015

   We use a sort using chance of failure over time ratio descending, tie-breaking preferring smaller time.

5. archery (30/30) - python - 9/16/2015

   We use binary search twice.

6. related questions (30/30) - python, with alternate solution - 9/24/2016

   Our main approach and alternate approaches use DFS with memoizing.

7. typeahead search (10/10) - python - 9/29/2015

   We use a trie with memoizing of data strings at nodes associated with a word base.

8. scrabble stepladder (10/10) - python - 10/3/2015

   We use branch-and-bound using a bound based on "truncated sums" and memoizing.

9. sorted set (9/9) - python - 10/8/2015

   We solve essentially an exercise in remote procedure calls.

10. wombats (100/100) - python - 10/11/2015

   We solve max. weight closure. We use Picard transform and push-relabel max. flow algorithm.

11. ontology (100/100) - c++ - 11/2/2015

   We use a binary persistent tree and Euler-tour technique.

12. datacenter cooling (n/a) - python - 11/30/2015

   We use Jacobsen Hamiltonian cycle enumeration with base connection counts and memoizing.

13. answer classifier (79.4/100) - python - 12/29/2015

   We use MIRA.

14. duplicate (146.07/200) - python - 1/8/2016

   We identify duplicate question pairs. We use cosine dissimilarity, tf-idf metric with character {1, 2, 3}-grams, feature selection, chi-squared-test-based logistic regression, low-memory matrix representation.

15. labeler (134.88/200) - python - 1/8/2016

   We label using most appropriate topic ID values. We use various heuristics (filtering away of topics that don't appear for any question, word count under-/over-shoot, inquisitive word presence, average word length), tf-idf metric with word unigrams, chi-squared-test-based feature selection, logistic regression with one-versus-rest strategy.

16. answered (65.16/100) - python - 1/27/2016

   We predict whether a question gets upvoted in within one day. We use various heuristics (tf-idf metric with word {1, 2}-grams, anonymous author, num. of context and associated topics that pass thresholds for popularity, non-negative word under-/over-shoot, inqusitive first word presence, existence of at least one fully capitalized word with at least two characters, average word length), transductive learning using fixed-seed k-means clustering, feature rediction using chi-squared test, logistic regression.

17. interest (68.50/100) - python - 2/7/2016

   We essentially measure quality of a question. We use various heuristics (log transform and smoothing for target viewer-follower-ratio values, capitalized first letter, penalizing for having no word tokens, punctuation ratio, log-transformed number of associated topics, topic-question word overlap to number of question words ratio, word under-/over-shoot, lower-case inquisitive word inclusion, question texst first word, context topic name, associated topic name not broken up into words with dictionary vectorizer, log-transformed associated topic follower count sum, sparse features and standardization for features not related to one-hot encoding - question text, context topic, associated topic names), transductive learning using k-means clustering with cluster identifier values binarized, f-regression feature selection, linear SVR with squared epsilon-insensitive loss.

18. views (54.58/100) - python - 2/7/2016

   We essentially measure quality of a question. We use various heuristics (log transform and smoothing for target view-lived-days-ratio values; question mark inclusion; log-transformed number of associated topics; topic-question word overlap to number of question words ratio, punctuation ratio; total num. of words in question text; word under-/over-shoot; num. of long acronyms thresholded; case-insensitive inquisitive word inclusion; correct form word count; non-acronym long well-capitalized word count; feature bucketing for certain of the previously mentioned features as well as num. answers and promoted-to values; log transform for num. answers and promoted-to values; thresholded associated topic popularity status; 
question text first word, context topic name, associated topic name not broken up into words with dictionary vectorizers; anonymous author status; log-transformed associated topic follower count sum; lack of context topic status), sparse features and max-abs. value scaling, transductive learning using k-means clustering, cluster identifier values binarized, f-regression feature selection, linear SVR with squared epsilon-insensitive loss.

19. browser extensions - quora image-started question posting (QISQP) - html, css, javascript, jquery - 3/12/2016

   We make a Firefox add-on SDK extension that lets you start a post by right-clicking on an image in a document or just an image in the browser. Works for images with JPG/JPEG, PNG, GIF, BMP as their extension.

20. choosing a substring (n/a) - python - 4/7/2016

   Interview problem. We use memoizing.

21. suggesting the right hotel (n/a) - python - 4/7/2016

   We use favored cities to find most similar unvisited hotels and if we run out of favored cities, revert to k-nearest-neighbor search with k-d tree to find hotels most similar to visited hotels for a booker in feature space. Features used are mean number of stars, mean number of reviews, mean min. price. We normalize feature values.

22. python uri - python - 4/23/2016

   We make a URI parser using grammar from RFC 3986. We support various methods that deal with the URI parts.

23. trend analyzer - python, html, css, javascript, jquery, d3.js - 11/29/2016

   We deal with data cleaning, LeFevre Incognito anonymization, Srikant/Agrawal quantitative/categorical association rule mining, parallel coordinates rule plot.


