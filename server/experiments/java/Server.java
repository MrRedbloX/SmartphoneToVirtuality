import java.io.IOException;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.ServerSocket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.net.DatagramPacket;

import javafx.application.Application;

/**
 * The Server class which will receive sensors data from Android smartphone.
 * The communication is made by UDP.
 * @author COGOLUEGNES Charles
 */
public class Server {
    private static final int port = 4269;
    private static int upd_count = 0;
    private boolean running = true;

    public static final int TYPE_ACCELEROMETER = 1;
    public static final int TYPE_ORIENTATION = 3;
    public static final int TYPE_PROXIMITY = 8;

    /**
     * Constructor of Server class.
     * First it prints the network address and port.
     * Then it triggers a method to follow the updates per second.
     */
    public Server() {
      print_addr();
      follow_updates();
    }

    /**
     * Print the network address and port of the server.
     */
    private void print_addr() {
      try(final DatagramSocket socket = new DatagramSocket()){
        socket.connect(InetAddress.getByName("8.8.8.8"), 10002);
        System.out.println(socket.getLocalAddress().getHostAddress()+":"+port);
      }
      catch (Exception e) {
        e.printStackTrace();
      }
    }

    /**
     * Starts the UDP server.
     * Run indefinitely or until the running variable is set to false.
     * When a result is given, it calls the process method.
     */
    public void startUDP() {
      try {
        DatagramSocket socket = new DatagramSocket(port);
        byte[] buf = new byte[256];
        while (running) {
          DatagramPacket packet = new DatagramPacket((sbyte[])(object) buf, buf.length);
          socket.receive(packet);
          upd_count++;
          packet = new DatagramPacket(buf, buf.length, packet.getAddress(), packet.getPort());
          String received = new String(packet.getData(), 0, packet.getLength());
          process(received.substring(0, received.indexOf('\0')));
          buf = new byte[256];
        }
        socket.close();
      }
      catch(Exception e) {
        e.printStackTrace();
      }
    }

    /**
     * Process the given String.
     * Parse the data and send to the GUI the changes of a sensor.
     * @param s a String of format: "<type:int>_(<val:float>)|(<x:float> <y:float> <z:float>)"
     */
    private void process(String s) {
      try {
        String[] splt = s.split("_");
        int type = Integer.parseInt(splt[0]);
        if(type == TYPE_PROXIMITY) GUI.setProximity(Float.parseFloat(splt[1]));
        else {
          String[] coords = splt[1].split(" ");
          float x = Float.parseFloat(coords[0]);
          float y = Float.parseFloat(coords[1]);
          float z = Float.parseFloat(coords[2]);
          if(type == TYPE_ACCELEROMETER) GUI.setAccelerometer(x, y, z);
          else if(type == TYPE_ORIENTATION) GUI.setOrientation(x, y, z);
        }
      }
      catch(Exception e) {
        e.printStackTrace();
      }
    }

    /**
     * Send to the GUI the number of updates per second.
     */
    private void follow_updates() {
      new Thread() {
        public void run() {
          while(true) {
            try {
              Thread.sleep(1000);
              GUI.setUps(upd_count);
              upd_count = 0;
            }
            catch(Exception e) {
              e.printStackTrace();
            }
          }
        }
      }.start();
    }

    /**
     * Static method which instanciates and start the server in a new thread.
     */
    private static void startServer() {
      new Thread() {
        public void run() {
          Server server = new Server();
          server.startUDP();
        }
      }.start();
    }

    /**
     * Main method.
     * First start the server.
     * Then launch the GUI.
     * @param args Arguments for the main program.
     */
    public static void main(String[] args) {
      startServer();
      Application.launch(GUI.class, args);
    }
}
