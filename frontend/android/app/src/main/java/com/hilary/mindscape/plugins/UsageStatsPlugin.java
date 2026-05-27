package com.hilary.mindscape.plugins;

import android.app.AppOpsManager;
import android.app.usage.UsageEvents;
import android.app.usage.UsageStats;
import android.app.usage.UsageStatsManager;
import android.content.Context;
import android.content.Intent;
import android.os.Build;
import android.provider.Settings;

import com.getcapacitor.JSObject;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;

import java.util.HashMap;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;

@CapacitorPlugin(name = "UsageStats")
public class UsageStatsPlugin extends Plugin {

    @PluginMethod
    public void openUsageAccessSettings(PluginCall call) {
        Intent intent = new Intent(Settings.ACTION_USAGE_ACCESS_SETTINGS);
        intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
        getContext().startActivity(intent);
        call.resolve();
    }

    @PluginMethod
    public void getUsageSnapshot(PluginCall call) {
        if (!hasUsageStatsPermission()) {
            call.reject("USAGE_ACCESS_NOT_GRANTED");
            return;
        }

        Integer hours = call.getInt("hours", 24);
        Integer topApps = call.getInt("topApps", 8);
        long endTime = System.currentTimeMillis();
        long startTime = endTime - (hours.longValue() * 60L * 60L * 1000L);

        UsageStatsManager usageStatsManager =
                (UsageStatsManager) getContext().getSystemService(Context.USAGE_STATS_SERVICE);

        List<UsageStats> stats = usageStatsManager.queryUsageStats(
                UsageStatsManager.INTERVAL_DAILY, startTime, endTime
        );

        Map<String, Long> appUsageMillis = new HashMap<>();
        long totalForegroundMillis = 0L;

        for (UsageStats stat : stats) {
            long foreground = stat.getTotalTimeInForeground();
            if (foreground <= 0) continue;
            appUsageMillis.put(stat.getPackageName(), foreground);
            totalForegroundMillis += foreground;
        }

        List<Map.Entry<String, Long>> entries = new ArrayList<>(appUsageMillis.entrySet());
        Collections.sort(entries, (a, b) -> Long.compare(b.getValue(), a.getValue()));
        Map<String, Long> topUsage = new HashMap<>();
        int limit = Math.min(topApps, entries.size());
        for (int i = 0; i < limit; i++) {
            Map.Entry<String, Long> entry = entries.get(i);
            topUsage.put(entry.getKey(), entry.getValue() / 1000L);
        }

        int unlockCount = countUnlockEvents(usageStatsManager, startTime, endTime);

        JSObject appUsageJson = new JSObject();
        for (Map.Entry<String, Long> entry : topUsage.entrySet()) {
            appUsageJson.put(entry.getKey(), entry.getValue());
        }

        JSObject result = new JSObject();
        result.put("screenTimeSeconds", totalForegroundMillis / 1000L);
        result.put("unlockCount", unlockCount);
        result.put("appUsage", appUsageJson);
        result.put("windowHours", hours);
        call.resolve(result);
    }

    private int countUnlockEvents(UsageStatsManager manager, long startTime, long endTime) {
        UsageEvents events = manager.queryEvents(startTime, endTime);
        UsageEvents.Event event = new UsageEvents.Event();
        int unlockCount = 0;
        while (events.hasNextEvent()) {
            events.getNextEvent(event);
            if (event.getEventType() == 18) {
                unlockCount++;
            }
        }
        return unlockCount;
    }

    private boolean hasUsageStatsPermission() {
        Context context = getContext();
        AppOpsManager appOps =
                (AppOpsManager) context.getSystemService(Context.APP_OPS_SERVICE);
        if (appOps == null) return false;

        int mode;
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            mode = appOps.unsafeCheckOpNoThrow(
                    AppOpsManager.OPSTR_GET_USAGE_STATS,
                    android.os.Process.myUid(),
                    context.getPackageName()
            );
        } else {
            mode = appOps.checkOpNoThrow(
                    AppOpsManager.OPSTR_GET_USAGE_STATS,
                    android.os.Process.myUid(),
                    context.getPackageName()
            );
        }
        return mode == AppOpsManager.MODE_ALLOWED;
    }
}
