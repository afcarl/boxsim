package experiments.interact;


// This file contains the java code for the simulation.
// It can be compiled and executed without dependency to Processing.

import java.io.IOException;
import java.util.ArrayList;
import java.util.LinkedList;
import java.util.zip.DataFormatException;

import org.jbox2d.common.Vec2;

import playground.Playground;
import playground.controllers.ArmController;
import playground.controllers.PIDController;
import playground.entities.Arm;
import playground.entities.BodyEntity;
import playground.entities.Ball;
import playground.entities.Box;
import playground.sensors.LogSensor;
import playground.sensors.PosSensor;
import playground.sensors.AngSensor;

import sockit.InputMessage;
import sockit.OutputMessage;

public class InteractExp extends Exp {


	protected boolean availInverse = false;

    /* The arm controler */
	public Arm arm;
    public ArmController armc;
    public PosSensor armPos;
    public AngSensor armAng;

    public ArrayList<Float> lengths;
    public float angle_limit;
    public int base_x, base_y;

    public ArrayList<ArrayList<Number>> toy_vectors;
    public ArrayList<BodyEntity> toys;
    public ArrayList<PosSensor> toySensors;

    // FIXME Have a class protocol reading from a config file
    /* Protocol         id    description                  dest  content */
    private static final int
        HELLO_TYPE    = 0,  // Server available.            out   void
        BYE_TYPE      = 1,  // Server ended.                out   void
        ERROR_TYPE    = 2,  // Server encountered an error. out   string
        MSG_EXIT      = 3,
        MSG_CONF      = 4,  // Configure the server         out   list of floats
        RESET_TYPE    = 5,  // Reset the simulation         in    void
        SENSOR_TYPE   = 6,  // Simulation sensors           out   list of floats
        ORDER_TYPE    = 7,  // Arm order                    in    list of floats
        STEP_TYPE     = 8,  // Run simulation steps         in    int
        RESULT_TYPE   = 9,  // Simulation results          out   list of floats
        MSG_INVERSE   = 10, // Inverse request             out   list of floats
        MSG_DISPLAY   = 11; // Overlay display request     out   list of floats

    public static final int
        AREA_SIZE = 800,
        WALL_SIZE = 50;

    /* Interact experiment constructor */
    public InteractExp(int port, RunController rc) {
    	super(port, rc);

        lengths = new ArrayList<Float>();
    }


    public void createPlayground() {
        ArrayList<Float> init_pos = new ArrayList<Float>();
        for(int i = 0 ; i < 6 ; i++){
            init_pos.add(new Float(0.0f));
        }
        createPlayground(init_pos);
    }

    /* Initialize box2d physics and create the world */
    public void createPlayground(ArrayList<Float> init_pos) {

        ArrayList<Float> lengths = new ArrayList<Float>();
        for (int i = 0; i < 6; i++) {
            lengths.add(new Float(52));
        }

        int   base_x          = AREA_SIZE/2;
        int   base_y          = 80;

        ArrayList<Number> toy_vector = new ArrayList<Number>();
        toy_vector.add(new Integer(0)); // toy_type
        toy_vector.add(new Float(AREA_SIZE/2 + 100)); // toy_x
        toy_vector.add(new Float(AREA_SIZE/2 - 50)); // toy_y
        toy_vector.add(new Float(40.0f)); // toy_size
        toy_vector.add(new Float(0.3f)); // toy_friction
        toy_vector.add(new Float(0.7f)); // toy_restitution
        toy_vector.add(new Float(1.0f)); // toy_density

        toy_vectors = new ArrayList<ArrayList<Number>>();
        toy_vectors.add(toy_vector);

        createPlayground(init_pos, lengths, base_x, base_y, toy_vectors);
    }


    //
    private ArrayList<Number> readToyVector(InputMessage msg)
        throws IOException
    {
        ArrayList<Number> toy_vector = new ArrayList<Number>();

        toy_vector.add(new Integer(msg.readInt()));  // toy_type

        toy_vector.add(new Float(msg.readInt()));    // toy_x
        toy_vector.add(new Float(msg.readInt()));    // toy_y
        toy_vector.add(new Float(msg.readDouble())); // toy_size

        toy_vector.add(new Float(msg.readDouble())); // toy_friction
        toy_vector.add(new Float(msg.readDouble())); // toy_restitution
        toy_vector.add(new Float(msg.readDouble())); // toy_density

        return toy_vector;
    }

    /**
     * Create a toy object on the scene from a toy vector
     * @param toy_vector  parameter vector for the toy, created using readToyVector()
     */
    private BodyEntity createToy(ArrayList<Number> toy_vector) {
        int toy_type = ((Integer)toy_vector.get(0)).intValue();

        float toy_x    = ((Float)toy_vector.get(1)).floatValue();
        float toy_y    = ((Float)toy_vector.get(2)).floatValue();
        float toy_size = ((Float)toy_vector.get(3)).floatValue();

        float toy_friction = ((Float)toy_vector.get(4).floatValue());
        float toy_restitution = ((Float)toy_vector.get(5).floatValue());
        float toy_density = ((Float)toy_vector.get(6).floatValue());

        BodyEntity ball;
        if (toy_type == 0) {
            ball = (BodyEntity) playground.add(new Ball(playground, toy_x, toy_y, toy_size/2.0f, false, 1.0f, 1.0f, toy_friction, toy_restitution, toy_density));
        } else {
            assert (toy_type == 1);
            ball = (BodyEntity) playground.add(new Box(playground, toy_x, toy_y, toy_size, toy_size, 75.0f, false, 1.0f, 1.0f, toy_friction, toy_restitution, toy_density));
        }

        return ball;
    }

    public void createPlayground(ArrayList<Float> init_pos, ArrayList<Float> lengths, int base_x, int base_y, ArrayList<ArrayList<Number>> toy_vectors) {

        playground = new Playground(AREA_SIZE, AREA_SIZE, WALL_SIZE);
        playground.setGravity(0.0f, 0.0f);
        assert(init_pos.size() == lengths.size());

            // Arm + control interface
        arm = (Arm) playground.add(new Arm(playground, lengths.size(), lengths, angle_limit, base_x, base_y, init_pos));
        armc = (PIDController) playground.add(new PIDController(arm, 0.85f, 0.001f, 5.0f));
        //armc = (ArmController) playground.add(new ArmController(arm));

            // Toy object

        toys = new ArrayList<BodyEntity>();
        for(ArrayList<Number> toy_vector : toy_vectors) {
            BodyEntity toy = createToy(toy_vector);
            toys.add(toy);
        }

            // Sensors
        for(int i = 0; i < arm.bodies.size()-1; i++) { // Sensors for intermediary joints
        	playground.add(new PosSensor(arm.bodies.get(i), 10000, 1));
        	playground.add(new AngSensor(arm.bodies.get(i), 10000, 1));
        }
        armPos  = (PosSensor) playground.add(new PosSensor(arm, 10000, 1));
        armAng  = (AngSensor) playground.add(new AngSensor(arm, 10000, 1));

        toySensors = new ArrayList<PosSensor>();
        for(BodyEntity toy : toys) {
            PosSensor toyPos = (PosSensor) playground.add(new PosSensor(toy, 1000, 1));
            toySensors.add(toyPos);
        }

        // int gpix = playground.cf.addGroup();
        // for (int i = 0; i < arm.bodies.size(); i++) {
        //     playground.cf.addEntityToGroup(arm.bodies.get(i), gpix);
        // }
    }

    /**
     * Update the communications, and launch event.
     * This should be called at every couple of simulation steps.
     * @param steps  the number of steps since the start of the simulation.
     * @param date   the time elapsed in seconds since the start of the simulation.
     */
    public void update(long steps, double date) {

    	this.updateMessages();
    }

    @Override
    public void reset(ArrayList<Float> init_pos) {

        this.date  = 0.0f;
        this.steps = 0;

        createPlayground(init_pos, lengths, base_x, base_y, toy_vectors);
    }


    protected OutputMessage processConf(InputMessage msg)
		throws IOException
	{
    	STEP_FREQ = (float)msg.readDouble();
    	STEP_ITER = msg.readInt();
    	ITER_VEL  = msg.readInt();
    	ITER_POS  = msg.readInt();

        int n = msg.readInt();
        lengths.clear();
        for(int i = 0; i < n; i++) {
            float l_i = (float)msg.readDouble();
            lengths.add(new Float(l_i));
        }

        angle_limit = (float)msg.readDouble();

        base_x = msg.readInt();
        base_y = msg.readInt();

        int toy_number = msg.readInt();
        //System.out.println(toy_number);
        toy_vectors = new ArrayList<ArrayList<Number>>();
        for(int i = 0; i < toy_number; i++) {
            toy_vectors.add(readToyVector(msg));
        }

        OutputMessage bound_msg = new OutputMessage(MSG_CONF);

        // Reachable limits
        bound_msg.appendDouble((double) WALL_SIZE);
        bound_msg.appendDouble((double) AREA_SIZE - WALL_SIZE);
        bound_msg.appendDouble((double) WALL_SIZE);
        bound_msg.appendDouble((double) AREA_SIZE - WALL_SIZE);

        return bound_msg;
	}

    /**
     * Process a message containing an arm order.
     * @param msg
     * @throws DataFormatException
     * @throws IOException
     */
    private void processOrder(InputMessage msg)
    	throws DataFormatException, IOException
    {
    	int i = msg.readInt();
        if (i % arm.size != 0) {
            System.out.println("ERROR : Arm order message does not contains the proper number of elements (expected multiple of "+armc.length()+", got " + i + ")");
            throw new DataFormatException();
        } else {
            ArrayList<Float> order = new ArrayList<Float>();
            for (int j = 0; j < i; j++) {
                order.add(new Float(msg.readDouble()));
            }
            armc.execute(order);
        }
    }

    private void processReset(InputMessage msg)
        throws DataFormatException, IOException
    {
        int pos_provided = msg.readInt();
        if (pos_provided == 0) {
            this.rc.reset();
        }
        else {
            ArrayList<Float> init_pos = new ArrayList<Float>();
            for (int i = 0; i < pos_provided; i++) {
                init_pos.add(new Float(msg.readDouble()));
            }
            this.reset(init_pos);
            this.rc.reset();
        }

    }


    /**
     * Run physics engine steps.
     * @param msg  message of type STEP_TYPE, containing an int describing
     * 		       the number of steps to run.
     * @throws IOException  if an error reading the message is encountered.
     */
    private void doSteps(InputMessage msg)
    	throws IOException
    {
    	int n = msg.readInt();
    	this.rc.registerSteps(n);
    }

    /**
     * Get the results from the sensors.
     * @param msg  The message asking for the result.
     * @return  the message with the result.
     */
    protected OutputMessage getResult(InputMessage msg) {

    	OutputMessage result = new OutputMessage(RESULT_TYPE);

    	int featSize = 0;
    	int historySize = -1;
    	// We assume each sensor has the same history length
    	for (LogSensor s : playground.cc.logSensors) {
    		featSize += s.lenght();
    		if (historySize == -1) {
    			historySize = s.historySize();
    		} else {
    			assert historySize == s.historySize();
    		}
    	}

    	result.appendInt(featSize);
    	for (int i = 0; i < featSize; i++) {
    		result.appendInt(i);
    	}

    	for (int k = 0; k < historySize; k++) {
    		result.appendInt(featSize);
    		for (LogSensor s : playground.cc.logSensors) {
                for (Float f : s.history().get(k)) {
    				result.appendDouble(f.floatValue());
    			}
    		}
    	}

    	return result;
    }

    /**
     * Get the readings from the sensors.
     * @param msg  The message asking for the readings.
     * @return  the message with the readings.
     */
    protected OutputMessage getSensors(InputMessage msg) {

    	OutputMessage readings = new OutputMessage(SENSOR_TYPE);

    	int featSize = 0;
    	// We assume each sensor has the same history length
    	for (LogSensor s : playground.cc.logSensors) {
    		featSize += s.lenght();
    	}

    	readings.appendInt(featSize);

    	for (LogSensor s : playground.cc.logSensors) {
    		for (Float f : s.bareRead()) {
    			readings.appendDouble(f.doubleValue());
    		}
    	}

    	return readings;
    }

    /**
     * Prepare the request for the inverse model.
     * Note that mouseX, mouseY is not the position we want to request,
     * since it has to be relative to the rest position of the arm.
     * @param mouseX  the coordinate of the mouse in x.
     * @param mouseY  the coordinate of the mouse in y.
     */
    public void follow(float mouseX, float mouseY) {
    	if (this.availInverse) {
    		this.playground.overlay.put("mouse", new Vec2(mouseX, mouseY));
            //Vec2 target = playground.cooP2W(x, y);
        	this.availInverse = false;

        	ArrayList<Integer> feats = new ArrayList<Integer>();
        	feats.add(new Integer(0));
        	feats.add(new Integer(1));
        	ArrayList<Float> values = new ArrayList<Float>();
        	values.add(new Float(mouseX-arm.origin.x));
        	values.add(new Float(mouseY-arm.origin.y));
        	sendInverseRequest(feats, values);
    	}
    }

    public void sendInverseRequest(ArrayList<Integer> feats, ArrayList<Float> values) {
    	OutputMessage invreqmsg = new OutputMessage(MSG_INVERSE);
    	invreqmsg.appendInt(values.size());
    	for (Integer i: feats) {
        	invreqmsg.appendInt(i.intValue());
    	}
    	invreqmsg.appendInt(values.size());
    	for (Float v: values) {
        	invreqmsg.appendDouble(v.floatValue());
    	}
    	server.send(invreqmsg);
    }

	@SuppressWarnings("unchecked")
    protected OutputMessage handleDiplayRequest(InputMessage msg)
    	throws IOException
    {
    	int rtype = msg.readInt();
    	//if (rtype.equals("history")) {
    	if (rtype == 1) {
    		int n = msg.readInt(); // how many points
        	if (!playground.overlay.containsKey("history")) {
    			playground.overlay.put("history", new ArrayList<Vec2>());
    		}
    		Object points = playground.overlay.get("history");

    		for (int i = 0; i < n; i++) {
        		float px = (float)msg.readDouble();
        		float py = (float)msg.readDouble();
        		((ArrayList<Vec2>) points).add(new Vec2(px+arm.origin.x, py+arm.origin.y));
    		}
        	OutputMessage resp = new OutputMessage(MSG_DISPLAY);
    		resp.appendBoolean(true);
    		return resp;
    	}
    	else {
        	OutputMessage resp = new OutputMessage(MSG_DISPLAY);
    		resp.appendBoolean(false);
    		return resp;
    	}
    }

    /**
     * Process messages, and take appropriate action (eventually sending replies)
     * Currently, the contract is that subsequent message do not change a message
     * effect.
     */
    protected void processMessage(InputMessage msg)
         throws DataFormatException, IOException
    {
        int type = msg.getType();
        String RED       = "\u001B[31m";
        String CLR_RESET = "\u001B[0m";

        System.out.println("STATUS : received message of type ("+type+") and length ("+msg.getLength()+")");

        switch(type) {
            case HELLO_TYPE:
            {
                server.send(new OutputMessage(HELLO_TYPE));
                System.out.println("STATUS : client connected and acknowledged on port "+this.port);
                break;
            }
            case BYE_TYPE:
            {
                server.send(new OutputMessage(BYE_TYPE));
                System.out.println("STATUS : client disconnected.");
                break;
            }
            case ERROR_TYPE:
            {
                String s = msg.readString();
                System.out.print(s);
                break;
            }
            case MSG_CONF:
            {
            	OutputMessage bound_msg = this.processConf(msg);
                server.send(bound_msg);
                break;
            }
            case RESET_TYPE:
            {
                this.processReset(msg);
                server.send(this.getSensors(msg));
                break;
            }
            case MSG_EXIT:
            {
                server.send(new OutputMessage(MSG_EXIT));
                System.exit(0);
            }
            case ORDER_TYPE:
            {
                this.processOrder(msg);
                server.send(new OutputMessage(ORDER_TYPE));
                break;
            }
            case STEP_TYPE:
            {
                this.doSteps(msg);
                server.send(new OutputMessage(STEP_TYPE));
            	break;
            }
            case RESULT_TYPE:
            {
            	OutputMessage result = this.getResult(msg);
                server.send(result);
            	break;
            }
            case SENSOR_TYPE:
            {
            	OutputMessage sensors = this.getSensors(msg);
                server.send(sensors);
            	break;
            }
            case MSG_INVERSE:
            {
            	this.availInverse = msg.readBoolean();
            	break;
            }
            case MSG_DISPLAY:
            {
            	OutputMessage display = this.handleDiplayRequest(msg);
                server.send(display);
            	break;
            }
            default:
            {
                System.out.println(RED + "ERROR : Unrecognized message type ("+type+")." + CLR_RESET);
                throw new DataFormatException();
            }
        }
    }
}