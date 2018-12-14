# analysis

comparisons made here are w.r.t. experiments from srikant and agrawal's 1996 paper, "mining quantitative association rules in large relational tables".

we are able to reproduce approximately using our model the number of interesting rules for an input with 500,000 rows, 7 attributes (five quantitative and two categorical), min. support of .2, max. support of .4, min. confidence of .25.

|r|k|num. interesting rules (actual)|num. interesting rules (predicted)|
|---|---|---|---|
|1.1|1.5|~2000|2977|
|1.1|2|~400|472|
|1.1|3|~100|236|
|1.1|5|~28|39|
|2|1.5|~200|436|
|2|2|~60|77|
|2|3|~20|39|
|2|5|~4|6|
|1.5|1.5|~1800|2469|
|1.5|2|~200|388|
|1.5|3|~60|190|
|1.5|5|~15|30|

we compare these results with those in figure seven.

we offer a mixture of upper-bounding and average-case-bounding. in this case, we're always upper-bounding and within a factor of four of actual with our upper-/average-bound predictions. some of the misprediction can be attributed to unevenness in the sample data, not extensively taking into account effect of min. confidence, misuse of our fudge factors (utilization fraction range; support-/confidence-related integral approximation; subbotin beta and sigma for utilization spacing, "effective r", p-factor; categorical attribute distinct value count; scale for subbotin for effective r and p-factor; logistic curve shape for interesting item-set count over item-set count ratio), and certain assumptions we make.

assumptions we make include use of whole dense hierarchy and total r liquidity for interesting item-set count over item-set count ratio for phase i and interesting rule count over rule count ratio for phase ii. by "liquidity", we mean an item-set or rule can borrow r from any other item-set or rule, respectively, even if the candidate borrowed-from item-set or rule doesn't have anything that the borrowing item-set or rule does not have. specifically, we might be lacking an entire attribute or a leftover portion of an interval for an attribute that the two item-sets or rules share, which causes upper-bounding. borrowing r means, effectively, we are borrowing support since r = 1 means uniform support density and we are being optimistic with number of r-satisfying nodes by saying as we work our way down from root, borrowing r from below means r for nodes below is decreased from one instead of being unchanged. by "whole", we arbitrarily mean we consider all possible item-sets for a p value for phase i or all possible rules for a p value for phase ii because this means max. degree is two, which simplifies base and exponent for (effective degree) ^ (max. depth given full levels) calculation, but which hurts upper-bounding because degree could be greater than two for the right input rows and we could thereby have r-constraint's restraining effects be lessened; we then say we are average-case-bounding because we converge towards behavior with all possible item-sets or rules as we increase the number of input row collections we see. degree (and r-dodging) can be arbitrarily large if we stray from whole-size hierarchy, but <= n, where n is number of rows, and <= m = 2 ^ (p - 1), where m is number of leaves in whole hierarchy, because this is the max. width for any hierarchy for the item-sets or rules. by "denseness", we mean tightest packing for nodes in the form of a tree, which also causes upper-bounding if used with item-set count upper-bounding for phase i or rule count upper-bounding for phase ii. to not borrow is to assume all nodes satisfy r = 1. there are diminishing returns that cause successive borrowing's lowered effects on increasing effective degree because of inverse correlation between r and effective degree. note that the extreme state associated with indiscriminate (i.e., associated with total liquidity) and optimistic borrowing helps determine a tight packing that satisfies r for phase i and phase ii and helps with upper-bounding. note that this means we are at least three degrees removed from using actual effective degree - we say we can borrow r from any node, we are ignoring the extra cost of handling descendants when we increase r for a node, and degree can be greater than two and thus r can be less of a barrier to increasing interesting item-set over item-set ratio or interesting rule over rule ratio. we do, however, still upper-bound or apply average-case-bounding for some definition of average.

## note on phases

phase i refers to interesting item-set collection determination.

phase ii refers to interesting rule collection determination.

## note on item-sets and rules

r for item-sets says that item-set X has support r times expected support from a close ancestor generalization item-set X\_hat.

r for rules says that rule X has support r times expected support from a close ancestor generalization rule X\_hat.

generalizations and specializations always have same attributes as the current item-set or rule.

a rule X that is r-interesting relative to a rule X\_hat also has its associated same-size (in terms of number of attributes) item-set r-interesting relative to that for X\_hat. however, an item-set that is r-interesting does not have all its associated same-size (in terms of number of attributes) rules necessarily r-interesting. also, a rule that can come from a non-r-interesting item-set can itself be r-interesting because of omission of attributes for rule generation and resulting changing close ancestor relationships; source item-set may have been larger (in terms of number of attributes) than the rule. for example, say item-set {a, b} is not r-interesting because it is not r-interesting relative to close ancestor {a, b''} (which is also not r-interesting) but is r-interesting relative to close ancestor {a, b'}; and {a, b, c} is r-interesting relative to close ancestors {a, b', c} and {a, b'', c} and survives phase i; and a => b can come from {a, b, c} (and not {a, b}) and be r-interesting relative to close ancestor a => b', which came from {a, b'}, and survive phase ii.

rules that have no close ancestors, which happens when we have combinations of attribute values that have no containing rule or we have only attribute values that are maximal in width, automatically pass phase ii.

confidence only applies to rules.

## note on effective r

for "effective r", we use reciprocal of subbotin reverse cdf pass-through because we have truncation effect for low r (can be viewed as saturation and scaling for low r) and we have, to a lesser degree, depression of rules for high r. we have saturation for low r and we have depression for high r beyond that typically for gaussian for the following reasons: max. support causes truncation effect for low r as our abundant amount of small (in terms of number of attributes) rules with large support don't make it past phase ii; and for large r, it's harder for small rules to pass r-interesting because close ancestor support is likely to be high, and so large r may be unattainable because required amount of support is larger than number of input rows even though we use concept of expected support. we note that subbotin is center-heavy and has small tails.

we note that truncation plays a role in phase ii even though we already take into account scaling using max. support by using it to determine number of interesting item-sets because small (in terms of number of attributes) rules can re-surface during phase ii using large (in terms of number of attributes) item-sets.

## details of model

we adjust number of interesting item-sets based on support integral fraction and confidence integral fraction assuming gaussian distribution fixed approximation for r-k combinations. we account for k-completeness' effects on number of item-sets by using left half of subbotin cdf centered at x = 1 so we have behavior in agreement with concave up shape and values less than linear curve for spacing of utilization values. we use utilization values to, based on k and given spacing and min. and max. values, determine effective number of item-sets. specifically, we use the utilization values to modulate base interval counts for quantitative and categorical attributes for effective item-set count. we made an assumption that five options are available for each categorical attribute. we call the effective item-set count "effective n". we use a subbotin reverse cdf centered at x = 1 for "effective r" to modify r. we use a logistic function centered at x = 6 for interesting-item-set over effective n ratio to modulate (2 / r) ^ (log base two of effective n) because 2 / r is effective degree and the power is depth; we have a tree because at worst case, we have all item-set combinations and degree constraint for close ancestors (two for dense hierarchy); and we use logistic function because it behaves more gracefully than log with small (less than one) x. number of interesting item-sets is interesting-item-set over effective n ratio times effective n times adjusted support integral fraction times adjusted confidence integral fraction. number of rules is number of interesting item-sets times 3 ^ p because at worst-case, we have all size-p rules; we can either leave an attribute out, place it at left, or place it at right. for interesting rule count over rule count ratio we use ((2 / effective r) ^ p + max(log base (effective r) of rule count, 0) / (2 ^ p / p-factor). we thought of using effective r because we viewed it as an opportunity to apply subbotin reverse cdf to tame interesting rule count; we are saying that there is a plateau-like distribution for r-interesting value and transforming r into a different r by using a close-to-exponential transform (approaches infinity with increasing x) which is reciprocal of subbotin reverse cdf pass-through. our way of justifying this and being unusually concentrated at r = 1 is that we say it's disproportionately easier to satisfy low r than it is to satisfy high r (this gives us a gaussian) and we have a truncated gaussian because, we hypothesize, max. support leads to truncation effect for small rules, of which we have many, and number of rows becomes more of a constraint for high r, as we note in section "note on effective r"; subbotin is center-heavy and can be viewed as truncated if scaled correctly. effective degree is 2 / effective r and depth is p; we have a tree because at worst case, we have all attribute inclusion combinations (each level is to do with a decision about an attribute from a size-p rule; depth of p is an over-estimate) and degree constraint for close ancestors (two for dense hierarchy for same reason as for phase i). we have max of a log and zero because if we have effective degree of 1, we still have O(depth) internal nodes, and we ignore internal node count in case where number of r-interesting rule leaves per rule predicted is less than one for simplicity. we have 2 ^ p in denominator because this is an upper bound; this is what happens when we have no attenuation due to effective degree. we have p-factor to bring into the picture fact that assuming the average rule is size-p is an over-estimate; to this end, we use a subbotin pdf centered at x = 1 with r. number of interesting rules is interesting rule count over rule count ratio times rule count.

we don't make an extensive attempt to quantify effects of pruning due to min. confidence.

## note on implementation

for item-sets, we sidestep time bottleneck of low min. support with early iterations of candidate generation by using recommended pre-processing step of pruning frequent items with support greater than 1 / r and that have ancestors.

only items that are frequent are used for item-sets.

only item-sets that are r-interesting in terms of support and frequent are used for rules.

only rules that are r-interesting in terms of support and confidence are reported.

## note on close ancestor finding

we break problem of finding close ancestors for all n rectangles into problems of finding close descendants for a particular actual rectangle.

we note that our times involving r-tree and look-ahead will be off if dimension d is not moderately low and fixed; if dimension is tightly in O(n), we ought to introduce a factor of n for time.

### approach #1 -- graph and distance product

#### option #1 -- use brute-force

we note that brute force for transitive reduction of a DAG takes O(n ^ 3) time.

#### option #2 -- use approach that exploits sparsity

we may use a sparsity-exploiting algorithm for transitive reduction for a DAG. we do not consider this further, though it takes time in O(|V| \* |E|), which in principle is faster than O(n ^ 3). it's worth noting that via fischer/meyer 1971 transitive closure (which is closely related to transitive reduction) and lax boolean MM are mutually reduceable to each other and the latter is difficult to find significantly subcubic time algorithms for, so for worst-case input we should expect time nearly-cubic in n for transitive reduction of DAG for the short term.

we note that transitive reduction via lax boolean MM is about path of size >= 2 existence and path of size >= 1 existence.

### approach #2 -- heuristic approach with r-tree

assuming we have dimension d moderately low and fixed and not bound tightly by O(n), we can arrive at times that appear to be subcubic in n. we have two options -- both use an r-tree variant with bulk-loading e.g. via sort-tile-recursive (STR) approach via leutenegger 1997 and that is balanced and that is dynamic via bkd-tree-like occasional rebuilding (see procopiuc 2003) to support inserts and deletes in O(log(n) ^ 2) time. see guttman 1984 for details on standard r-tree. the main idea is that we find close descendants for each of n provided rectangles via a total of n close-descendant queries. we consider both options to involve heuristics because we may have many intermediate hunches for close-descendant that do not ultimately survive, even though subqueries have good guaranteed time for option one.

if we have pair-wise rectangles that do not frequently involve enclosure/containment and overlap is highly correlated with enclosure/containment, then it is conceivable that we can get better performance using r-tree via either of the two options for our approach. we note that a rectangle enclosure query asks for given a query rectangle rectangles that contain it and a rectangle containment query asks for given a query rectangle rectangles that fit in it. close-descendant query roughly works via a heuristic approach. we find primitive rectangles contained by query rectangle and use auxiliary queries to see if returned rectangles have parents that are contained by original query rectangle. the candidate close descendants we store in a "conflict" secondary r-tree for purpose of speeding up checks in form of enclosure subquery with early-stopping that determine whether a candidate parent encloses (and disqualifies) a candidate close descendant; we maintain this conflict tree via inserts and deletes. we note that when we encounter rectangles of same shape, we may choose to keep one of them arbitrarily. we use a best-first priority queue to guide bounding box consideration order; we prefer contained bounding boxes and we tie-break by preferring larger bounding box area (because it is harder to be a middle-man for a larger contained box).

#### option #1 -- use look-ahead

the first option is to use look-ahead for subqueries such as rectangle enclosure and rectangle containment in conjunction with corner transformation. close-descendant query would then not directly use look-ahead; its subqueries do. then, we have a coefficient of d for look-ahead-using queries for edge checks. we won't go into much detail about look-ahead except that it requires roughly disjoint bounding boxes for siblings (though shared edge is allowed) and that it is related to knowing that one child out of two subtrees definitely has a match (which is made more straightforward to notice assuming we also use corner transformation) via d edge checks at each node. it should be noted that without look-ahead enclosure and containment already take at least d time for each node for an r-tree. we modify enclosure subquery to use early-stopping, which leads time for such a query to be O(log(n)) instead of O(log(n) ^ 2). time for each close-descendant query is in O(k \* log(n) ^ 2), where k is number of hunch close-descendants s.t. k is in O(n). this means for n close-descendant queries overall we take time in O(k \* n \* log(n) ^ 2) = O(n ^ 2 \* log(n) ^ 2). since this is less than cubic in n (though we omit a factor of d assuming it is moderately low and fixed), this approach may be used to get better performance in practice. we have left out detail that for look-ahead-using enclosure/containment subqueries we may take non-constant time even if there are zero matches.

#### option #2 -- do not use look-ahead

the second option is to not use look-ahead and all we can say (without further simplifying assumptions) is that for each close-descendant query we have worst case of n hunches, each of which would then take O(log(n)) time to find (because we don't go down a branch more than once). we note that we assume that we do not use corner transformation. as a result, we have an exceedingly loose and pessimistic time bound of O(n \* log(n)) for attempt to disqualify a hunch close descendant via enclosure subquery with early-stopping. time for a close-descendant query then is bounded by O(k' \* n \* log(n)), where k' is worst-case number of hunches (i.e. n). time for n close-descendant queries then is bounded by O(k' \* n ^ 2 \* log(n)) = O(n ^ 3 \* log(n)). this figure is more than cubic in n (again noting that we omit a factor of d as it is moderately low and fixed), but the times for the approach are considerably pessimistic and we believe there is still a chance that it can perform well in practice w.r.t. brute-force. we show that this is plausible by now making a few assumptions, which we discuss below. while the first option does not take advantage of possibility that number of hunches can be significantly lower than n either, it has lower theoretical bounds because they take advantage of possibility that enclosure subquery with early-stopping for disqualifying a hunch close descendant can be guaranteed to be fast.

#### option #2 -- three assumptions

assumption "zero-overlap" says that boxes for children do not overlap except at a boundary unless we have a realized enclosure/containment relationship w.r.t. query rectangle -- this can only mostly be true because a real rectangle collection has a largest rectangle that cannot be enclosed and a smallest rectangle that cannot contain. we introduce b, which describes average false-positive-to-actual-positive ratio for believing that a child for a node is associated with a guaranteed match during disqualify attempt subquery s.t. b is in [0, 1]. time for second option close-descendant query is broken into two parts. the first part describes getting the hunches. the second part describes attempts to disqualify each hunch. the third part is to handle updates to conflict tree. assume number of hunches is k''. the time for the first part is O(k'' \* log(n)). the time for the second part is O(k'' \* (b + 1) ^ log(n) \* log(n)). the time for the third part is O(k'' \* log(n) ^ 2). the total time is loosely (assuming b is one) in O(k'' \* n \* log(n) ^ 2). the time for n close-descendant queries is O(k'' \* n ^ 2 \* log(n) ^ 2) = O(n ^ 3 \* log(n) ^ 2) if k'' is in O(n). this does not appear to be better than brute-force. if we make "zero-overlap" assumption, b is zero, which gives n close-descendant query time of O(k'' \* n \* log(n) ^ 2) = O(n ^ 2 \* log(n) ^ 2) if k'' is in O(n). the factor of log(n) ^ 2 (instead of log(n)) comes from insert/delete for conflict tree of hunch close descendants. this assumption can be true for rectangles for a hierarchy that is highly coherent -- i.e. one with many realized enclosure/containment relationships and good separation between rectangles that are not related via enclosure/containment.

we have two other assumptions -- "uniform sparsity" and "no pruning", each of which have secondary purposes that are related to our application of quantitative association rule mining. they allow us to tune to reduce work drastically given that the second option for close-descendant query can be very time-costly. specifically, say average number of partitions for a quantitative attribute (treating categorical attribute as possibly multiple two-partition quantitative attributes) is p; then, number of solid regions considered for each quantitative attribute is p ^ 2 -- all of which survive if we have "no pruning" assumption. as we reduce p, the space of all possible multi-dimensional rectangles shrinks and via "uniform sparsity" assumption for fixed n we have more collisions (i.e. possibly more enclosure/contain relationships) but number of rectangles (that are made of combinations of solid regions for different attributes) shrinks faster -- this means that w.r.t. close-descendant query the amount of time required we can drastically shrink by reducing average number of partitions $p$ slightly.

we ought to mention that originally we conceived of an assumption called "maximal disjointedness", which says that (i) bounding boxes overlap minimally with query rectangle unless we enclose query rectangle for enclosure query or we are contained by query rectangle for containment query; and (ii) bounding boxes for siblings s.t. neither sibling is contained in the other overlap minimally. this is a weaker form of "zero-overlap" assumption. we do not mention this assumption later.

post-script: quantitative attributes are more difficult to handle efficiently than categorical attributes because we can combine adjacent numerical values into solid ranges. then, say the number of distinct recognized values for a quantitative attribute is p -- then, because we have O(p) starts and O(p) ends, the number of ranges we may end up encountering is O(p ^ 2) if we have no alternate strategy for ignoring candidate ranges. these details are present directly in srikant/agrawal 1996 section 1.1.

#### miscellaneous shared details

the only reason we believe one might wish to not use option one is slightly more implementation difficulty. we don't often see a proposed algorithm that performs reporting and that has for each match a coefficient for time that is not one. still, the coefficient that we have of log(n) or log(n) ^ 2 is fine; log(n) ^ q for low q is often acceptable wherever we see O(1), as opposed to when we have e.g. n where we see O(1). in general, an r-tree is better than multi-layer segment tree for rectangle enclosure/containment/intersection queries or point domination query if d is less than log(n) ^ max(d - 1, 1) for d >= 1 given that for an r-tree we do not clone stored rectangles. option one and option two with assumptions imply that we appear to be better than brute-force given that it is appropriate to omit d.

see appendix a for details about look-ahead queries for rectangle enclosure/containment/intersection, point-dominance, close-descendant queries. times are O(k \* log(n) ^ 2) for each of those queries except for close-descendant query, where k is number of matches.

### miscellany regarding all approaches

note that approaches 2-1 and 2-2 can be strictly better than approaches 1-1 and 1-2.

we note that one example of a rectangle containment hierarchy DAG (which relies on requirement that rectangles are unique) is a linear hierarchy. if at all possible, we want to consider rectangles higher up in the hierarchy earlier for a close-descendant query.

for approach #2, for the sake of having vocabulary to describe close-descendant query, we introduce some terms. if we hit a conflict prune, we say we perform a "lower ricochet". lower ricochet takes advantage of conflict r-tree variant by saying that if an internal/leaf node has a containing actual rectangle in the conflict r-tree variant, we're not a close descendant candidate of the current start rectangle. "upper ricochet" is where we temporarily run out of contained rectangles and revert to enclosing rectangles.

we use approach 2-2 with an x-tree as our r-tree variant.

## appendix a: queries that use look-ahead queries

we assume we use an r-tree variant.

we do O(d) edge checks for each node to get look-ahead; we assume d is moderately low and fixed, so we leave it out for times. look-ahead gives us good theoretical time for a query. we use corner transformation to go from d-dimensional rectangle to (2 \* d)-dimensional points. we aim for balancedness, which means we may split up ties for a component inconsistently. we support enclosure, containment, dominance, close-descendant queries. note that e.g. intersection is hard to predict with local tests because stored composite boxes may contain voids. let us assume w.l.o.g. d == 2 -- this means points have dimension four. assume upper-left corner of rectangle is (x\_1, y\_1) and lower-right corner of rectangle is (x\_2, y\_2). then, a point image of a rectangle is (x\_1, y\_1, x\_2, y\_2). we have a query rectangle of (v\_1, v\_2, v\_3, v\_4) and a stored primitive rectangle of (v'\_1, v'\_2, v'\_3, v'\_4).

we remember that at least one point always exists on each bounding rectangle edge -- this allows us to be sure about knowing we will have a match in a subtree for at least one of two children.

assuming branching factor is two, we know that for at least one child we know using O(d) checks exactly if its subtree has a matching primitive for a certain type of query if (assuming rough disjointedness in bounding boxes -- we say roughly because an edge may be shared by two sibling bounding boxes):

1. rectangle enclosure (i.e. query rectangle is surrounded) - v\_i >= v'\_i for i in [1, d] AND v\_i <= v'\_i for i in [d + 1, 2 \* d] - query x interval and query y interval are smaller - assuming two dimensions (instead of four) with query x\_l at x axis and query x\_r at y axis, we are interested in quadrant III - have sure local pruning
2. rectangle containment (i.e. query rectangle surrounds) - v\_i <= v'\_i for i in [1, d] AND v\_i >= v'\_i for i in [d + 1, 2 \* d] - query x interval and query y interval are large - assuming two dimensions (instead of four) with query x\_l at x axis and query x\_r at y axis, we are interested in quadrant I - have sure local pruning
3. rectangle intersection - consider original rectangles -- for each interval (i.e. component pair) for original dimension we must lie in one of three quadrants (I, II, III) with a non-trivial origin - if we consider each three-quadrant group as combination of two half-spaces, then if we lie on a shared edge for an original pre-doubling dimension some edge will guarantee existence of a match for at least one child's subtree as long as we remember to logical-OR for green-light prediction for each half-space for an original dimension - have sure local pruning
4. point dominance (i.e. query point dominates a point in an r-tree) - point is inside orthant associated with a bounding box s.t. lower left of orthant and bounding box are aligned - assuming two dimensions (instead of four) with x at x axis and y at y axis, we are interested in quadrant I
5. rectangle close-descendant (i.e. query rectangle contains stored rectangles that are close descendant candidates) - consider rectangle containment - could have O(k) hunch primitive rectangles with k = O(n), each of which we do early-stopping enclosure queries that each take O(log(n) ^ 2) time (assuming we use look-ahead -- otherwise they each take O(log(n)) time with three assumptions as via approach 2-2) to see if we have a third rectangle that contains a hunch rectangle and that is enclosed by query rectangle (for purpose of disqualification) -- assuming we use look-ahead, this close-descendant query takes time in O(k \* log(n) ^ 2) time for each query, of which we have O(n), implying O(n ^ 2 \* log(n) ^ 2) time (with worst-case k) for all n close-descendant queries -- these overall times do not appear to be more than for brute force, but we are assuming dimension d is moderately low and fixed and not tightly in O(n) -- time without look-ahead query and with three assumptions as via approach 2-2 is O(n ^ 2 \* log(n))

again, a warning -- note that these values are missing a coefficient of d for edge checks at each node. even with this coefficient, these times are possibly better than they might be with a different approach, because an alternative (e.g. segment tree) requires coefficient of log(n) ^ d as opposed to d for r-tree with look-ahead. however, if d is in O(n) (for whatever reason) this means we need to include an extra factor of n for times.

it's worth considering that close-descendant can be solved via transitive reduction or (with low dimensions) pareto-point-finding/skyline algorithm.

it's worth considering that for low density we have two options - use r-tree the whole way (and this may give good time) or use sparsity-exploiting transitive reduction algorithm for a DAG. for high density, we use transitive reduction for DAG that takes time cubic in n.

we warn that when using look-ahead-using queries, we tend to use non-constant amount of time even if we have zero matches.

## references

1. agrawal and srikant: fast algorithms for mining association rules (1994)
2. berchtold et al.: the x-tree: an index structure for high-dimensional data (1996)
3. berchtold et al.: improving the query performance of high-dimensional index structures by bulk load operations (1998)
4. goebel: towards logarithmic search time complexity for r-trees (2007)
5. pagel et al.: the transformation technique for spatial objects revisited (1993)
6. procopiuc et al.: bkd-tree: a dynamic scalable kd-tree (2003)
7. srikant and agrawal: mining quantitative association rules in large relational tables (1996)
8. fischer and meyer: bolean matrix multiplication and transitive closure (1971)
9. leutenegger et al.: str: a simple and efficient algorithm for r-tree packing (1997)
10. procopiuc et al.: bkd-tree: a dynamic scalable kd-tree (2003)
11. guttman: r-trees: a dynamic index structure for spatial searching (1984)


