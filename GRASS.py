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
	n_suffix = lcp(x, y)

	copyX = x[n_suffix:]
	copyY = y[n_suffix:]

	if(copyX>copyY):
		return copyX, copyY
	else:
		return copyY, copyX

def cohesion(p_neighbors, v_neighbors):
	return (1 + len(set(p_neighbors).intersection(v_neighbors))) / len(v_neighbors)


##############################################################
###############  			 MAIN   		  ################
##############################################################

# Default stemmer parameters
l = 4
l_forced = False
alpha = 6
delta = 0.8

# Output file path
stems_file_path = "stems.txt"

# Overriding value if passed as argument in command line
lexicon_path = None
try:
	opts, args = getopt(sys.argv[1:], "l:", ["alpha=", "delta=", "l="])
except GetoptError:          
	print "- Unknown command."                        
	quit()    
for opt, arg in opts:     
	if opt == "-l":
		if not ((type(arg) is str) and path.isfile(arg)):
			print "- Bad lexicon file."                        
			quit()
		lexicon_path = arg.strip()
	if opt == '--alpha':                
		alpha = int(arg) 
	elif opt == '--l':                
		l = int(arg) 
		l_forced = True
	elif opt == '--delta':                
		alpha = float(arg)

if lexicon_path is None:
	print "- Missing lexicon file."                        
	quit()

print "+ Parsing lexicon..."

lexicon = []
lexicon_lengths = []
fp = open(lexicon_path, "r")
i = 0
for w in fp:
	word = w.strip()
	lexicon.append(word)
	lexicon_lengths.append(len(word))

	# blocco per debugging
	if i > 1000:
		break

fp.close()
print "+ Lexicon parsed."


# updating l value if present
if not l_forced:
	l = sum(lexicon_lengths)/len(lexicon)

classes = [[]]
# sort lexicon
lexicon.sort()

print "+ Clustering words..."
# clustering words into classes
i = 0
j = 0
while (i < len(lexicon)) and (i<1000):
	w1 = lexicon[i]
	w2 = lexicon[i+1] if (i < len(lexicon)-1) else ""
	classes[j].append(w1)
	if lcp(w1, w2) < l:
		classes.append([])
		j += 1
	i += 1

del classes[j]	# empty class
print "+ Done."

print "+ Computing alpha-frequencies..."
frequencies = {}
for m in range(0, len(classes), 1):
	for j in range(0, len(classes[m])):
		for k in range(j+1, len(classes[m])):
			w1 = classes[m][j]
			w2 = classes[m][k]
			pair = lcs(w1, w2)
			if pair not in frequencies.keys(): 
				frequencies.update({pair: ((w1, w2), 1)})
			else:
				(ws, freq) = frequencies[pair]
				frequencies.update({pair: (ws, freq + 1)})
print "+ Done."

print "+ Generating graph..."
# "Clearing" old classes
classes = []

g = Graph(directed=False)	
for i in range(0, len(lexicon)):  # creo un nodo per ogni parola
	g.add_vertex(lexicon[i])

# scorro ttute le coppie di suffissi
for sx, (words, f) in frequencies.items():
	# se la frequenza della coppia e' almeno alpha
	if f >= alpha:
		w1, w2 = words
		g.add_edge(w1, w2, weight=f)		 # aggiungo l'arco che unisce le due parole
											# con il peso dell'alpha-frequency

###################### Algoritmo 2 ############################
print "+ Identifyng classes..."
jj = 0
while g.vcount() != 0:  #while pricipale (finche' il sottografo non e' vuoto
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
			g.delete_edge(g.get_eid(u, v))

	# output class S
	classes.append([g.vs[v]["name"] for v in S])
	print "\t+ #%d class created." % jj
	sys.stdout.write("\033[F")							# printing on the same line
	#sys.stdout.flush()
	jj += 1

	# Rimuovo da G i veritici in S e gli archi incidenti
	g.delete_vertices(S)

# removing names
del g
print "+ Classed created."

print "+ Storing stems..."
fp = open(stems_file_path, "w")
for c in classes:
	for word in c[1:]:
		fp.write("%s\t%s\n" % (word, c[0]))

fp.close()

print "+ Done. Bye."
quit()