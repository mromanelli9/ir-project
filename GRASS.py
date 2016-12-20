#
#  Authors:   Federico Ghirardelli, Marco Romanelli
#  A.A.:      2016-2017
#

import getopt, sys
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

def printClass(classes):
	i=0
	for item in classes:
	    print "class %i: %s" % (i, item)
	    i +=1


##############################################################
###############  			 MAIN   		  ################
##############################################################

# Default stemmer parameters
l = 4
alpha = 1 			# debugging iniziale
delta = 0.8

# Overriding value if passed as argument in command line
try:                                
	opts, args = getopt.getopt(sys.argv[1:], "", ["alpha=", "gamma=", "l="])
except getopt.GetoptError:          
	print "- Unknown command."                        
	quit()    

for opt, arg in opts:                
	if opt == '--alpha':                
		alpha = int(arg) 
	elif opt == '--l':                
		l = int(arg) 
	elif opt == '--gamma':                
		alpha = float(arg)

lexicon = ["leg", "legs", "legalize", "execute", "executive", "legal", "legging", "legroom", "legitimization", "legislations", "legendary", "executioner", "executable", "executed", "farmer", "farmhouse", "farmworks", "farming", "farms", "asian", "asiatic", "asianization", "india", "indian", "indianapolis", "indiana", "pieceworker", "piercings", "piercers", "pied", "indians", "indianina" , "legionnaire", "legitimized", "legitimator", "legalizer", "legalizing", "legwarmer", "leghorns" , "legally", "farmse", "barse" , "bars" ,"aaaa" , "aaaaa"]

#lexicon = ["legalize", "execute", "executive", "legal", "executioner", "executable", "executed"]
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

frequencies = {}
for m in range(0, len(classes), 1):
	for j in range(0, len(classes[m]), 1):
		for k in range(j+1, len(classes[m]), 1):
			w1 = classes[m][j]
			w2 = classes[m][k]
			pair = lcs(w1, w2)
			if pair not in frequencies.keys(): 
				frequencies.update({pair: ((w1, w2), 1)})
			else:
				(ws, freq) = frequencies[pair]
				frequencies.update({pair: (ws, freq + 1)})

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
while g.vcount() != 0:  #while pricipale (finche' il sottografo non e' vuoto)
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

	# Rimuovo da G i veritici in S e gli archi incidenti
	g.delete_vertices(S)

print
for c in classes:
	print "Stem: %s, parole: %s" % (c[0], c[1:]) 

quit()