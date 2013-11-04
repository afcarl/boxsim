package experiments.interact;

/**
 * Java code to run the experiment setup using Processing.
 * This is not a .pde file, and as such can't be used directly in Processing.
 */

import java.io.IOException;

import playground.Mouse;

import processing.core.*;
import procbox.*;

public class ProcSketch extends PApplet implements RunController {

    public static final long serialVersionUID = 2L;

    public InteractExp exp;
    public Render        render;
    public Mouse         mouse;

    private int remaining_steps;


    public void setup() {

    	// Treating cli args
    	int port = 1989;
        if (args.length >= 1) {
        	try {
        		port = Integer.parseInt(args[0]);
        	} catch (NumberFormatException e) {
        	    System.err.println("Usage: exp.java PORT (must be an integer)");
        	    System.exit(1);
        	}

        };

    	exp = new InteractExp(port, this);

        size((int) exp.playground.w, (int) exp.playground.h);
        smooth();
        rectMode(CENTER);

        mouse = new Mouse(exp.playground);
        render = new Render(this, mouse);

        remaining_steps = 0;

    }

    public void draw() {

        if (remaining_steps <= 0) {
            exp.updateMessages();
        } else {
            float timestep = 1.0f/(exp.STEP_ITER*exp.STEP_FREQ);
            exp.playground.cc.logSensors(exp.steps);
            exp.playground.cc.update();
            exp.date += timestep;
            exp.steps += 1;

            for (int i = 0; i < exp.STEP_ITER; i++) {
            	exp.playground.step(timestep, exp.ITER_VEL, exp.ITER_POS);
            }
            remaining_steps -= 1;
        }

        render.render(exp.playground);
        // System.out.println(exp.ballPos.bareRead().get(0).floatValue() + " " + exp.ballPos.bareRead().get(1).floatValue());

    }

    public void mousePressed() {
        if (!mouse.mousePressed(mouseX, mouseY)) {
        	try {
        	    exp.follow(mouseX, mouseY);
        	} catch (IOException e)
        	{}
        }
    }

    public void mouseReleased() {
        mouse.mouseReleased(mouseX, mouseY);
    }

    public void mouseDragged() {
        if (!mouse.mouseDragged(mouseX, mouseY)) {
            try {
                exp.follow(mouseX, mouseY);
            } catch (IOException e)
            {}
        }
    }

    public void registerSteps(int n) {
        remaining_steps += n;
    }

    public void reset() {
        mouse = new Mouse(exp.playground);
        render = new Render(this, mouse);
    }

    // Keyboard interaction code.
    public void keyPressed() {

        if (key == 'r') {
        	this.reset();
    	}
        if (key == 't') {
            this.remaining_steps += 60;
        }
    }

    public static void main(String args[]) {
    	String[] args_ext = new String[args.length+1];
    	args_ext[0] = "experiments.interact.ProcSketch";
    	System.arraycopy(args, 0, args_ext, 1, args.length);

    	PApplet.main(args_ext);
    }
}

