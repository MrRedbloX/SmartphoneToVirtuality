package com.example.smartphonetovirtuality;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.Service;
import android.content.Context;
import android.content.Intent;
import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;
import android.hardware.SensorManager;
import android.os.AsyncTask;
import android.os.Build;
import android.os.IBinder;
import android.os.PowerManager;
import android.os.PowerManager.WakeLock;
import android.util.DisplayMetrics;

import androidx.annotation.Nullable;
import androidx.annotation.RequiresApi;
import androidx.core.app.NotificationCompat;


/**
 * An Android service aiming to send data of different sensors to a server.
 * When the service is on it has to be able to send sensors data in any condition (ex: screen lock).
 * @author COGOLUEGNES Charles
 */
public class SensorsService extends Service implements SensorEventListener {
    private static String ip;
    private static int port;
    private boolean running;
    private WakeLock wakeLock;
    private float max_proximity, min_proximity;

    private static final int TYPE_SCREEN_SIZE = 37;
    private static final float INCH_METER_CONST = 0.0254f;

    @Nullable
    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }

    /**
     * Binds the sensors.
     * Creates a notification on foreground.
     */
    @RequiresApi(api = Build.VERSION_CODES.O)
    @Override
    public void onCreate() {
        super.onCreate();
        bindSensors();
        startForeground(4269, createNotification());
    }

    /**
     * Acquire a lock on the CPU.
     * Gets the ip and port of the server device.
     * @param intent intent.
     * @param flags flags.
     * @param startId id.
     * @return a start id.
     */
    @RequiresApi(api = Build.VERSION_CODES.N)
    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        acquireLock();
        ip = intent.getStringExtra("ip");
        port = intent.getIntExtra("port", 0);
        trigger(TYPE_SCREEN_SIZE, screenSize());
        running = true;
        return Service.START_STICKY;
    }

    /**
     * Release the lock and stop the notification.
     */
    @RequiresApi(api = Build.VERSION_CODES.ECLAIR)
    @Override
    public void onDestroy() {
        super.onDestroy();
        running = false;
        wakeLock.release();
        stopForeground(true);
        stopSelf();
    }

    /**
     * Triggers a change when a sensor data has changed.
     * @param event the data of the sensor.
     */
    @RequiresApi(api = Build.VERSION_CODES.N)
    @Override
    public void onSensorChanged(SensorEvent event) {
        if(running) {
            switch (event.sensor.getType()) {
                case Sensor.TYPE_ROTATION_VECTOR:
                    trigger(Sensor.TYPE_ROTATION_VECTOR, event.values);
                    break;
                case Sensor.TYPE_LINEAR_ACCELERATION:
                    // Since acceleration is not used in the server yet it is not sent.
                    //trigger(Sensor.TYPE_LINEAR_ACCELERATION, event.values);
                    break;
                case Sensor.TYPE_PROXIMITY:
                    trigger(Sensor.TYPE_PROXIMITY, normalizeProximity(event.values[0]));
                    break;
                default:
                    System.out.println("Unhandled sensor.");
            }
        }
    }

    /**
     * Creates a listener for every used sensor.
     * Gets the min and max proximity.
     */
    @RequiresApi(api = Build.VERSION_CODES.LOLLIPOP)
    private void bindSensors() {
        SensorManager manager = (SensorManager) getSystemService(SENSOR_SERVICE);
        manager.registerListener(this, manager.getDefaultSensor(Sensor.TYPE_LINEAR_ACCELERATION), SensorManager.SENSOR_DELAY_NORMAL);
        manager.registerListener(this, manager.getDefaultSensor(Sensor.TYPE_ROTATION_VECTOR), SensorManager.SENSOR_DELAY_NORMAL);

        Sensor proximity = manager.getDefaultSensor(Sensor.TYPE_PROXIMITY);
        max_proximity = proximity.getMaximumRange();
        min_proximity = proximity.getMinDelay();
        manager.registerListener(this, proximity, SensorManager.SENSOR_DELAY_NORMAL);
    }

    /**
     * Normalize the given proximity with a max and a min proximity of the device.
     * @param proximity the given proximity.
     * @return an array of float which contains the normalize proximity.
     */
    private float[] normalizeProximity(float proximity) {
        return new float[] {(proximity - min_proximity) / (max_proximity - min_proximity)};
    }

    /**
     * Returns the size of the screen of the device.
     * @return an array which contains the height and the width in meters.
     */
    private float[] screenSize() {
        DisplayMetrics dm = getResources().getDisplayMetrics();
        return new float[] {dm.heightPixels / dm.xdpi * INCH_METER_CONST, dm.widthPixels / dm.ydpi * INCH_METER_CONST};
    }

    @RequiresApi(api = Build.VERSION_CODES.O)
    private Notification createNotification() {
        String channelId = "STVService";
        NotificationChannel channel = new NotificationChannel(channelId, "STV Service", NotificationManager.IMPORTANCE_DEFAULT);
        NotificationManager service = (NotificationManager) getSystemService(Context.NOTIFICATION_SERVICE);
        service.createNotificationChannel(channel);

        return new NotificationCompat.Builder(this, channelId)
                .setSmallIcon(R.drawable.ic_launcher_foreground)
                .setContentTitle("STV")
                .setContentText("Running")
                .setPriority(NotificationCompat.PRIORITY_HIGH)
                .setCategory(Notification.CATEGORY_SERVICE)
                .build();
    }

    /**
     * Acquires a lock on the CPU.
     */
    private void acquireLock() {
        PowerManager powerManager = (PowerManager) getSystemService(POWER_SERVICE);
        wakeLock = powerManager.newWakeLock(PowerManager.PARTIAL_WAKE_LOCK, "MyApp::MyWakelockTag");
        wakeLock.acquire(10*60*1000L /*10 minutes*/);
    }

    /**
     * Triggers a background task to send sensors data.
     * @param type the sensor which has changed.
     * @param data the coordinates or value of the sensor.
     */
    @RequiresApi(api = Build.VERSION_CODES.N)
    private void trigger(int type, float[] data) {
        float[] args = {type};
        new SensorsTask().execute(args, data);
    }

    private static class SensorsTask extends AsyncTask<float[], Void, Void> {

        /**
         * Sends the data via UDP to the server.
         * @param args the data.
         * @return Void.
         */
        @Override
        protected Void doInBackground(float[]... args) {
            Client.sendUDP((byte) Math.round(args[0][0]), args[1], ip, port);
            return null;
        }
        @Override
        protected void onPostExecute(Void aVoid) {
            super.onPostExecute(aVoid);
        }
    }

    @Override
    public void onAccuracyChanged(Sensor sensor, int accuracy) {}
}
