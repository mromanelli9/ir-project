#
#  Authors:   Federico Ghirardelli, Marco Romanelli
#  A.A.:      2016-2017
#

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

def printClass(classes):
	i=0
	for item in classes:
	    print "class %i: %s" % (i, item)
	    i +=1

def cohesion(vicini_p, vicini_v):
	cohe = (1 + len(set(vicini_p).intersection(vicini_v))) / len(vicini_v)
	return cohe

def generateGraph(lexiconOriginal, alpha, count, neigh):

	g = Graph()	
	lexicon = lexiconOriginal
	g.add_vertices(len(lexicon))
	layout = g.layout_kamada_kawai()
	for i in range(0, len(lexicon)):  # creo un nodo per ogni parola
		g.vs[i]["name"] = lexicon[i]
		g.vs[i]["label"] = lexicon[i]

	k = 0
	# scorro ttute le coppie di suffissi
	for sx, (words, f) in count.items():
		# se la frequenza della coppia e' almeno alpha
		if f >= alpha:
			w1, w2 = words
			g.add_edge(w1, w2)		 # aggiungo l'arco che unisce le due parole
			g.es[k]["peso"] = count[sx][1]  # peso = frequenza
			g.es[k]["label"] = [sx, count[sx]]
			k += 1

	###################### Algoritmo 2 ############################

	while g.vcount() != 0:  #while pricipale (finche' il sottografo non e' vuoto)
	
		S = []
		classe_S = []
		vicini_list = []
		pesoArchi = []
		dicNodoArco = {} # dizionario
		gradi = g.degree() # lista dei gradi per ogni nodo
		index, value = max(enumerate(gradi), key=itemgetter(1)) # indice e valore del nodo con grado maggiore

		u = g.vs[index] 
		print "nodo con grado maggiore : ",
		print u["label"],
		print " index : ",
		print index
		S.append(index)
		classe_S.append(u["label"])
	
		vicini_u = g.neighbors(u) # lista posizioni dei vicini
		print "\n"
		print "nodi vicini a u: ",
		print vicini_u

		for el in vicini_u:
			# lista dei nodi vicini 
			vert = (g.vs.select(el)) #memorizzato come oggetto vertice
			edge = g.es.find(_between=((index,), (el,))) # edge(u,v)
			peso = edge["peso"]
			dicNodoArco[vert] = [edge, peso, el]

		#print dicNodoArco
		#ordina il dizionario per peso degli archi decrescente
		dicNodoArco_sorted = sorted(dicNodoArco.items(), key=itemgetter(1), reverse=True) 
		#print dicNodoArco_sorted

		# 4 :
		for nodo, peso in dicNodoArco_sorted:
			v = nodo
			vicini_v = g.neighbors(peso[2]) # vicini di v
			if cohesion(vicini_u, vicini_v) >= gamma:
				classe_S.append(nodo["label"])
			else:
				delete_edges(peso[0])

		# 11 : Output the class S
		classes.append(classe_S)
		print "S : ",
		print classe_S

	
		# 12 : From G remove the vertices in S and their incident edges.
		#for el in S:
		g.delete_vertices(S)
			
		# non creo G' perche' ho gia' tolto i nodi da G

	#layout = g.layout_circle()
	#plot(g, layout = layout)



##############################################################
###############  			 MAIN   		  ################
##############################################################

# Stemmer parameters
l = 4
alpha = 1 			# debugging iniziale
gamma = 0.8
	

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

generateGraph(lexicon, alpha, frequencies, gamma)

quit()