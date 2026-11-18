package com.dolgurum.bangguseok;

import android.Manifest;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.content.pm.PackageManager;
import android.media.AudioAttributes;
import android.media.AudioFormat;
import android.media.AudioTrack;
import android.media.session.MediaSession;
import android.media.session.PlaybackState;
import android.os.Build;
import android.view.KeyEvent;
import androidx.core.app.ActivityCompat;
import androidx.core.app.NotificationCompat;
import androidx.core.app.NotificationManagerCompat;
import androidx.core.content.ContextCompat;
import com.getcapacitor.JSObject;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;

/**
 * 운동 중 알림 + 이어폰 버튼 (11/18 보스 "워치·이어폰 연동"). 웹 화면에서 window.Capacitor.Plugins.Workout
 *  show({ title, text, paused, alert }) — 알림 칸에 운동 숫자. 갤럭시 워치는 폰 알림을 그대로 보여 줌 → 손목에서 거리·시간
 *     · 계속 떠 있는(ongoing) 알림은 워치로 안 넘어가서 일반 알림 + 소리 없이 고치기. alert:true면 한 번 울림(1km마다 워치 진동)
 *     · 알림 버튼 '일시정지/다시 시작' → 'action' {a:'toggle'} (워치에서도 누름)
 *  clear() — 알림 지우기
 *  media({ on }) — 이어폰 톡(재생/일시정지 버튼) → 'action' {a:'toggle'}. 음악 앱이 재생 중이면 그쪽이 버튼을 가져감(안드로이드 규칙)
 */
@CapacitorPlugin(name = "Workout")
public class WorkoutPlugin extends Plugin {
    private static final String CH = "workout";
    private static final int ID = 7301;
    private static final String ACT = "com.re2.bangguseokrunner.WORKOUT_TOGGLE";
    private BroadcastReceiver rx;
    private MediaSession ms;
    private boolean asked = false;

    @Override
    public void load() {
        rx = new BroadcastReceiver() {
            @Override public void onReceive(Context c, Intent i) { toggle("notif"); }
        };
        ContextCompat.registerReceiver(getContext(), rx, new IntentFilter(ACT), ContextCompat.RECEIVER_NOT_EXPORTED);
    }

    private void toggle(String from) {
        JSObject d = new JSObject(); d.put("a", "toggle"); d.put("from", from);
        notifyListeners("action", d);
    }

    private void channel() {
        if (Build.VERSION.SDK_INT < 26) return;
        NotificationManager nm = (NotificationManager) getContext().getSystemService(Context.NOTIFICATION_SERVICE);
        if (nm.getNotificationChannel(CH) != null) return;
        NotificationChannel ch = new NotificationChannel(CH, "운동 중 숫자", NotificationManager.IMPORTANCE_DEFAULT);
        ch.setDescription("운동 중 거리·시간 (워치에도 보임)");
        ch.setSound(null, null); ch.enableVibration(false); ch.setShowBadge(false);
        nm.createNotificationChannel(ch);
    }

    @PluginMethod
    public void show(PluginCall call) {
        try {
            Context c = getContext();
            if (Build.VERSION.SDK_INT >= 33 && ContextCompat.checkSelfPermission(c, Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) {
                if (!asked && getActivity() != null) { asked = true; ActivityCompat.requestPermissions(getActivity(), new String[]{ Manifest.permission.POST_NOTIFICATIONS }, 7302); }
                JSObject r = new JSObject(); r.put("ok", false); r.put("reason", "permission"); call.resolve(r); return;
            }
            channel();
            Intent open = c.getPackageManager().getLaunchIntentForPackage(c.getPackageName());
            PendingIntent pOpen = open == null ? null : PendingIntent.getActivity(c, 0, open, PendingIntent.FLAG_IMMUTABLE | PendingIntent.FLAG_UPDATE_CURRENT);
            Intent t = new Intent(ACT).setPackage(c.getPackageName());
            PendingIntent pT = PendingIntent.getBroadcast(c, 1, t, PendingIntent.FLAG_IMMUTABLE | PendingIntent.FLAG_UPDATE_CURRENT);
            boolean paused = Boolean.TRUE.equals(call.getBoolean("paused", false));
            boolean alert = Boolean.TRUE.equals(call.getBoolean("alert", false));
            NotificationCompat.Builder b = new NotificationCompat.Builder(c, CH)
                .setSmallIcon(R.drawable.ic_tracking)
                .setContentTitle(call.getString("title", "방구석러너"))
                .setContentText(call.getString("text", ""))
                .setStyle(new NotificationCompat.BigTextStyle().bigText(call.getString("text", "")))
                .setCategory("workout")
                .setOnlyAlertOnce(!alert)
                .setSilent(!alert)
                .setAutoCancel(false)
                .setShowWhen(false)
                .setPriority(NotificationCompat.PRIORITY_DEFAULT)
                .addAction(0, paused ? "▶ 다시 시작" : "⏸ 일시정지", pT);
            if (pOpen != null) b.setContentIntent(pOpen);
            NotificationManagerCompat.from(c).notify(ID, b.build());
            JSObject r = new JSObject(); r.put("ok", true); call.resolve(r);
        } catch (Exception e) {
            JSObject r = new JSObject(); r.put("ok", false); r.put("reason", "error"); call.resolve(r);
        }
    }

    @PluginMethod
    public void clear(PluginCall call) {
        try { NotificationManagerCompat.from(getContext()).cancel(ID); } catch (Exception ignored) {}
        call.resolve();
    }

    @PluginMethod
    public void media(PluginCall call) {
        boolean on = Boolean.TRUE.equals(call.getBoolean("on", false));
        try {
            if (on && ms == null) {
                ms = new MediaSession(getContext(), "bgr-workout");
                ms.setCallback(new MediaSession.Callback() {
                    @Override public boolean onMediaButtonEvent(Intent i) {
                        KeyEvent k = i.getParcelableExtra(Intent.EXTRA_KEY_EVENT);
                        if (k != null && k.getAction() == KeyEvent.ACTION_UP) {
                            int code = k.getKeyCode();
                            if (code == KeyEvent.KEYCODE_HEADSETHOOK || code == KeyEvent.KEYCODE_MEDIA_PLAY_PAUSE || code == KeyEvent.KEYCODE_MEDIA_PLAY || code == KeyEvent.KEYCODE_MEDIA_PAUSE) toggle("button");
                        }
                        return true;
                    }
                });
                ms.setPlaybackState(new PlaybackState.Builder()
                    .setActions(PlaybackState.ACTION_PLAY_PAUSE | PlaybackState.ACTION_PLAY | PlaybackState.ACTION_PAUSE)
                    .setState(PlaybackState.STATE_PLAYING, 0, 1f).build());
                ms.setActive(true);
                silence();   // 안드로이드는 '마지막으로 소리를 낸 앱'에 이어폰 버튼을 줌 → 0.3초 무음
            } else if (!on && ms != null) {
                ms.setActive(false); ms.release(); ms = null;
            }
        } catch (Exception ignored) {}
        call.resolve();
    }

    private void silence() {
        try {
            int rate = 8000, n = rate * 3 / 10;
            AudioTrack at = new AudioTrack.Builder()
                .setAudioAttributes(new AudioAttributes.Builder().setUsage(AudioAttributes.USAGE_MEDIA).setContentType(AudioAttributes.CONTENT_TYPE_UNKNOWN).build())
                .setAudioFormat(new AudioFormat.Builder().setEncoding(AudioFormat.ENCODING_PCM_16BIT).setSampleRate(rate).setChannelMask(AudioFormat.CHANNEL_OUT_MONO).build())
                .setTransferMode(AudioTrack.MODE_STATIC).setBufferSizeInBytes(n * 2).build();
            at.write(new short[n], 0, n); at.play();
            new android.os.Handler(android.os.Looper.getMainLooper()).postDelayed(() -> { try { at.stop(); at.release(); } catch (Exception ignored) {} }, 600);
        } catch (Exception ignored) {}
    }

    @Override
    protected void handleOnDestroy() {
        try { NotificationManagerCompat.from(getContext()).cancel(ID); } catch (Exception ignored) {}
        try { if (ms != null){ ms.release(); ms = null; } } catch (Exception ignored) {}
        try { getContext().unregisterReceiver(rx); } catch (Exception ignored) {}
    }
}
