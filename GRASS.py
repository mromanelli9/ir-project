#!/Users/Marco/anaconda2/bin/python
from collections import Counter

def lcp(x, y):
	# len(x) must be < than len(y)
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

l = 4 			# thresold value for suffix pair identification (NB: default value)
alpha = 6		# suffix frequency cut-off

lexicon = []
classes = [[]]
alpha_frequencies = set()

# Grouping words in classes
lexicon_lengths = []
fp = open('English.dic', 'r')
for w in fp:
	word = w.strip()
	lexicon.append(w)

	lexicon_lengths.append(len(word))
fp.close()

print "Lexicon contain %d words." % len(lexicon)

# updating l value
l = sum(lexicon_lengths)/len(lexicon)

# clearing memomry
del fp
del lexicon_lengths

lexicon.sort()

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

del classes[j]		# empty class

print "%d classes are been created. (l=%d)" % (len(classes), l)

# Phase 1: Identify Suffix Pair
suffixes = []
for i in range(0, len(classes)):
	c_class = classes.pop()		# C_i

	for k in range(0, len(c_class)):
		for j in range(0, k):
			(w1, w2) = (c_class[j], c_class[k])
			
			r = lcp(w1, w2)
			pair = (w1[r:], w2[r:])
			suffixes.append(tuple((sorted(pair)))) 	# per sicurezza (doppioni in ordine inverso)

# Compute suffix pairs frequencies
n = len(suffixes)	# forcing floating operations
for k, val in Counter(suffixes).items():
	alpha_frequencies.add((k, val))

# clearing memory
del suffixes
del classes		# dopo servono? boh
#print alpha_frequencies
print "%d suffixes are been found. (alpha=%d)" % (len(alpha_frequencies), alpha)

print "End."
quit()