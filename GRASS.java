/*
  GRAS Stemmer (Java version)
  Authors:   Federico Ghirardelli, Marco Romanelli
  A.A.:      2016-2017
*/

import java.io.File;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.BufferedWriter;
import java.io.FileWriter;
import java.util.Properties;
import java.io.UnsupportedEncodingException;
import java.util.HashMap;
import java.util.Map;
import java.util.TreeMap;
import java.util.ArrayList;
import java.util.List;
import java.util.Set;
import java.util.Arrays;
import java.util.HashSet;
import java.util.Collections;
import java.util.Iterator;

// JGraphT graph library (jgrapht-core-1.0.1.jar)
import org.jgrapht.*;
import org.jgrapht.graph.*;
import org.jgrapht.Graph;
import org.jgrapht.alg.util.VertexDegreeComparator;
import org.jgrapht.alg.NeighborIndex;

public class GRASS
{
	private static String PROP_FILE = "config.properties";
	private static String stem_filename = "stem.txt";
	private static int l;
	private static int alpha;
	private static double delta;
	private static Boolean computeValuel;

	public static void main(String[] args) throws Exception
	{
		String lexicon_filename;
		ArrayList<String> lexicon;
		ArrayList<ArrayList<String>> wordClasses;
		ArrayList<ArrayList<String>> stemClasses;
		HashMap<ArrayList<String>, Integer> suffixes;
		SimpleWeightedGraph<String, DefaultWeightedEdge> graph;

		if (args == null || args.length != 1) {
			System.out.println("! Missing lexicon.");
			System.exit(0);
		}
		lexicon_filename = args[0];

		// Welcome message
		System.out.println("GRAS Stemmer (Java version)");
		System.out.println("Authors: Marco Romanelli, Federico Ghirardelli\n");

		// Load parameters from config file
		loadProperties();

		// read words from lexicon file
		System.out.println("+ Parsing lexicon file...");
		lexicon = readLexicon(lexicon_filename);
		System.out.printf("+ %d words found.\n", lexicon.size());
		if (computeValuel)	System.out.printf("\t+ l = %d (average word length)\n.", l);

		// sort lexicon (alphabetically)
		System.out.format("+ Sorting lexicon... (%d)\n", lexicon.size());
		Collections.sort(lexicon);

		// create the set of classes s.t. any two words in any class have the lcp of length > 3
		wordClasses = createWordClasses(lexicon, l);
		System.out.format("+ Classes created (%d).\n", wordClasses.size());

		// compute alpha frequencies
		System.out.println("+ Computing suffix alpha frequencies...");
		suffixes = computeSuffixesFrequencies(wordClasses);
		System.out.format("+ Done. (%d).\n", suffixes.size());

		// Generate graph
		System.out.println("+ Generating graph...");
		graph = generateGraph(wordClasses, suffixes);
		System.out.format("+ Done. (|V|=%d, |E|=%d)\n", graph.vertexSet().size(), graph.edgeSet().size());

		// "delete" unused objects
		lexicon = null;
		wordClasses = null;

		// Identify classes
		System.out.println("+ Identifying classes...");
		stemClasses = algorithm2(graph);
		System.out.format("+ Done. (%d).\n", stemClasses.size());

		// "delete" unused ojbects
		graph = null;

		// Writing to file...
		stem_filename += stem_filename.format("_%s_%s_0%s.txt", l, alpha, (int)(delta*10));
		System.out.printf("+ Writing stems to file \"%s\"\n", stem_filename);
		storeStems(stemClasses, stem_filename);
		System.out.println("+ Stems stored!");
		System.out.println("+ Bye!\n");
	}

	public static void loadProperties()
	{
		Properties prop = new Properties();
		FileInputStream input = null;

		try
		{
			input = new FileInputStream(PROP_FILE);

			// load a properties file
			prop.load(input);

			// get the property values
			l = Integer.parseInt(prop.getProperty("l"));
			alpha = Integer.parseInt(prop.getProperty("alpha"));
			delta = Double.parseDouble(prop.getProperty("delta"));
			computeValuel = prop.getProperty("auto-compute-l").equals("True") ? true : false;
			stem_filename = prop.getProperty("output-file");

			System.out.println("+ Parsing config.properties...");
			if (computeValuel)
				System.out.println("\t+ l will set to word avarage length.");
			else
				System.out.printf("\t+ l = %d (forced to this value)\n", l);

			System.out.printf("\t+ alpha = %d\n\t+ delta = %.2f\n", alpha, delta);

		}
		catch (IOException e)
		{
			System.out.format("! Error loading config.properties (%s).\n", e);
			System.exit(1);
		}
		finally
		{
			if (input != null) {
				try
				{
					input.close();
				}
				catch  (IOException e)
				{
					System.out.format("! Error loading config.properties (%s).\n", e);
				}
			}
		}
	}

	public static ArrayList<String> readLexicon(String filename) throws Exception
	{
		ArrayList<String> filedata = null;

		try
		{
			filedata = new ArrayList<String>();
			File fp = new File(filename);
			BufferedReader in = new BufferedReader(new InputStreamReader(new FileInputStream(fp), "UTF-8"));

			String line = null;
			String word = null;

			int i = 0;
			// Skip the first 2 lines
			while ((line = in.readLine()) != null && (i++ < 1)) continue;

			while ((line = in.readLine()) != null) {
				word = line.split(",")[0];
				filedata.add(word);
			}
		}
		catch (UnsupportedEncodingException e)
		{
			System.out.println("! UTF-8 decoding error: " + e.getMessage());
		}
		catch (IOException e)
		{
			System.out.println("! IO exception error: " + e.getMessage());
		}
		catch(Exception e)
		{
			System.out.println("! Unknown error: "+ e.getMessage());
		}
		finally
		{
			if ((filedata == null) || filedata.isEmpty()) System.exit(2);
		}

		// Compute l value (average word length)
		if (computeValuel)
		{
			int sum = filedata
				.stream()
				.mapToInt(w -> w.length())
				.sum();

			l = sum / filedata.size();
		}

		return filedata;
	}

	public static ArrayList<ArrayList<String>> createWordClasses(ArrayList<String> lexicon, int threshold)
	{
		String w1, w2 = null;
		ArrayList<ArrayList<String>> allClasses = new ArrayList<ArrayList<String>>();
		ArrayList<String> singleClass = new ArrayList<String>();

		int i = 0;
		int lexicon_size = lexicon.size();

		lexicon.add(lexicon_size, "");		// così controlla anche l'ultima parola

		while (i < lexicon_size)
		{
			w1 = lexicon.get(i);
			w2 = lexicon.get(i+1);
			singleClass.add(w1);

			if (longestCommontPrefix(w1, w2) < threshold)
			{
				allClasses.add(singleClass);
				singleClass = new ArrayList<String>();
			}

			i++;
		}

		lexicon.remove(lexicon_size);		// il lexicon torna quello vero

		return allClasses;
	}

	public static HashMap<ArrayList<String>, Integer> computeSuffixesFrequencies(ArrayList<ArrayList<String>> wClasses)
	{
		HashMap<ArrayList<String>, Integer> suffixes = new HashMap<ArrayList<String>, Integer>();
		ArrayList<String> currentClass = new ArrayList<String>();
		ArrayList<String> pair = null;
		String w1, w2, s1, s2;
		int i, j, k, lcp;
		Integer oldPairFreq;

		for (i = 0; i < wClasses.size(); i++)
		{
			currentClass = wClasses.get(i);

			for (k = 0; k < currentClass.size(); k++)
			{
				w1 = currentClass.get(k);
				for (j = 0; j < k; j++)
				{
					w2 = currentClass.get(j);
					lcp = longestCommontPrefix(w2, w1);
					s1 = w1.substring(lcp);
					s2 = w2.substring(lcp);
					pair = new ArrayList<String>();
					pair.add(s1);
					pair.add(s2);

					oldPairFreq = suffixes.put(pair, 1);
					if (oldPairFreq != null)
						suffixes.put(pair, oldPairFreq + 1);
				}
			}
		}

		return suffixes;
	}

	public static SimpleWeightedGraph<String, DefaultWeightedEdge> generateGraph(ArrayList<ArrayList<String>> wordClasses, HashMap<ArrayList<String>, Integer> suffixes)
	{
		SimpleWeightedGraph<String, DefaultWeightedEdge> graph = new SimpleWeightedGraph<String, DefaultWeightedEdge>(DefaultWeightedEdge.class);
		DefaultWeightedEdge edge;
		ArrayList<String> pair = null;
		String w1, w2, s1, s2;
		int lcp;
		Integer pairFreq;

		// adding vertices
		for (ArrayList<String> currentClass : wordClasses)
			for (String word: currentClass)
				graph.addVertex(word);

		System.out.println("+ Vertexes created... ");
		System.out.println("+ Adding edges... ");

		// adding edges (WARNING: bottleneck!)
		for (ArrayList<String> currentClass : wordClasses)
		{
			if (currentClass.size() == 1) continue;

			for (int i = 0; i < currentClass.size(); i++)
			{
				for (int j = 0; j < i; j++)
				{
					w1 = currentClass.get(i);
					w2 = currentClass.get(j);
					lcp = longestCommontPrefix(w2, w1);
					s1 = w1.substring(lcp);
					s2 = w2.substring(lcp);
					pair = new ArrayList<String>();
					pair.add(s1);
					pair.add(s2);

					pairFreq = suffixes.get(pair);
					if ((pairFreq != null) && (pairFreq >= alpha))
					{
						edge = graph.addEdge(w2, w1);
						graph.setEdgeWeight(edge, pairFreq);
					}
				}
			}
		}

		return graph;
	}

	public static ArrayList<ArrayList<String>> algorithm2(SimpleWeightedGraph<String, DefaultWeightedEdge> graph)
	{
		ArrayList<ArrayList<String>> classes = new ArrayList<ArrayList<String>>();
		ArrayList<String> s;
		HashSet<String> adjU, adjV, intersection;
		VertexDegreeComparator comparator = new VertexDegreeComparator(graph, VertexDegreeComparator.Order.ASCENDING);
		String u;
		double chs;

		while (graph.vertexSet().size() > 0)
		{			// u <-- vertex with maximum degree in G
			u = Collections.max(graph.vertexSet(), comparator);
			s = new ArrayList<String>();

			// s = S (current class)
			s.add(u);

			// for all v in Adjacent(u)...
			adjU = new HashSet<String>(Graphs.neighborListOf(graph, u));

			// taken in decrease order of w(u,v)...
			adjU = weightDecreaseOrdering(graph, adjU, u);

			for (String v : adjU)
			{
				adjV = new HashSet<String>(Graphs.neighborListOf(graph, v));
				intersection = new HashSet<String>(adjU);
				intersection.retainAll(adjV);
				chs = cohesion(intersection.size(), adjV.size());

				if (chs > delta)
					s.add(v);
				else
					graph.removeEdge(graph.getEdge(u, v));
			}

			// Store class S
			classes.add(s);

			// From G remove the vertices in S and their incident edges.
			for (String x : s)
			{
				adjV = new HashSet<String>(Graphs.neighborListOf(graph, x));
				for (String y : adjV)
					graph.removeEdge(graph.getEdge(x, y));
				graph.removeVertex(x);
			}

			if (graph.edgeSet().size() == 0)
			{
				System.out.println("+\t Optimizing...");
				for (String v : graph.vertexSet())
					classes.add(new ArrayList<String>(Arrays.asList(v)));
				break;
			}
		}

		return classes;
	}

	public static HashSet<String> weightDecreaseOrdering(SimpleWeightedGraph<String, DefaultWeightedEdge> graph, HashSet<String> adj, String v)
	{
		HashSet<String> rlist = new HashSet<String>();
		HashMap<String, Integer> map = new HashMap<String, Integer>();
		DefaultWeightedEdge edge;
		Iterator iterator;
		int w;

		for (String u : adj)
		{
			edge = graph.getEdge(v, u);
			w = (int) graph.getEdgeWeight(edge);
			map.put(u, w);
		}

		iterator = map.entrySet().iterator();
		while(iterator.hasNext())
		{
			Map.Entry value = (Map.Entry)iterator.next();
			rlist.add((String) value.getKey());
		}

		return rlist;
	}

	public static int longestCommontPrefix(String a, String b)
	{
		if ("".equals(a) || "".equals(b)) return 0;
		if (a.length() > b.length())
		{
			String x = a;
		 	a = b;
		 	b = x;
		}

		int i, a_n;
		a_n = a.length();

		i = 0;
		while ((i < a_n) && (a.charAt(i) == b.charAt(i))) i++;

		return i;
	}

	public static double cohesion(int adjIntersection, int adjV)
	{
		double chs;

		chs = (1 + adjIntersection) / adjV;

		return chs;
	}

	public static void storeStems(ArrayList<ArrayList<String>> classes, String filename)
	{
		ArrayList<String> output = new ArrayList<String>();
		BufferedWriter buffer = null;
		Iterator iter;
		String stem, s;
		FileWriter fw;
		File fp;

		// Sorting words
		for (ArrayList<String> cc : classes)
		{

			stem = cc.get(0);
			if (cc.size() == 1)
				s = stem + "\t" + stem + "\n";
			else
			{
				s = new String();
				iter = cc.listIterator();
				iter.next();
				while (iter.hasNext())
					s += iter.next() + "\t" + stem + "\n";
			}
			output.add(s);
		}
		Collections.sort(output);

		 try
		 {
			 fp = new File(filename);
			 fp.createNewFile();
			 fw = new FileWriter(fp);
			 buffer = new BufferedWriter(fw);

			 for (String line : output)
			 	buffer.write(line);
		 }
		 catch (IOException e)
		 {
			 System.out.format("! IO Error: %s\n", e);
		 }
		 finally
		 {
			 try
			 {
				 if (buffer != null) buffer.close();
			 }
			 catch (IOException e)
			 {
				  System.out.format("! IO Error: %s\n", e);
			 }
		 }
	}
}
