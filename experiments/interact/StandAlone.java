package experiments.interact;

/** Run the experiment without any display feedback.
 *  Perfect for clusters.
 */

public class StandAlone implements RunController {

    Exp exp;

    public static void main (String[] args){

    	int port = Integer.parseInt(args[0]);;
   	    if (args.length >= 1) {
   	    	try {
        		port = Integer.parseInt(args[0]);
        	} catch (NumberFormatException e) {
        	    System.err.println("Usage: exp.java PORT (must be an integer)");
        	    System.exit(1);
        	}
   	    }

   	    StandAlone sa = new StandAlone();
   	    sa.exp = new InteractExp(port, sa);

   	    while(true) {
   	    	sa.exp.update();
   	    }
    }

    public void registerSteps(int n) {

    	float timestep = 1.0f/(exp.STEP_ITER*exp.STEP_FREQ);

    	for (int i = 0; i < n; i++) {
    		exp.playground.cc.logSensors(exp.steps);
    		exp.playground.cc.update();

    		exp.date += timestep;
    		exp.steps += 1;

            for (int k = 0; k < exp.STEP_ITER; k++) {
            	exp.playground.step(timestep, exp.ITER_VEL, exp.ITER_POS);
            }
		}
    }

    public void reset() {
    }
}
