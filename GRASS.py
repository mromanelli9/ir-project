#
#  Module:    GRASS (main module)
#  Authors:   Federico Ghirardelli, Marco Romanelli
#  A.A.:     2016-2017
#

from LCP import lcp
from CS import lcs
from collections import Counter

def printClass(classes):
	i=0
	for item in classes:
	    print "class ",
	    print i,
	    print " :",
	    print item
	    i +=1
	

lexicon = ["leg", "legs", "legalize", "execute", "executive", "legal", "legging", "legroom", "legitimization", "legislations", "legendary", "executioner", "executable", "executed", "farmer", "farmhouse", "farmworks", "farming", "farms", "asian", "asiatic", "asianization", "india", "indian", "indianapolis", "indiana", "pieceworker", "piercings", "piercers", "pied", "indians", "indianina" , "legionnaire", "legitimized", "legitimator", "legalizer", "legalizing", "legwarmer", "leghorns" , "legally", "farmse", "barse" , "bars" ,"aaaa" , "aaaaa"]
l = 4		# thresold value for suffix pair identification ()
classes = [[]]


#print lexicon
lexicon.sort()
print "----------------------------------------------"
#print lexicon


i = 0
j = 0
while (i < len(lexicon)):
	w1 = lexicon[i]
	w2 = lexicon[i+1] if (i < len(lexicon)-1) else ""

	classes[j].append(w1)

	if lcp(w1, w2) < l:
		classes.append([])
		j += 1
	
	i += 1

del classes[j]	# empty class

printClass(classes)

suffix_array = []

for m in range(0, len(classes), 1):
	for j in range(0, len(classes[m]), 1):
		for k in range(j+1, len(classes[m]), 1):
	    		
			suffix_array.append(lcs(classes[m][j], classes[m][k]))

counter = Counter(suffix_array)
print(counter)

quit()





















