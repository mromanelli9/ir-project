#
#  Module:    GRASS (main module)
#  Authors:   Federico Ghirardelli, Marco Romanelli
#  A.A.:     2016-2017
#

from LCP import lcp
from CS import lcs
from collections import Counter
from igraph import *
import operator

l = 4
alpha = 1
gamma = 0.5

def printClass(classes):
	i=0
	for item in classes:
	    print "class ",
	    print i,
	    print " :",
	    print item
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
		g.vs[i]["word"] = lexicon[i]
		g.vs[i]["label"] = lexicon[i]

	i = 0
	j = 0
	k = 0
	for i in range(0, len(lexicon)):
		for j in range(i+1, len(lexicon)-1):  #scorro ogni coppia di parole
			prefix = lcs(lexicon[i], lexicon[j])
			if prefix in count:	# se la coppia prefissi e' in counter
				if( count[prefix]>= alpha): # se la frequenza della coppia e' almeno alpha
		    			g.add_edges([(i,j)]) # aggiungo l'arco che unisce le due parole
					g.es[k]["peso"] = count[prefix]  # peso = alpha-freq
					g.es[k]["label"] = [prefix, count[prefix]]
					k +=1

	###################### Algoritmo 2 ############################

	seq = g.vs.select()  # numero di nodi del grafo

	while not len(seq) == 0:  #while pricipale (finche' il sotto grafo non e' vuoto)
	
		S = []
		classe_S = []
		vicini_list = []
		pesoArchi = []
		dicNodoArco = {} # dizionario
		gradi = g.degree() # lista dei gradi per ogni nodo
		index, value = max(enumerate(gradi), key=operator.itemgetter(1)) # indice e valore del nodo con grado maggiore

		u = g.vs[index] 
		print "nodo con grado maggiore : ",
		print u["word"],
		print " index : ",
		print index
		S.append(index)
		classe_S.append(u["word"])
	
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
		dicNodoArco_sorted = sorted(dicNodoArco.items(), key=operator.itemgetter(1), reverse=True) 
		#print dicNodoArco_sorted

		# 4 :
		for nodo, peso in dicNodoArco_sorted:
			v = nodo
			vicini_v = g.neighbors(peso[2]) # vicini di v
			if cohesion(vicini_u, vicini_v) >= gamma:
				S.append(peso[2])
				classe_S.append(nodo["word"])
			else:
				delete_edges(peso[0])

		# 11 : Output the class S
		print "S : ",
		print classe_S

	
		# 12 : From G remove the vertices in S and their incident edges.
		#for el in S:
		g.delete_vertices(S)
			
		
		seq = g.vs.select() # aggiorno numero di nodi rimasti in G
		# non creo G' perche' ho gia' tolto i nodi da G


	layout = g.layout_circle()
	plot(g, layout = layout)
	
		
	

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

suffix_array = []

for m in range(0, len(classes), 1):
	for j in range(0, len(classes[m]), 1):
		for k in range(j+1, len(classes[m]), 1):
	    		
			suffix_array.append(lcs(classes[m][j], classes[m][k]))

counter = Counter(suffix_array)
print(counter)
print "\n\n"

generateGraph(lexicon, alpha, counter, gamma)

quit()