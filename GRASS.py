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
from itertools import combinations, takewhile
import cPickle as pickle
from numpy import mean

# Set the interpreter's 'check interval', how often to perform periodic checks
sys.setcheckinterval = 1000

##############################################################
###############   FUNCTIONS AND SUBROUTINES   ################
##############################################################

# Compute Longest Common Prefix (index)
def lcp(x, y):
	# len(x) must be shorter than len(y)
	if not x or not y:
		return 0

	i = 0
	while ((i < len(x)) and (x[i] == y[i])): i += 1

	return i

# Compute Longest Common Suffix (pair of substrings)
def lcs(x, y):
	i = 0
	while ((i < len(x)) and (x[i] == y[i])): i += 1

	return (x[i:], y[i:])

# Compute cohesion function as described in the paper
def cohesion(p_neighbors, v_neighbors):
	return (1 + len(set(p_neighbors).intersection(v_neighbors))) / len(v_neighbors)

# Procedure for parsing the input (lexicon) file
def lexicon_parser(path, readnumbers=True, lower_bound=0, upper_bound=None):
	# assuming path is a regular file path
	lexicon = []

	fp = open(lexicon_path, "r")
	signature = [fp.readline() for i in range(0,2)]

	# verify terrier lexicon's "signature"
	# that means, check if it's a real terrier lexicon file
	if not ((signature[0][:23] == "Setting TERRIER_HOME to") and (signature[1][:20] == "Setting JAVA_HOME to")):
		print "- Error while parsing the lexicon."
		return [], 0

	# for every line
	for w in fp:
		try:
			word = w[:w.index(',')].strip()
		except:
			print "Oops!  word wrong at line %d" % pos		# if there's no ',' char
			sys.exit()
		if word[0].isdigit() and not readnumbers:
			continue
		lexicon.append(word.decode("utf-8"))

	fp.close()

	# cut lexicon with lower/upper bounds
	if lower_bound != 0:
		lexicon = lexicon[lower_bound:]
	if upper_bound != None:
		lexicon = lexicon[:(upper_bound-lower_bound)]

	average_length = int(mean([len(w) for w in lexicon]))

	return lexicon, average_length

# Show an help message
def help_message():
	print "Usage: python GRASS.py -l <lexicon-path> [OPTIONS]\n"
	sys.exit()


##############################################################
###############  			 MAIN   		  ################
##############################################################

# Default stemmer parameters
l = None
l_forced = False				# if True l will be computed as the average word length
alpha = 4
delta = 0.8
readnumbers = True

# other "global" variables
freq_filename_dump = "suffix_pair_freq_l-p1.txt"
freq_filename_load = None

# Output file path
stems_file_path = "stems.txt"

# Command line arguments parsing
if len(sys.argv) < 2:
	help_message()

# Overriding value if passed as argument in command line
lexicon_path = None
try:
	opts, args = getopt(sys.argv[1:], "l:", ["alpha=", "delta=", "l=", "no-numbers", "freq-file="])
except GetoptError:
	    help_message()
for opt, arg in opts:
	if opt == "-l":
		if not ((type(arg) is str) and path.isfile(arg)):
			print "- Bad lexicon file."
			sys.exit()
		lexicon_path = arg.strip()
	if opt == '--alpha':
		alpha = int(arg)
	elif opt == '--l':
		l = int(arg)
		l_forced = True
	elif opt == '--delta':
		delta = float(arg)
	elif opt == '--no-numbers':
		readnumbers = False
		print "+ [OPTION] Do not parse numbers."
	elif opt == '--freq-file':
		freq_filename_load = str(arg)
		print "+ [OPTION] Suffix pair frequencies file selected."

if lexicon_path is None:
	print "- Missing lexicon file."
	sys.exit()

# Read input lexicon
print "+ Parsing lexicon..."
lexicon, average_length = lexicon_parser(lexicon_path, readnumbers)

if len(lexicon) == 0:
	print "- Error while parsing the lexicon."
	sys.exit()

lexicon.sort() 			# sort lexicon

print "+ Lexicon parsed (%d words)." % len(lexicon)

# updating l value if l_forced=False
if not l_forced:
	l = average_length
del average_length

print "+ Parameters:"
print "\t+ l = %d" % l
print "\t+ alpha = %d" % alpha
print "\t+ delta = %.1f" % delta

print "+ Clustering words in classes..."
classes = [[]]

# clustering words into classes
i = 0
j = 0

while i < len(lexicon):
	# Compute lcp between every two consecutive words
	# and put them in the same class if lcp >= l
	w1 = lexicon[i]
	w2 = lexicon[i+1] if (i < len(lexicon)-1) else ""
	classes[j].append(w1)
	if lcp(w1, w2) < l:
		classes.append([])
		j += 1
	i += 1

del classes[j]	# empty class
print "+ Done (%d word classes created)." % len(classes)

# If no freq file found compute it:
if freq_filename_load == None:
###################### Algorithm #1 ############################
	print "+ Computing alpha-frequencies..."
	frequencies_temp = Counter({})
	append = list.append				# speed-up
	i = 0

	# loop for every class
	for m in range(0, len(classes)):
		suffix_array = []

		if len(classes[m]) == 1:
			continue

		# computing pairs of suffixes (current class)
		for w1, w2 in combinations(classes[m], 2):
			append(suffix_array, lcs(w1, w2))

		# combining two counters, local and global (so far)
		frequencies_temp = frequencies_temp + Counter(suffix_array)

	print "+ %d \"raw\" suffixes pair found." % len(frequencies_temp)

	# Storing "raw" suffix pair frequencies for further uses
	freq_filename_dump = freq_filename_dump.replace("p1", str(l))
	pickle.dump(frequencies_temp, open(freq_filename_dump, "wb"))

	# Removing names (clear memory)
	del suffix_array

else:
	# otherwise load it
	with open(freq_filename_load, "rb") as fp:
		frequencies_temp = pickle.load(fp)

	print "+ Load external \"raw\" suffix pair (%s)." % len(frequencies_temp)

# Removing suffixes with frequency less than alpha
print "\t+ Doing some improvement..."
frequencies = {k:v for k,v in frequencies_temp.iteritems() if v >= alpha}

print "+ Done: %d alpha-suffixes found." % len(frequencies)
del frequencies_temp

print "+ Generating graph G=(V,E) ..."
g = Graph(directed=False)

# adding a vertex for each word in the lexicon
for i in range(0, len(lexicon)):
	g.add_vertex(lexicon[i])

print "\t+ |V|=%d" % g.vcount()

# compute edges
for m in range(0, len(classes)):
	if len(classes[m]) == 1:
		continue

	# computing pairs of suffixes (current class)
	alpha_suffix_array = [(w1, w2) for w1, w2 in combinations(classes[m], 2) if lcs(w1, w2) in frequencies]

	# if there's a suffix pair with frequency greater than alpha
	# induced by the two words/nodes, then add an edge
	for w1, w2 in alpha_suffix_array:
		g.add_edge(w1, w2, weight=frequencies[lcs(w1, w2)])

# if something weird happened
if len(g.es) == 0:
	print "\t- The number of edges is equal to zero. Something wrong?"
	sys.exit()
else:
	print "\t+ |E|=%d" % g.ecount()

# Remove names (clear memory)
del alpha_suffix_array
del classes
classes = []

###################### Algorithm #2 ############################
print "+ Identifying classes..."
jj = 0
early_quitting = False

# while the graph is not empty
while (g.vcount() != 0) and not early_quitting:
	S = []

	degree_list = g.degree() # degree list for each node
	index, value = max(enumerate(degree_list), key=operator.itemgetter(1)) # index-value of maximum degree node
	u = g.vs[index] 			# = pivot

	S.append(index)				# S={u}

	# find the adjacency list for u and v
	u_adjacency = g.neighbors(u)
	u_dec_adjacency = []
	for v in u_adjacency:
		edge_id = g.get_eid(u, v)
		w = g.es[edge_id]["weight"]
		u_dec_adjacency.append((v, w))

	u_dec_adjacency.sort(key=operator.itemgetter(1), reverse=True)	# sort by decreasing weight

	# append node v to the class if choesion value is greater than delta
	for (v, weight) in u_dec_adjacency:
		if cohesion(u_adjacency,g.neighbors(v)) >= delta:
			S.append(v)
		else:
			g.delete_edges(g.get_eid(u, v))

	# output class S
	classes.append([g.vs[v]["name"] for v in S])

	# Remove from G vertexes which are in S and adjacent edges
	g.delete_vertices(S)

	# loop breaking
	if len(g.es) == 0:
		early_quitting = True

# when quitting with early_quitting=True there're still vertex in the graph to be added in some class(es)
# I assume that there'd go in singleton sets
if early_quitting:
	print "\t+ Adding additional %d singletons." % len(g.vs)
	classes += [[v["name"]] for v in g.vs]

# remove names (clear memory)
del g
print "+ Classed created."

print "+ Storing items..."
output = []

# create a word-stem list in order to sort it later
for c in classes:
	if len(c) == 1:
		output.append((c[0], c[0]))
	else:
		for word in c[1:]:
			output.append((word, c[0]))

output.sort(key=operator.itemgetter(0))		# ordino le parole del dizionario (come in origine)

# store the word - stem pairs in the lookup file
fp = open(stems_file_path, "w")
for word, stem in output:
	s = "%s\t%s\n" % (word, stem)
	fp.write(s.encode("utf-8"))

fp.close()

print "+ Done. Bye."
sys.exit()
