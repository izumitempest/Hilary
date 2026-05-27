import { Capacitor, registerPlugin } from '@capacitor/core';

const UsageStats = registerPlugin('UsageStats');

export async function logMobileBehaviorSnapshot(apiClient) {
  if (!Capacitor.isNativePlatform() || Capacitor.getPlatform() !== 'android') {
    return;
  }
  try {
    const snapshot = await UsageStats.getUsageSnapshot({ hours: 24, topApps: 8 });
    await apiClient.post('/behavior/log', {
      screen_time_seconds: snapshot.screenTimeSeconds ?? 0,
      app_usage: snapshot.appUsage ?? {},
      unlock_count: snapshot.unlockCount ?? 0,
    });
  } catch (error) {
    // Non-fatal. App should continue if user has not granted usage access.
    console.debug('Usage stats unavailable:', error?.message || error);
  }
}

export async function openUsageSettings() {
  if (!Capacitor.isNativePlatform() || Capacitor.getPlatform() !== 'android') {
    return;
  }
  try {
    await UsageStats.openUsageAccessSettings();
  } catch (error) {
    console.debug('Unable to open usage settings:', error?.message || error);
  }
}
