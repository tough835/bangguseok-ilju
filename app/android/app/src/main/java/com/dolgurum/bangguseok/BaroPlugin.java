package com.dolgurum.bangguseok;

import android.content.Context;
import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;
import android.hardware.SensorManager;
import com.getcapacitor.JSObject;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;

/**
 * 기압계(공기 압력 센서) 실시간 읽기 (11/18 보스 "운동 중 고도"). 웹 화면에서 window.Capacitor.Plugins.Baro
 * start() → { ok, reason } · 1초에 한 번 'baro' 알림 { hpa } · stop()
 * 높이 = 기압 차이로 계산(웹 쪽). 기압계가 없는 폰은 ok:false → 웹이 지형 자료로 대신함
 */
@CapacitorPlugin(name = "Baro")
public class BaroPlugin extends Plugin implements SensorEventListener {
    private SensorManager sm;
    private boolean on = false;
    private long lastSent = 0;
    private float sum = 0; private int cnt = 0;

    @PluginMethod
    public void start(PluginCall call) {
        JSObject r = new JSObject();
        try {
            sm = (SensorManager) getContext().getSystemService(Context.SENSOR_SERVICE);
            Sensor s = sm != null ? sm.getDefaultSensor(Sensor.TYPE_PRESSURE) : null;
            if (s == null) { r.put("ok", false); r.put("reason", "none"); call.resolve(r); return; }
            if (!on) { sm.registerListener(this, s, SensorManager.SENSOR_DELAY_NORMAL); on = true; }
            r.put("ok", true);
        } catch (Exception e) { r.put("ok", false); r.put("reason", "error"); }
        call.resolve(r);
    }

    @PluginMethod
    public void stop(PluginCall call) { off(); call.resolve(); }

    private void off() {
        try { if (sm != null && on) sm.unregisterListener(this); } catch (Exception ignored) {}
        on = false; sum = 0; cnt = 0;
    }

    @Override
    public void onSensorChanged(SensorEvent e) {
        sum += e.values[0]; cnt++;
        long now = System.currentTimeMillis();
        if (now - lastSent < 1000 || cnt == 0) return;   // 1초 평균 한 번
        JSObject d = new JSObject(); d.put("hpa", sum / cnt); d.put("t", now);
        sum = 0; cnt = 0; lastSent = now;
        notifyListeners("baro", d);
    }

    @Override public void onAccuracyChanged(Sensor s, int a) {}

    @Override protected void handleOnDestroy() { off(); }
}
