import os
import traceback, random, time
import signal
import subprocess
import socket

import treedict

from toolbox import gfx
from sockit.client import Client
from sockit.outmsg import OutboundMessage

# Socket adress
IP = 'localhost'
PORT = 1989

# Protocol
MSG_HELLO     = 0  # Server available.            out   void
MSG_BYE       = 1  # Server ended.                out   void
MSG_ERROR     = 2  # Server encountered an error. out   string
MSG_EXIT      = 3
MSG_CONF      = 4  # Configure the server         out   list of floats
MSG_RESET     = 5  # Reset the simulation         in    void
MSG_SENSOR    = 6  # Simulation sensors           out   list of floats
MSG_ORDER     = 7  # Arm order                    in    list of floats
MSG_STEP      = 8  # Run simulation steps         in    int
MSG_RESULT    = 9  # Simulation results           out   list of floats
MSG_INVERSE   = 10 # Inverse request              out   list of floats
MSG_DISPLAY   = 11 # Overlay display request      out   list of floats

prefixcolor = gfx.purple

defaultcfg = treedict.TreeDict()
defaultcfg.java_output = False
defaultcfg.debug       = False

class BoxCom(object):
    """Handle all technical aspects of simulation instanciation and communication"""

    def __init__(self, sim, cfg, debug = False, java_output = False):
        self.sim = sim
        self.cfg = sim.cfg
        self.cfg.update(defaultcfg, overwrite = False)

        self.client = Client()

        port = self.find_port()
        self.simproc = self.launch_sim(port)

        self.connect(port)

    def print_debug(self, s):
        if self.cfg.debug:
            print("{}dbg{}: {}{}".format(gfx.red, gfx.end, s, '\033[K'))

    def print_status(self, s):
        if self.cfg.verbose:
            print("{}sim{}: {}{}".format(prefixcolor, gfx.end, s, '\033[K'))

    def find_port(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        sock.bind(('', 0))
        sock.listen(socket.SOMAXCONN)
        ipaddr, port = sock.getsockname()
        sock.close()
        return port

    def launch_sim(self, port):

        interact_file = os.path.dirname(__file__) + '/' + 'interact.jar'
        assert os.path.exists(interact_file), "The file {} does not exist. Did you build the java code ?".format(interact_file)

        if self.cfg.visu:
            cmd = "java -cp {} experiments.interact.ProcSketch {}".format(interact_file, port)
        else:
            cmd = "java -cp {} experiments.interact.StandAlone {}".format(interact_file, port)

        if self.cfg.java_output:
            DEVNULL = None
        else:
            DEVNULL = open(os.devnull, 'wb')
        proc = subprocess.Popen(cmd, stdout=DEVNULL,
                                shell=True, preexec_fn=os.setsid)

        time.sleep(5)
        return proc

    def receive_sensors(self):
        """Interprets and return results"""
        resmsg = self.client.sendAndReceive(OutboundMessage(MSG_SENSOR, []))
        assert resmsg.type == MSG_SENSOR

        results =  self.process_sensors(resmsg)
        self.print_debug("Received results: {}".format(", ".join(["%+2.1f" % e for e in results]),))

        return results

    def process_sensors(self, resmsg):
        n_feature = resmsg.readInt()
        feats = {}
        for _ in range(n_feature):
            name = resmsg.readString()
            assert name not in feats
            n_size = resmsg.readInt()
            feats[name] = tuple(resmsg.readDouble() for _ in range(n_size))

        return feats

    def send_order(self, init_pos, order, nsteps, conf):
        """Send an order, run nsteps, and return result"""


        self.print_debug("Reseting the simulation")
        resetMsg = self.client.sendAndReceive(OutboundMessage(MSG_RESET, [len(init_pos)] + init_pos + conf))
        assert resetMsg.type == MSG_SENSOR

        self.print_debug("Sending order({})".format(", ".join(["%+2.1f" % o for o in order]), prefixcolor, gfx.end))
        orderConfirm = self.client.sendAndReceive(OutboundMessage(MSG_ORDER, [len(order)]+order ))
        assert orderConfirm.type == MSG_ORDER

        self.print_debug("Requesting {} steps run".format(nsteps))
        stepConfirm = self.client.sendAndReceive(OutboundMessage(MSG_STEP, [nsteps]), timeout = 1000)
        assert stepConfirm.type == MSG_STEP

        return self.process_sensors(resetMsg), self.receive_sensors()

    def close(self):
        os.killpg(self.simproc.pid, signal.SIGTERM)

    def connect(self, port):
        b = self.client.connect(IP, port)

        try:
            if b:
                msg = self.client.sendAndReceive(OutboundMessage(type_msg=MSG_HELLO), timeout = 1.0)
                self.print_status("connected on port {}".format(self.client.port))
            else:
                self.print_status("ERROR")
        except KeyboardInterrupt:
            exit(1)
        except:
            traceback.print_exc()
            self.client.disconnect()

    def send_conf(self, conf):
        msg = self.client.sendAndReceive(OutboundMessage(MSG_CONF, [60.0, 3, 20, 20] + conf))
        assert msg.type == MSG_CONF

        reachable_space = ((msg.readDouble(), msg.readDouble()), (msg.readDouble(), msg.readDouble()))
        self.print_status("sent configuration {}".format(", ".join("{:+3.1f}".format(c_i) if type(c_i) == float else "{}".format(c_i) for c_i in [60.0, 3, 20, 20] + conf)))
        self.print_status("reachable space: x:({:+3.1f}, {:+3.1f}), y:({:+3.1f}, {:+3.1f})".format(
                          reachable_space[0][0], reachable_space[0][1], reachable_space[1][0], reachable_space[1][1]))
        return reachable_space

    def disconnect(self):
        self.print_status("disconnecting")

        msg = self.client.sendAndReceive(OutboundMessage(MSG_BYE, ["Bye Server !"]))
        assert msg.type == MSG_BYE

        self.client.disconnect()

        self.print_status("disconnected")
        self.close()
