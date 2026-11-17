package com.dolgurum.bangguseok;

import android.Manifest;
import android.content.pm.PackageManager;
import android.os.Build;
import android.os.Bundle;
import androidx.activity.OnBackPressedCallback;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;
import com.getcapacitor.BridgeActivity;

public class MainActivity extends BridgeActivity {
    @Override
    public void onCreate(Bundle savedInstanceState) {
        registerPlugin(StepsPlugin.class);   // 24시간 걸음 칩
        registerPlugin(TtsPlugin.class);     // 음성 안내 (화면 꺼져도)
        registerPlugin(MeterPlugin.class);   // 운동 1회 데이터·배터리 측정
        super.onCreate(savedInstanceState);
        // 안드로이드 13+: 알림 권한이 있어야 '기록 중' 알림이 떠서 잠금 중 GPS가 유지됨
        if (Build.VERSION.SDK_INT >= 33 &&
            ContextCompat.checkSelfPermission(this, Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) {
            ActivityCompat.requestPermissions(this, new String[]{ Manifest.permission.POST_NOTIFICATIONS }, 1001);
        }
        // 폰 '뒤로' = 화면 한 단계만 닫기 (11/17 보스 승인).
        // 웹 화면(index.html)의 bgrBack()이 팝업·내 기록·코스 화면을 하나씩 닫고, 운동 중이면 끝낼지 묻는다.
        // 닫을 것이 없으면(첫 화면) 앱을 끄지 않고 뒤로 보낸다 — 잠금 중 GPS·걸음 기록이 끊기지 않게.
        getOnBackPressedDispatcher().addCallback(this, new OnBackPressedCallback(true) {
            @Override
            public void handleOnBackPressed() {
                try {
                    getBridge().getWebView().evaluateJavascript(
                        "(function(){try{return !!(window.bgrBack&&window.bgrBack())}catch(e){return false}})()",
                        v -> { if (!"true".equals(v)) moveTaskToBack(true); });
                } catch (Exception e) {
                    moveTaskToBack(true);
                }
            }
        });
    }
}
