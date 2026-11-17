package com.dolgurum.bangguseok;

import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.net.ConnectivityManager;
import android.net.Network;
import android.net.NetworkCapabilities;
import android.net.TrafficStats;
import android.os.BatteryManager;
import android.os.Build;
import android.os.Process;
import com.getcapacitor.JSObject;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;

/**
 * 운동 1회 데이터·배터리 측정 (11/17). 웹 화면에서 window.Capacitor.Plugins.Meter.snap() 으로 부름.
 * rx·tx = 이 앱이 지금까지 주고받은 바이트(안드로이드가 직접 셈) · batt = 배터리 % · chg = 충전 중 · net = wifi / cell / none
 */
@CapacitorPlugin(name = "Meter")
public class MeterPlugin extends Plugin {

    @PluginMethod
    public void snap(PluginCall call) {
        JSObject r = new JSObject();
        int uid = Process.myUid();
        long rx = TrafficStats.getUidRxBytes(uid), tx = TrafficStats.getUidTxBytes(uid);
        r.put("rx", rx == TrafficStats.UNSUPPORTED ? -1 : rx);
        r.put("tx", tx == TrafficStats.UNSUPPORTED ? -1 : tx);
        Context ctx = getContext();
        try {
            BatteryManager bm = (BatteryManager) ctx.getSystemService(Context.BATTERY_SERVICE);
            int lv = bm != null ? bm.getIntProperty(BatteryManager.BATTERY_PROPERTY_CAPACITY) : -1;
            boolean chg;
            Intent bi = ctx.registerReceiver(null, new IntentFilter(Intent.ACTION_BATTERY_CHANGED));
            if (lv <= 0 && bi != null) {
                int l = bi.getIntExtra(BatteryManager.EXTRA_LEVEL, -1), s = bi.getIntExtra(BatteryManager.EXTRA_SCALE, 100);
                lv = l >= 0 ? Math.round(l * 100f / s) : -1;
            }
            if (Build.VERSION.SDK_INT >= 23 && bm != null) chg = bm.isCharging();
            else chg = bi != null && bi.getIntExtra(BatteryManager.EXTRA_PLUGGED, 0) != 0;
            r.put("batt", lv); r.put("chg", chg);
        } catch (Exception e) { r.put("batt", -1); r.put("chg", false); }
        String net = "none";
        try {
            ConnectivityManager cm = (ConnectivityManager) ctx.getSystemService(Context.CONNECTIVITY_SERVICE);
            if (cm != null && Build.VERSION.SDK_INT >= 23) {
                Network n = cm.getActiveNetwork();
                NetworkCapabilities nc = n != null ? cm.getNetworkCapabilities(n) : null;
                if (nc != null) net = nc.hasTransport(NetworkCapabilities.TRANSPORT_WIFI) || nc.hasTransport(NetworkCapabilities.TRANSPORT_ETHERNET) ? "wifi"
                    : nc.hasTransport(NetworkCapabilities.TRANSPORT_CELLULAR) ? "cell" : "other";
            }
        } catch (Exception e) { net = "unknown"; }
        r.put("net", net);
        call.resolve(r);
    }
}
