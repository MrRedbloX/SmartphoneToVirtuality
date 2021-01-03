package com.example.smartphonetovirtuality;

import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;

/**
 * UPD client which sends data to a UDP server.
 * @author COGOLUEGNES Charles
 */
public class Client {
    /**
     * Sends a message via a datagram packet through a datagram socket.
     * @param type a type of sensor.
     * @param data data of sensor.
     * @param ip the ip address of the server.
     * @param port the port of the server.
     */
    public static void sendUDP(byte type, float[] data, String ip, int port) {
        try {
            DatagramSocket socket = new DatagramSocket();
            byte[] buf = concatBytes(new byte[]{type}, floatsToBytes(data));
            DatagramPacket packet = new DatagramPacket(buf, buf.length, InetAddress.getByName(ip), port);
            socket.send(packet);
            socket.close();
        }
        catch (Exception e) {
            e.printStackTrace();
        }
    }

    private static byte[] floatsToBytes(float[] xs) {
        ByteBuffer buffer = ByteBuffer.allocate(xs.length * 4);
        buffer.order(ByteOrder.LITTLE_ENDIAN);
        for(float x : xs) buffer.putFloat(x);
        return buffer.array();
    }

    private static byte[] concatBytes(byte[] a, byte[] b) {
        return ByteBuffer.allocate(a.length + b.length).put(a).put(b).array();
    }
}

