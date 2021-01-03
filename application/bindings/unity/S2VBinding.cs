using UnityEngine;
using System;
using System.Net;
using System.Net.Sockets;

/**
 * The Server class which will receive sensors data from Android smartphone.
 * The communication is made by UDP.
 * @author COGOLUEGNES Charles
 */

public class S2VBinding : MonoBehaviour {
    public string ipAddress = "192.168.1.67";
    public int port = 4269;
    byte[] buf;
    Socket socket;

    const short MAX_SIZE = 256;
    const byte TYPE_LINEAR_ACCELERATION = 10;
    const byte TYPE_PROXIMITY = 8;
    const byte TYPE_ROTATION_VECTOR = 11;
    const byte TYPE_SCREEN_SIZE = 37;
    const byte TYPE_SUB = 38;
    const byte TYPE_UNSUB = 39;
    const byte TYPE_POSITION = 40;

    public Transform trans;
    public float proximity;

    void Start() {
        this.gameObject.GetComponent<MeshRenderer>().enabled = false;
        createServer();
    }

    void Update() {
        if(socket.Available > 0) receive();
        this.transform.rotation = trans.rotation;
        this.transform.localScale = trans.localScale;
        this.transform.position = trans.position;
    }

    void OnDestroy() {
        socket.Send(new byte[] {TYPE_UNSUB});
    }

    void createServer() {
        //Creates UDP Server on local network
        socket = new Socket(AddressFamily.InterNetwork, SocketType.Dgram, ProtocolType.Udp);
        socket.Connect(new IPEndPoint(IPAddress.Parse(ipAddress), port));
        socket.Send(new byte[] {TYPE_SUB});
    }

    void receive() {
        buf = new byte[MAX_SIZE];
        socket.Receive(buf, 0, buf.Length, SocketFlags.None);
        process(buf);
    }

    void process(byte[] data) {
        byte[] cleaned = AfterType(data);
        switch(data[0]) {
            case TYPE_ROTATION_VECTOR:
                float[] rotation = GetRotationVector(cleaned, 0, 4);
                float xRot = rotation[0];
                float yRot = rotation[1];
                float zRot = rotation[2];
                float wRot = rotation[3];
                trans.localRotation = new Quaternion(xRot, yRot, zRot, wRot);
                break;
            case TYPE_SCREEN_SIZE:
                float[] size = GetScreenSize(cleaned, 0, 4);
                float height = size[0];
                float width = size[1];
                trans.localScale = new Vector3(width,height,0.007f);
                break;
            case TYPE_PROXIMITY:
                this.proximity = ToFloat(cleaned);
                break;
            case TYPE_LINEAR_ACCELERATION:
                // Not used for now
                float[] accel = GetAccel(cleaned, 0, 4);
                float xAcc = accel[0];
                float yAcc = accel[1];
                float zAcc = accel[2];
                break;
            case TYPE_POSITION:
                float[] position = GetPosition(cleaned, 0, 4);
                float xPos = position[0];
                float yPos = position[1];
                float zPos = position[2];
                trans.position = new Vector3(xPos, yPos, zPos);
                break;
        }
    }

    byte[] SubArray(byte[] data, int index, int length) {
        byte[] result = new byte[length];
        Array.Copy(data, index, result, 0, length);
        return result;
    }

    float ToFloat(byte[] data) {
        return BitConverter.ToSingle(data, 0);
    }

    byte[] AfterType(byte[] data) {
        return SubArray(data, 1, data.Length-1);
    }

    float GetFloat(byte[] data, int start, int size) {
        return ToFloat(SubArray(data, start, size));
    }

    float[] GetRotationVector(byte[] data, int start, int size) {
        return new float[] {
            GetFloat(data, start, size), // x
            GetFloat(data, start+size, size), // y
            GetFloat(data, start+size*2, size), // z
            GetFloat(data, start+size*3, size) // w
        };
    }

    float[] GetScreenSize(byte[] data, int start, int size) {
        return new float[] {
            GetFloat(data, start, size), // heigth
            GetFloat(data, start+size, size) // width
        };
    }

    float GetProximity(byte[] data) {
        return ToFloat(data);
    }

    float[] GetAccel(byte[] data, int start, int size) {
        return new float[] {
            GetFloat(data, start, size), // x
            GetFloat(data, start+size, size), // y
            GetFloat(data, start+size*2, size), // z
        };
    }

    float[] GetPosition(byte[] data, int start, int size) {
        return new float[] {
            GetFloat(data, start, size), // x
            GetFloat(data, start+size, size), // y
            GetFloat(data, start+size*2, size), // z
        };
    }
}
