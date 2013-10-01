INT_CLASS := $(patsubst %.java,%.class,$(wildcard target/interact/*.java))

all: interact interact.jar

clean:
	rm -Rf target/*;

interact:
	javac -cp ext/procbox.jar:ext/sockit.jar experiments/interact/*.java -d target/;

interact.jar: $(INT_CLASS)
	mkdir -p target && \
	cd target/ && \
	mkdir -p inflate && \
	rm -Rf inflate/* && \
	unzip -q -o ../ext/procbox.jar -d inflate && \
	unzip -q -o ../ext/sockit.jar -d inflate && \
	cp -Rf experiments inflate/ && \
	cd inflate && \
	jar -cf ../interact.jar .; \
	cd .. && \
	cp interact.jar ../boxsim/boxsim/ && \
	rm -Rf inflate;
