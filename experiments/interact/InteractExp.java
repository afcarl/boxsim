package experiments.interact;


// This file contains the java code for the simulation.
// It can be compiled and executed without dependency to Processing.

import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
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
import playground.sensors.VelSensor;

import sockit.InboundMessage;
import sockit.OutboundMessage;


public class InteractExp extends Exp {

    protected boolean availInverse = false;

    /* The arm controler */
    public Arm arm;
    public ArmController armc;
    public PosSensor armPos;
    public AngSensor armAng;

    public ArrayList<Float> lengths;
    public float angle_limit;
    public boolean arm_collisions;
    public int base_x, base_y;

    public ArrayList<Object> toy_vectors;
    public ArrayList<BodyEntity> toys;
    public ArrayList<PosSensor> toySensors;

    public ArrayList<String> channels;

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

        channels = new ArrayList<String>();

        playground = new Playground(AREA_SIZE, AREA_SIZE, WALL_SIZE);
    }


    public void createPlayground()
    {
        ArrayList<Float> init_pos = new ArrayList<Float>();
        for(int i = 0 ; i < 6 ; i++){
            init_pos.add(new Float(0.0f));
        }
        createPlayground(init_pos);
    }
    //
    // /* Initialize box2d physics and create the world */
    // public void createPlayground(ArrayList<Float> init_pos) {
    //
    //     ArrayList<Float> lengths = new ArrayList<Float>();
    //     for (int i = 0; i < 6; i++) {
    //         lengths.add(new Float(52));
    //     }
    //
    //     int   base_x          = AREA_SIZE/2;
    //     int   base_y          = 80;
    //
    //     ArrayList<Object> toy_vector = new ArrayList<Object>();
    //     toy_vector.add(new Integer(0)); // toy_type
    //     toy_vector.add(new String("")); // toy_name
    //     toy_vector.add(new Float(AREA_SIZE/2 + 100)); // toy_x
    //     toy_vector.add(new Float(AREA_SIZE/2 - 50)); // toy_y
    //     toy_vector.add(new Float(40.0f)); // toy_size
    //     toy_vector.add(new Float(0.3f)); // toy_friction
    //     toy_vector.add(new Float(0.7f)); // toy_restitution
    //     toy_vector.add(new Float(1.0f)); // toy_density
    //
    //     toy_vectors = new ArrayList<Object>();
    //     toy_vectors.add(toy_vector);
    //
    //     createPlayground(init_pos, lengths, base_x, base_y, toy_vectors);
    // }

    /**
     * Create a toy object on the scene from a toy vector
     * @param toy_vector  parameter vector for the toy, created using readToyVector()
     */
    private BodyEntity createToy(ArrayList<Object> toy_vector) {
        String toy_name = (String) toy_vector.get(0);
        String toy_type = (String) toy_vector.get(1);

        float toy_x    = ((Number) ((ArrayList<Object>) toy_vector.get(2)).get(0)).floatValue();
        float toy_y    = ((Number) ((ArrayList<Object>) toy_vector.get(2)).get(1)).floatValue();
        float toy_size = ((Number) toy_vector.get(3)).floatValue();

        float toy_friction        = ((Number) toy_vector.get(4)).floatValue();
        float toy_restitution     = ((Number) toy_vector.get(5)).floatValue();
        float toy_density         = ((Number) toy_vector.get(6)).floatValue();
        float toy_linear_damping  = ((Number) toy_vector.get(7)).floatValue();
        float toy_angular_damping = ((Number) toy_vector.get(8)).floatValue();

        BodyEntity toy;
        if (toy_type.toString().equals("ball")) {
            toy = (BodyEntity) playground.add(new Ball(playground, toy_name, toy_x, toy_y, toy_size/2.0f, false, toy_linear_damping, toy_angular_damping, toy_friction, toy_restitution, toy_density));
        } else {
            assert (toy_type.toString().equals("box"));
            toy = (BodyEntity) playground.add( new Box(playground, toy_name, toy_x, toy_y, toy_size, toy_size, 75.0f, false, toy_linear_damping, toy_angular_damping, toy_friction, toy_restitution, toy_density));
        }

        return toy;
    }

    public void createPlayground(ArrayList<Float> init_pos) {

        playground = new Playground(AREA_SIZE, AREA_SIZE, WALL_SIZE);
        playground.setGravity(0.0f, 0.0f);
        assert(init_pos.size() == lengths.size());

            // Arm + control interface
        arm = (Arm) playground.add(new Arm(playground, "arm", lengths.size(), lengths, angle_limit, base_x, base_y, init_pos));
        armc = (PIDController) playground.add(new PIDController(arm, 0.85f, 0.001f, 5.0f));

        if (!arm_collisions) {
            int armgrp = playground.cf.addGroup();
            for (Box b: arm.bodies) {
                playground.cf.addEntityToGroup(b, armgrp);
            }
            playground.cf.addEntityToGroup(arm.tip, armgrp);
        }

            // Toy object

        toys = new ArrayList<BodyEntity>();
        for(Object toy_vector : toy_vectors) {
            BodyEntity toy = createToy((ArrayList<Object>) toy_vector);
            toys.add(toy);
        }

            // Sensors
        for(int i = 0; i < arm.bodies.size()-1; i++) { // Sensors for intermediary joints
            playground.add(new PosSensor(arm.bodies.get(i), 10000000, 1));
            playground.add(new AngSensor(arm.bodies.get(i), 10000000, 1));
        }
        armPos  = (PosSensor) playground.add(new PosSensor(arm, 10000000, 1));
        armAng  = (AngSensor) playground.add(new AngSensor(arm, 10000000, 1));

		armPos  = (PosSensor) playground.add(new PosSensor(arm.tip, 10000000, 1));
        armAng  = (AngSensor) playground.add(new AngSensor(arm.tip, 10000000, 1));

        toySensors = new ArrayList<PosSensor>();
        int i = 0;
        for(BodyEntity toy : toys) {
            PosSensor toyPos = (PosSensor) playground.add(new PosSensor(toy, 1000000, 1));
            VelSensor toyVel = (VelSensor) playground.add(new VelSensor(toy, 1000000, 1));
            toySensors.add(toyPos);
            i++;
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

        createPlayground(init_pos);
    }


    protected OutboundMessage processConf(InboundMessage msg)
        throws IOException
    {
        STEP_FREQ = (float)msg.readDouble();
        STEP_ITER = msg.readInt();
        ITER_VEL  = msg.readInt();
        ITER_POS  = msg.readInt();

        ArrayList<Object> lengths_d = (ArrayList<Object>) msg.readArrayList();

        lengths.clear();
        for(Object d : lengths_d) {
            lengths.add(new Float(((Number)d).floatValue()));
        }

        ArrayList<Object> joint_limits = (ArrayList<Object>) msg.readArrayList();
        angle_limit = ((Number)joint_limits.get(1)).floatValue();

        ArrayList<Object> base_pos = (ArrayList<Object>) msg.readArrayList();
        base_x = ((Number)base_pos.get(0)).intValue();
        base_y = ((Number)base_pos.get(1)).intValue();

        arm_collisions = msg.readBoolean();

        toy_vectors = (ArrayList<Object>) msg.readArrayList();

        ArrayList<Object> channels_o = (ArrayList<Object>) msg.readArrayList();
        channels.clear();
        for(Object d : channels_o) {
            channels.add((String) d);
        }

        // Reachable limits
        ArrayList<ArrayList<Double>> bounds = new ArrayList<ArrayList<Double>>();
        ArrayList<Double> bounds_x = new ArrayList<Double>();
        bounds_x.add(new Double(WALL_SIZE));
        bounds_x.add(new Double(AREA_SIZE - WALL_SIZE));
        bounds.add(bounds_x);
        ArrayList<Double> bounds_y = new ArrayList<Double>();
        bounds_y.add(new Double(WALL_SIZE));
        bounds_y.add(new Double(AREA_SIZE - WALL_SIZE));
        bounds.add(bounds_y);

        HashMap<String, Object> context = new HashMap<String, Object>();
        context.put(new String("geobounds"), (Object) bounds);

        OutboundMessage context_msg = new OutboundMessage(MSG_CONF);
        context_msg.appendMap(context);
        return context_msg;
    }

    private ArrayList<Float> alo2alf(ArrayList<Object> alo) {
        ArrayList<Float> alf = new ArrayList<Float>();
        for (Object o : alo) {
            alf.add(new Float(((Number) o).floatValue()));
        }

        return alf;
    }

    /**
     * Process a message containing an arm order.
     * @param msg
     * @throws DataFormatException
     * @throws IOException
     */
    private void processOrder(InboundMessage msg)
        throws DataFormatException, IOException
    {
        ArrayList<Float>  start_pos = alo2alf((ArrayList<Object>) msg.readArrayList());
        ArrayList<Float>    end_pos = alo2alf((ArrayList<Object>) msg.readArrayList());
        ArrayList<Float> velocities = alo2alf((ArrayList<Object>) msg.readArrayList());

        assert  start_pos.size() == lengths.size();
        assert    end_pos.size() == lengths.size();
        assert velocities.size() == lengths.size();


        ArrayList<Float> order = new ArrayList<Float>();
        for(int i = 0; i < lengths.size(); i++) {
            order.add(end_pos.get(i));
            order.add(velocities.get(i));
        }

        this.reset(start_pos);
        this.rc.reset();
        armc.execute(order);
    }

    private OutboundMessage processReset(InboundMessage msg)
        throws DataFormatException, IOException
    {
        if (playground != null) {
            // do things
        }

        return new OutboundMessage(RESET_TYPE);
        // int pos_provided = msg.readInt();
        // if (pos_provided == 0) {
        //     this.rc.reset();
        // }
        // else {
        //     ArrayList<Float> init_pos = new ArrayList<Float>();
        //     for (int i = 0; i < pos_provided; i++) {
        //         init_pos.add(new Float(msg.readDouble()));
        //     }
        //     this.reset(init_pos);
        //     this.rc.reset();
        // }
    }


    /**
     * Run physics engine steps.
     * @param msg  message of type STEP_TYPE, containing an int describing
     *                the number of steps to run.
     * @throws IOException  if an error reading the message is encountered.
     */
    private void doSteps(InboundMessage msg)
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
    // protected OutboundMessage getResult(InboundMessage msg)
    //     throws IOException
    // {
    //
    //     OutboundMessage result = new OutboundMessage(RESULT_TYPE);
    //
    //     int featSize = 0;
    //     int historySize = -1;
    //     // We assume each sensor has the same history length
    //     for (LogSensor s : playground.cc.logSensors) {
    //         featSize += s.lenght();
    //         if (historySize == -1) {
    //             historySize = s.historySize();
    //         } else {
    //             assert historySize == s.historySize();
    //         }
    //     }
    //
    //     result.appendInt(featSize);
    //     for (int i = 0; i < featSize; i++) {
    //         result.appendInt(i);
    //     }
    //
    //     for (int k = 0; k < historySize; k++) {
    //         result.appendInt(featSize);
    //         for (LogSensor s : playground.cc.logSensors) {
    //             for (Float f : s.history().get(k)) {
    //                 result.appendDouble(f.floatValue());
    //             }
    //         }
    //     }
    //
    //     return result;
    // }

    /**
     * Get the readings from the sensors.
     * @param msg  The message asking for the readings.
     * @return  the message with the readings.
     */
    protected OutboundMessage getSensors(InboundMessage msg)
        throws IOException
    {
        OutboundMessage outmsg = new OutboundMessage(SENSOR_TYPE);

        HashMap<String, Object> readings = new HashMap<String, Object>();

        for (LogSensor s : playground.cc.logSensors) {
            for(String channel : this.channels){
                if(channel.compareTo(s.getName()) == 0){
                    readings.put(s.getName(), s.history());
                }
            }
        }

        readings.put(playground.cr.getName(), playground.cr.history());

        outmsg.appendMap(readings);

        return outmsg;
    }

    /**
     * Prepare the request for the inverse model.
     * Note that mouseX, mouseY is not the position we want to request,
     * since it has to be relative to the rest position of the arm.
     * @param mouseX  the coordinate of the mouse in x.
     * @param mouseY  the coordinate of the mouse in y.
     */
    public void follow(float mouseX, float mouseY)
        throws IOException
    {

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

    public void sendInverseRequest(ArrayList<Integer> feats, ArrayList<Float> values)
        throws IOException
    {
        OutboundMessage invreqmsg = new OutboundMessage(MSG_INVERSE);
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
    protected OutboundMessage handleDiplayRequest(InboundMessage msg)
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
            OutboundMessage resp = new OutboundMessage(MSG_DISPLAY);
            resp.appendBoolean(true);
            return resp;
        }
        else {
            OutboundMessage resp = new OutboundMessage(MSG_DISPLAY);
            resp.appendBoolean(false);
            return resp;
        }
    }

    /**
     * Process messages, and take appropriate action (eventually sending replies)
     * Currently, the contract is that subsequent message do not change a message
     * effect.
     */
    protected void processMessage(InboundMessage msg)
         throws DataFormatException, IOException
    {
        int type = msg.getType();
        String RED       = "\u001B[31m";
        String CLR_RESET = "\u001B[0m";

        //System.out.println("STATUS : received message of type ("+type+") and length ("+msg.getLength()+")");

        switch(type) {
            case HELLO_TYPE:
            {
                server.send(new OutboundMessage(HELLO_TYPE));
                System.out.println("STATUS: client connected and acknowledged on port "+this.port);
                break;
            }
            case BYE_TYPE:
            {
                server.send(new OutboundMessage(BYE_TYPE));
                System.out.println("STATUS: client disconnected.");
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
                OutboundMessage context = this.processConf(msg);
                server.send(context);
                break;
            }
            case RESET_TYPE:
            {
                server.send(this.processReset(msg));
                break;
            }
            case MSG_EXIT:
            {
                server.send(new OutboundMessage(MSG_EXIT));
                System.exit(0);
            }
            case ORDER_TYPE:
            {
                this.processOrder(msg);
                server.send(new OutboundMessage(ORDER_TYPE));
                break;
            }
            case STEP_TYPE:
            {
                this.doSteps(msg);
                server.send(new OutboundMessage(STEP_TYPE));
                break;
            }
            case SENSOR_TYPE:
            {
                OutboundMessage sensors = this.getSensors(msg);
                server.send(sensors);
                break;
            }
            // case RESULT_TYPE:
            // {
            //     OutboundMessage result = this.getResult(msg);
            //     server.send(result);
            //     break;
            // }
            // case MSG_INVERSE:
            // {
            //     this.availInverse = msg.readBoolean();
            //     break;
            // }
            // case MSG_DISPLAY:
            // {
            //     OutboundMessage display = this.handleDiplayRequest(msg);
            //     server.send(display);
            //     break;
            // }
            default:
            {
                System.out.println(RED + "ERROR : Unrecognized message type ("+type+")." + CLR_RESET);
                throw new DataFormatException();
            }
        }
    }
}