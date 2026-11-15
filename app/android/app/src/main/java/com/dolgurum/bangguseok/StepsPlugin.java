package com.dolgurum.bangguseok;

import android.Manifest;
import android.os.Build;
import androidx.work.ExistingPeriodicWorkPolicy;
import androidx.work.PeriodicWorkRequest;
import androidx.work.WorkManager;
import com.getcapacitor.JSObject;
import com.getcapacitor.PermissionState;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;
import com.getcapacitor.annotation.Permission;
import com.getcapacitor.annotation.PermissionCallback;
import java.util.Calendar;
import java.util.concurrent.TimeUnit;

/** 웹 화면에서 window.Capacitor.Plugins.Steps 로 부름 */
@CapacitorPlugin(name = "Steps", permissions = { @Permission(alias = "activity", strings = { Manifest.permission.ACTIVITY_RECOGNITION }) })
public class StepsPlugin extends Plugin {

    private boolean needsPerm() { return Build.VERSION.SDK_INT >= 29 && getPermissionState("activity") != PermissionState.GRANTED; }

    private void schedule() {
        PeriodicWorkRequest req = new PeriodicWorkRequest.Builder(StepWorker.class, 15, TimeUnit.MINUTES).build();
        WorkManager.getInstance(getContext()).enqueueUniquePeriodicWork("bgsj-steps", ExistingPeriodicWorkPolicy.KEEP, req);
    }

    @PluginMethod
    public void start(PluginCall call) {   // 권한 묻기 + 15분 읽기 예약 + 오늘 걸음
        if (needsPerm()) { requestPermissionForAlias("activity", call, "afterPerm"); return; }
        schedule(); today(call);
    }

    @PermissionCallback
    private void afterPerm(PluginCall call) {
        if (needsPerm()) { JSObject r = new JSObject(); r.put("available", false); r.put("reason", "permission"); call.resolve(r); return; }
        schedule(); today(call);
    }

    @PluginMethod
    public void today(PluginCall call) {
        if (needsPerm()) { JSObject r = new JSObject(); r.put("available", false); r.put("reason", "permission"); call.resolve(r); return; }
        new Thread(() -> {
            long v = StepReader.readOnce(getContext(), 3000);
            JSObject r = new JSObject();
            if (v < 0) { r.put("available", false); r.put("reason", "sensor"); call.resolve(r); return; }
            r.put("available", true);
            r.put("day", StepStore.dayKey());
            r.put("steps", StepStore.update(getContext(), v));
            JSObject hist = new JSObject();   // 지난 7일 (앱을 며칠 안 열어도 채워 넣게)
            Calendar c = Calendar.getInstance();
            for (int i = 1; i <= 7; i++) {
                c.add(Calendar.DAY_OF_MONTH, -1);
                String k = c.get(Calendar.YEAR) + "-" + (c.get(Calendar.MONTH) + 1) + "-" + c.get(Calendar.DAY_OF_MONTH);
                long h = StepStore.hist(getContext(), k);
                if (h >= 0) hist.put(k, h);
            }
            r.put("history", hist);
            call.resolve(r);
        }).start();
    }
}
