#!/Users/Marco/anaconda2/bin/python

def lcp(x, y):
	# len(x) must be < than len(y)
	if not x or not y:
		return 0

	if len(x) > len(y):
		t = x
		x = y
		y = t

	i = 0
	while ((x[i] == y[i]) and (i < len(x)-1)):
		i += 1

	return i

lexicon = ["leg", "legs", "legalize", "execute", "executive", "legal"]
l = 4 			# thresold value for suffix pair identification ()
classes = [[]]


#fp = open('English.dic', 'r')
#for word in fp:
#	lexicon.append(word.strip())
#fp.close()

print lexicon
lexicon.sort()
print lexicon

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

print classes

quit()