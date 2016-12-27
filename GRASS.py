# -*- coding: utf-8 -*-
#
#  GRAS Stemmer
#  Authors:   Federico Ghirardelli, Marco Romanelli
#  A.A.:      2016-2017
#

import getopt, sys
from os import path
from getopt import GetoptError, getopt
from collections import Counter
from igraph import *
from operator import itemgetter

##############################################################
###############   FUNCTIONS AND SUBROUTINES   ################
##############################################################

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

def lcs(x, y):
	n = lcp(x, y)
	return (x[n:], y[n:])

def cohesion(p_neighbors, v_neighbors):
	return (1 + len(set(p_neighbors).intersection(v_neighbors))) / len(v_neighbors)

def lexicon_parser(path, readnumbers=True):
	# assuming path is a regular file path
	words_lengths = []
	average_length = 0
	lexicon_n = 0
	lexicon = []

	fp = open(lexicon_path, "r")
	signature = [fp.readline() for i in range(0,2)]

	# verifying terrier lexicon's "signature" 
	if not ((signature[0][:23] == "Setting TERRIER_HOME to") and (signature[1][:20] == "Setting JAVA_HOME to")):
		print "- Error while parsing the lexicon."
		return [], 0

	for w in fp:
		word = w[:w.index(',')].strip()
		if word[0].isdigit() and not readnumbers:
			continue
		lexicon.append(word.decode("utf-8"))			# potrebbe portare a errori?
		words_lengths.append(len(word))

	fp.close()

	lexicon_n = len(lexicon)
	average_length = sum(words_lengths) / len(lexicon)

	return lexicon, average_length


def help_message():
	print "Usage: python GRASS.py -l <lexicon-path> [OPTIONS]\n"                 
	quit()


##############################################################
###############  			 MAIN   		  ################
##############################################################

# Default stemmer parameters
l = 5
l_forced = False
alpha = 6
delta = 0.8
readnumbers = True

# Other variables
cutoff = None


# Output file path
stems_file_path = "stems.txt"

if len(sys.argv) < 2:
	help_message()

# Overriding value if passed as argument in command line
lexicon_path = None
try:
	opts, args = getopt(sys.argv[1:], "l:", ["alpha=", "delta=", "l=", "cut-off=", "no-numbers"])
except GetoptError:          
	    help_message()
for opt, arg in opts:     
	if opt == "-l":
		if not ((type(arg) is str) and path.isfile(arg)):
			print "- Bad lexicon file."                        
			quit()
		lexicon_path = arg.strip()
	if opt == '--alpha':                
		alpha = int(arg) 
		print "+ [OPTION] Value of alpha overriden: %d." % alpha
	elif opt == '--l':                
		l = int(arg) 
		l_forced = True
		print "+ [OPTION] Value of l overriden: %d." % l
	elif opt == '--delta':                
		delta = float(arg)
		print "+ [OPTION] Value of delta overriden: %.1f." % delta
	elif opt == '--cut-off':                
		cutoff = int(arg)
		print "+ [OPTION] Cut-off value set: %d." % cutoff
	elif opt == '--no-numbers':                
		readnumbers = False
		print "+ [OPTION] Do not parse numbers." 

if lexicon_path is None:
	print "- Missing lexicon file."                        
	quit()

print "+ Parsing lexicon..."
lexicon, average_length = lexicon_parser(lexicon_path, readnumbers)
if len(lexicon) == 0:
	print "- Error while parsing the lexicon."
	quit()

print "+ Lexicon parsed (%d words)." % len(lexicon)

# updating l value if present
if not l_forced:
	l = average_length
	print "+ [OPTION] Value of l is now equal to the average word length (%d)." % l
del average_length

lexicon.sort() 			# sort lexicon

# limit cutoff to lexicon's length
if cutoff and cutoff > len(lexicon):
	cutoff = len(lexicon)

print "+ Clustering words in classes..."
classes = [[]]

# clustering words into classes
i = 0
j = 0
if not cutoff:
	cutoff = len(lexicon)
while i < cutoff:
	w1 = lexicon[i]
	w2 = lexicon[i+1] if (i < len(lexicon)-1) else ""
	classes[j].append(w1)
	if lcp(w1, w2) < l:
		classes.append([])
		j += 1
	i += 1

del classes[j]	# empty class
print "+ Done (%d word classes created)." % len(classes)


###################### Algorithm #1 ############################
print "+ Computing alpha-frequencies..."
frequencies = Counter({})
suffix_array = []
i = 0
for m in range(0, len(classes)):
	print "\t+ Working on class #%d" % m
	sys.stdout.write("\033[F")
	sys.stdout.flush()

	# computing pairs of suffixes (current class)
	suffix_array = [lcs(classes[m][j], classes[m][k]) for j in range(0, len(classes[m])) for k in range(j+1, len(classes[m]))]

	# combining two counters, local and global (so far)
	frequencies = frequencies + Counter(suffix_array)		

print "\t+ Working on class #%d" % len(classes)

# Removing suffixes with frequency less than alpha
print "\t+ Doing some improvement..."
temp = frequencies
frequencies = {k:v for k,v in temp.iteritems() if v >= alpha}

print "+ Done: %d alpha-suffixes found." % len(frequencies)

# Removing names (clear memory)
del temp
del suffix_array

print "+ Generating graph G=(V,E) ..."
# "Clearing" old classes

g = Graph(directed=False)

# creating a vertex foreach word in the lexicon
for i in range(0, cutoff):  
	g.add_vertex(lexicon[i])

print "\t+ |V|=%d" % len(g.vs)

# creating an edge foreach alpha-suffix:
# foreach pair of words in the lexicon...
# for i in range(0, len(lexicon)):
# 	for j in range(i+1, len(lexicon)):  
# 			suffix = lcs(lexicon[i], lexicon[j])
# 			print i, j
# 			if suffix in frequencies:
# 				w1 = lexicon[i]
# 				g.add_edge(lexicon[i], lexicon[j], weight=frequencies[suffix])

c_edge = 0
for m in range(0, len(classes)):
	alpha_suffix_array = [(classes[m][j], classes[m][k], lcs(classes[m][j], classes[m][k])) for j in range(0, len(classes[m]))
														for k in range(j+1, len(classes[m]))
							if lcs(classes[m][j], classes[m][k]) in frequencies]

	for w1, w2, suffix in alpha_suffix_array:
		print "\t+ Adding edge #%d" % c_edge
		sys.stdout.write("\033[F")
		sys.stdout.flush()
		c_edge += 1


		g.add_edge(w1, w2, weight=frequencies[suffix])
		
sys.stdout.write("\r\033[K")

# if something weird happened
if len(g.es) == 0:
	print "\t- The number of edges is equal to zero. Something wrong?"
	quit()
else:
	print "\t+ |E|=%d" % len(g.es)

# Removing names (clear memory)
del alpha_suffix_array
del classes
classes = []

###################### Algorithm #2 ############################
print "+ Identifyng classes..."
jj = 0
early_quitting = False
while (g.vcount() != 0) and not early_quitting:  #while pricipale (finche' il sottografo non e' vuoto
	S = []

	degree_list = g.degree() # lista dei gradi per ogni nodo
	index, value = max(enumerate(degree_list), key=operator.itemgetter(1)) # indice e valore del nodo con grado maggiore
	u = g.vs[index] 			# = pivot

	S.append(index)				# S={u}

	u_adjacency = g.neighbors(u)
	u_dec_adjacency = []
	for v in u_adjacency:
		edge_id = g.get_eid(u, v)
		w = g.es[edge_id]["weight"]
		u_dec_adjacency.append((v, w))

	u_dec_adjacency.sort(key=operator.itemgetter(1), reverse=True)	# ordino secondo il peso in ordine decrescente

	for (v, weight) in u_dec_adjacency:
		if cohesion(u_adjacency,g.neighbors(v)) >= delta:
			S.append(v)
		else:
			g.delete_edges(g.get_eid(u, v))

	# output class S
	classes.append([g.vs[v]["name"] for v in S])
	
	print "\t+ %d class created." % jj
	sys.stdout.write("\033[F")							# printing on the same line
	sys.stdout.flush()
	jj += 1

	# Rimuovo da G i veritici in S e gli archi incidenti
	g.delete_vertices(S)

	#print g
	# loop breaking
	if len(g.es) == 0:
		early_quitting = True

print "\t+ %d class created." % jj

# when quitting with early_quitting=True there're still vertex in the graph to be added in some class(es)
# I assume that there'd go in singleton sets ---> ???
if early_quitting:
	print "\t+ Adding additional %d singletons." % len(g.vs)
	for v in g.vs:
		classes.append([v["name"]])

# removing names
del g
print "+ Classed created."

print "+ Storing stems..."
output = []
for c in classes:
	if len(c) == 1:
		output.append((c[0], c[0]))
	else:
		for word in c[1:]:
			output.append((word, c[0]))

output.sort(key=operator.itemgetter(0))		# ordino le parole del dizionario (come in origine)

fp = open(stems_file_path, "w")
for word, stem in output:
	s = "%s\t%s\n" % (word, stem)
	fp.write(s.encode("utf-8"))

fp.close()

print "+ Done. Bye."
quit()