JFLAGS = -cp ".:jgrapht-core-1.0.1.jar"
JENCFLAGS = -encoding UTF-8
JC = javac
JVM = java

.SUFFIXES: .java .class
.java.class:
	$(JC) $(JFLAGS) $(JENCFLAGS) *.java

CLASSES = GRASS.java
	#PThread.java

MAIN = GRASS

default: classes

classes: $(CLASSES:.java=.class)

run: classes
	set -e; \
    $(JVM) $(JFLAGS) $(MAIN) ${ARGS}

clean:
	$(RM) *.class
