#
#  Module:    LCP
#  Authors:   Federico Ghirardelli, Marco Romanelli
#  A.A.:     2016-2017
#

# Compute Longest Common Prefix
def lcp(x, y):
	# len(x) must be shorter than len(y)

	if not x or not y:
		return 0

	if len(x) > len(y):
		t = x
		x = y
		y = t

	i = 0
	while ((i < len(x)) and (x[i] == y[i])):
		i += 1

	return i




