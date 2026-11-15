package com.dolgurum.bangguseok;

import android.content.Context;
import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;
import android.hardware.SensorManager;
import android.os.Handler;
import android.os.HandlerThread;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;

/** 걸음 칩 값을 한 번 읽어 옴 (최대 timeoutMs 기다림). 칩이 없거나 권한이 없으면 -1 */
public class StepReader {
    public static long readOnce(Context ctx, long timeoutMs) {
        SensorManager sm = (SensorManager) ctx.getSystemService(Context.SENSOR_SERVICE);
        if (sm == null) return -1;
        Sensor s = sm.getDefaultSensor(Sensor.TYPE_STEP_COUNTER);
        if (s == null) return -1;
        final long[] out = { -1 };
        final CountDownLatch latch = new CountDownLatch(1);
        HandlerThread ht = new HandlerThread("bgsj-steps"); ht.start();
        SensorEventListener l = new SensorEventListener() {
            @Override public void onSensorChanged(SensorEvent e) { out[0] = (long) e.values[0]; latch.countDown(); }
            @Override public void onAccuracyChanged(Sensor sensor, int accuracy) {}
        };
        try {
            if (!sm.registerListener(l, s, SensorManager.SENSOR_DELAY_NORMAL, new Handler(ht.getLooper()))) return -1;
            latch.await(timeoutMs, TimeUnit.MILLISECONDS);
        } catch (Exception ignored) {
        } finally {
            try { sm.unregisterListener(l); } catch (Exception ignored) {}
            ht.quitSafely();
        }
        return out[0];
    }
}
