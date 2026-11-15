package com.dolgurum.bangguseok;

import android.content.Context;
import androidx.annotation.NonNull;
import androidx.work.Worker;
import androidx.work.WorkerParameters;

/** 15분마다 걸음 칩을 읽어 하루 기준점을 갱신 (앱을 안 열어도 0시 경계가 맞도록) */
public class StepWorker extends Worker {
    public StepWorker(@NonNull Context ctx, @NonNull WorkerParameters p) { super(ctx, p); }
    @NonNull @Override public Result doWork() {
        long v = StepReader.readOnce(getApplicationContext(), 8000);
        if (v >= 0) StepStore.update(getApplicationContext(), v);
        return Result.success();
    }
}
