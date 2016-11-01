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


