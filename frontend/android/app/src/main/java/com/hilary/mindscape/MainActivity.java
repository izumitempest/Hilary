package com.hilary.mindscape;

import android.os.Bundle;
import com.getcapacitor.BridgeActivity;
import com.hilary.mindscape.plugins.UsageStatsPlugin;

public class MainActivity extends BridgeActivity {
    @Override
    public void onCreate(Bundle savedInstanceState) {
        registerPlugin(UsageStatsPlugin.class);
        super.onCreate(savedInstanceState);
    }
}
