package com.example.smartphonetovirtuality;

import androidx.annotation.RequiresApi;
import androidx.appcompat.app.AppCompatActivity;

import android.annotation.SuppressLint;
import android.app.AlertDialog;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.hardware.Sensor;
import android.hardware.SensorManager;
import android.os.Build;
import android.os.Bundle;
import android.widget.CompoundButton;
import android.widget.EditText;
import android.widget.Switch;

import java.util.ArrayList;

/**
 * Main Android activity.
 * @author COGOLUEGNES Charles
 */
public class MainActivity extends AppCompatActivity {
    private final MainActivity $this = this;
    private Intent intent;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        @SuppressLint("UseSwitchCompatOrMaterialCode")
        Switch connectSwitch = findViewById(R.id.connect_switch);
        connectSwitch.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
            /**
             * When the switch button has changed.
             * Starts the SensorsService when the switch is on and stop the service if it is off.
             * @param buttonView switch button.
             * @param isChecked if the switch is toggle.
             */
            @RequiresApi(api = Build.VERSION_CODES.O)
            public void onCheckedChanged(CompoundButton buttonView, boolean isChecked) {
                if(intent == null) intent = new Intent($this, SensorsService.class);
                if(isChecked) {
                    EditText ip = findViewById(R.id.ip_text);
                    EditText port = findViewById(R.id.port_text);
                    intent.putExtra("ip", ip.getText().toString());
                    intent.putExtra("port", Integer.parseInt(port.getText().toString()));
                    PackageManager manager = getPackageManager();
                    boolean hasRotationVector = ((SensorManager) getSystemService(SENSOR_SERVICE)).getDefaultSensor(Sensor.TYPE_ROTATION_VECTOR) != null;
                    boolean hasAccelerometer = manager.hasSystemFeature(PackageManager.FEATURE_SENSOR_ACCELEROMETER);
                    boolean hasProximity = manager.hasSystemFeature(PackageManager.FEATURE_SENSOR_PROXIMITY);
                    if(handleSensorsExist(hasRotationVector, hasAccelerometer, hasProximity)) startService(intent);
                }
                else stopService(intent);
            }
        });
    }

    /**
     * Check if sensors exist on the phone.
     * @param rotationVector if has rotation vector.
     * @param accelerometer if has accelerometer.
     * @param proximity if has proximity.
     * @return true if phone has every wanted sensors false if not.
     */
    private boolean handleSensorsExist(boolean rotationVector, boolean accelerometer, boolean proximity) {
        ArrayList<String> sensors = new ArrayList<>();
        if(!rotationVector) sensors.add("Rotation Vector");
        if(!accelerometer) sensors.add("Accelerometer");
        if(!proximity) sensors.add("Proximity");
        if(sensors.size() > 0){
            showSensorsNotFound(sensors.toArray(new String[0]));
            return false;
        }
        return true;
    }

    /**
     * Display a dialog showing what sensor(s) the phone does not have then quit the application.
     * @param sensors an array which contains the non present sensors.
     */
    private void showSensorsNotFound(String[] sensors) {
        String  listSensors = "";
        for(String s : sensors) listSensors += s+", ";
        listSensors = listSensors.substring(0, listSensors.length()-2);
        listSensors += '.';
        AlertDialog.Builder builder = new AlertDialog.Builder($this);
        builder
            .setMessage("Your device does not support the following sensor(s): "+listSensors)
            .setCancelable(false)
            .setPositiveButton("OK", (dialog, which) -> {
                dialog.dismiss();
                finish();
            });
        builder.show();
    }

    /**
     * Stop the service if it exists.
     */
    @Override
    protected void onDestroy() {
        super.onDestroy();
        if(intent != null) stopService(intent);
    }
}