# this starts the java server only, for debugging purposes
# the first argument is the port number.
cd ../../;
java -cp target/interact.jar:ext/sockit.jar experiments.interact.StandAlone $1