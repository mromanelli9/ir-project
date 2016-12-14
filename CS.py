#
#  Module:    LCP
#  Authors:   Federico Ghirardelli, Marco Romanelli
#  A.A.:     2016-2017
#

from LCP import lcp

def lcs(x, y):

	copyX = ""
	copyY = ""
	
	n_suffix = lcp(x, y)

	copyX = x[n_suffix:]
	copyY = y[n_suffix:]

	if(copyX>copyY):
		return copyX, copyY
	else:
		return copyY, copyX



