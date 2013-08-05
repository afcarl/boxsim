package experiments.interact;


// This file contains the java code for the simulation.
// It can be compiled and executed without dependency to Processing.

import java.io.IOException;
import java.util.zip.DataFormatException;
import java.util.ArrayList;

import playground.Playground;
import sockit.InputMessage;
//import sockit.OutputMessage;
import sockit.Server;

public abstract class Exp {

	public RunController rc;

    /* The simulation */
	public Playground playground;

    /* Server */
    protected Server server;
    protected int port;

    // FIXME Have a class protocol reading from a config file

    // Step configuration
    /** Duration of a simulation step **/
    public float STEP_FREQ = 60.0f;
    /** Number of physics iteration per step **/
    public int   STEP_ITER = 3;
    /** Number of constraint solver velocity phase per iteration **/
    public int   ITER_VEL  = 8;
    /** Number of constraint solver position phase per iteration **/
    public int   ITER_POS  = 3;

    /* Time in seconds since the last reset */
    protected float date  = 0.0f;
    /* the number of steps sinc the last reset */
    protected int   steps = 0;

    /** Scafolding experiment constructor */
    public Exp(int port, RunController rc) {
        this.rc = rc;

        server = new Server();
        server.start(port);
        this.port = port;

        this.createPlayground();
    }

    /**
     * If the main class does not run the main loop, call this method.
     */
    void mainLoop() {

    	while(true) {
        	update();
    	}
    }

    /**
     * Reset the simulation.
     */
    public void reset() {

    	this.date  = 0.0f;
    	this.steps = 0;

    	createPlayground();
    }

    /**
     * Reset the simulation.
     */
    public void reset(ArrayList<Float> init_pos) {

        this.date  = 0.0f;
        this.steps = 0;

        createPlayground(init_pos);
    }

    /** Initialize box2d physics and create the world */
    public abstract void createPlayground();
    public abstract void createPlayground(ArrayList<Float> init_pos);

    /**
     * Update the communications, and launch event.
     * This should be called at every couple of simulation steps.
     * @param steps  the number of steps since the start of the simulation.
     * @param date   the time elapsed in seconds since the start of the simulation.
     */
    public void update() {

    	this.updateMessages();
    	try { Thread.sleep(1); } catch (Exception e) {}
    }

    /**
     * Get new messages and launch their execution.
     */
    public void updateMessages() {
        int n = server.getNumberOfMessages();
        if (n > 0) {
            for (int i = 0; i < n; i++) {
                InputMessage in_msg = server.receive();
                if (in_msg == null) {
                    System.out.println("Fuck");
                }
                try {
                    this.processMessage(in_msg);
                }
                catch (DataFormatException e) {
                    System.out.println("    -> The message was not processed succesfully due to an message format error.");
                    e.printStackTrace();
                    //server.send(new OutputMessage(ERROR_TYPE));
                }
                catch (IOException e) {
                    System.out.println("    -> The message was not processed succesfully due to an IO error.");
                    e.printStackTrace();
                    //server.send(new OutputMessage(ERROR_TYPE));
                }
            }
        }
    }

    /**
     * Process messages, and take appropriate action (eventually sending replies)
     * Currently, the contract is that subsequent message do not change a message
     * effect.
     */
    protected abstract void processMessage(InputMessage msg)
         throws DataFormatException, IOException;
}