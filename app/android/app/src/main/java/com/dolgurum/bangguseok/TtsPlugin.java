package com.dolgurum.bangguseok;

import android.content.Context;
import android.media.AudioAttributes;
import android.media.AudioFocusRequest;
import android.media.AudioManager;
import android.os.Build;
import android.speech.tts.TextToSpeech;
import android.speech.tts.UtteranceProgressListener;
import com.getcapacitor.JSObject;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;
import java.util.Locale;

/**
 * 음성 안내 (11/17). 웹 화면에서 window.Capacitor.Plugins.Tts.speak({ text }) 로 부름.
 * 폰 기본 음성(TextToSpeech)을 써서 화면이 꺼져 있어도 말함 (잠금 중 GPS 알림이 앱을 깨워 둠).
 * 말하는 동안 음악은 잠깐 작아지고(ducking), 끝나면 원래대로.
 */
@CapacitorPlugin(name = "Tts")
public class TtsPlugin extends Plugin {
    private TextToSpeech tts;
    private boolean ready = false;
    private int pending = 0;
    private AudioManager am;
    private AudioFocusRequest focusReq;
    private final AudioManager.OnAudioFocusChangeListener focusListener = c -> {};

    @Override
    public void load() {
        am = (AudioManager) getContext().getSystemService(Context.AUDIO_SERVICE);
        tts = new TextToSpeech(getContext(), status -> {
            if (status != TextToSpeech.SUCCESS) return;
            int r = tts.setLanguage(Locale.KOREAN);
            ready = r != TextToSpeech.LANG_MISSING_DATA && r != TextToSpeech.LANG_NOT_SUPPORTED;
            AudioAttributes aa = new AudioAttributes.Builder()
                .setUsage(AudioAttributes.USAGE_ASSISTANCE_NAVIGATION_GUIDANCE)
                .setContentType(AudioAttributes.CONTENT_TYPE_SPEECH).build();
            tts.setAudioAttributes(aa);
            tts.setOnUtteranceProgressListener(new UtteranceProgressListener() {
                @Override public void onStart(String id) {}
                @Override public void onDone(String id) { release(); }
                @Override public void onError(String id) { release(); }
            });
        });
    }

    private synchronized void grab() {
        pending++;
        if (pending > 1 || am == null) return;
        if (Build.VERSION.SDK_INT >= 26) {
            focusReq = new AudioFocusRequest.Builder(AudioManager.AUDIOFOCUS_GAIN_TRANSIENT_MAY_DUCK)
                .setAudioAttributes(new AudioAttributes.Builder()
                    .setUsage(AudioAttributes.USAGE_ASSISTANCE_NAVIGATION_GUIDANCE)
                    .setContentType(AudioAttributes.CONTENT_TYPE_SPEECH).build())
                .setOnAudioFocusChangeListener(focusListener).build();
            am.requestAudioFocus(focusReq);
        } else {
            am.requestAudioFocus(focusListener, AudioManager.STREAM_MUSIC, AudioManager.AUDIOFOCUS_GAIN_TRANSIENT_MAY_DUCK);
        }
    }

    private synchronized void release() {
        pending = Math.max(0, pending - 1);
        if (pending > 0 || am == null) return;
        if (Build.VERSION.SDK_INT >= 26) { if (focusReq != null) am.abandonAudioFocusRequest(focusReq); }
        else am.abandonAudioFocus(focusListener);
    }

    @PluginMethod
    public void speak(PluginCall call) {
        String text = call.getString("text", "");
        JSObject r = new JSObject();
        if (!ready || text == null || text.isEmpty()) { r.put("ok", false); call.resolve(r); return; }
        Float rate = call.getFloat("rate", 1.0f);
        tts.setSpeechRate(rate == null ? 1.0f : rate);
        grab();
        int res = tts.speak(text, TextToSpeech.QUEUE_ADD, null, "bgr" + System.nanoTime());
        if (res != TextToSpeech.SUCCESS) release();
        r.put("ok", res == TextToSpeech.SUCCESS);
        call.resolve(r);
    }

    @PluginMethod
    public void stop(PluginCall call) {
        if (tts != null) tts.stop();
        synchronized (this) { pending = 1; }
        release();
        call.resolve();
    }

    @PluginMethod
    public void available(PluginCall call) {
        JSObject r = new JSObject(); r.put("ready", ready); call.resolve(r);
    }

    @Override
    protected void handleOnDestroy() {
        if (tts != null) { tts.stop(); tts.shutdown(); }
    }
}
