import os

PKG = "com.instagram.android"  # change to your clone's package if needed

def w(path, text):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w") as f:
        f.write(text)

w("settings.gradle", r'''
pluginManagement {
    repositories { google(); mavenCentral(); gradlePluginPortal() }
}
dependencyResolutionManagement {
    repositories { google(); mavenCentral() }
}
rootProject.name = "Calculator"
include ':app'
''')

w("build.gradle", r'''
plugins { id 'com.android.application' version '8.5.0' apply false }
''')

w("gradle.properties", "android.useAndroidX=true\norg.gradle.jvmargs=-Xmx2g\n")

w("app/build.gradle", r'''
plugins { id 'com.android.application' }
android {
    namespace 'com.sr.calc'
    compileSdk 34
    defaultConfig {
        applicationId 'com.sr.calc'
        minSdk 24
        targetSdk 34
        versionCode 1
        versionName '1.0'
    }
    compileOptions {
        sourceCompatibility JavaVersion.VERSION_1_8
        targetCompatibility JavaVersion.VERSION_1_8
    }
}
''')

w("app/src/main/AndroidManifest.xml", r'''<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <uses-permission android:name="android.permission.INTERNET"/>
    <queries>
        <package android:name="PKG_HERE"/>
    </queries>
    <application
        android:label="Calculator"
        android:theme="@android:style/Theme.DeviceDefault.NoActionBar">
        <activity android:name=".MainActivity" android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN"/>
                <category android:name="android.intent.category.LAUNCHER"/>
            </intent-filter>
        </activity>
        <activity android:name=".WebActivity" android:exported="false"/>
    </application>
</manifest>
'''.replace("PKG_HERE", PKG))

w("app/src/main/java/com/sr/calc/MainActivity.java", r'''
package com.sr.calc;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.view.Gravity;
import android.widget.*;

public class MainActivity extends Activity {
    static final String TARGET_PKG = "PKG_HERE";
    static final String SECRET = "2+2";
    TextView display;
    String expr = "";
    int pos;

    @Override
    protected void onCreate(Bundle b) {
        super.onCreate(b);
        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setBackgroundColor(0xFF000000);
        display = new TextView(this);
        display.setTextSize(44f);
        display.setTextColor(0xFFFFFFFF);
        display.setGravity(Gravity.END | Gravity.BOTTOM);
        display.setPadding(24, 24, 24, 24);
        root.addView(display, new LinearLayout.LayoutParams(-1, 0, 1.2f));
        String[] rows = {"789/", "456*", "123-", "C0.+", "="};
        for (String r : rows) {
            LinearLayout row = new LinearLayout(this);
            for (char ch : r.toCharArray()) {
                final char c = ch;
                Button btn = new Button(this);
                btn.setText(String.valueOf(c));
                btn.setTextSize(24f);
                btn.setOnClickListener(v -> press(c));
                row.addView(btn, new LinearLayout.LayoutParams(0, -1, 1f));
            }
            root.addView(row, new LinearLayout.LayoutParams(-1, 0, 1f));
        }
        setContentView(root);
    }

    void press(char c) {
        if (c == 'C') {
            expr = "";
        } else if (c == '=') {
            if (expr.equals(SECRET)) {
                expr = "";
                display.setText("");
                openTarget();
                return;
            }
            expr = calc(expr);
        } else {
            expr += c;
        }
        display.setText(expr);
    }

    void openTarget() {
        Intent i = getPackageManager().getLaunchIntentForPackage(TARGET_PKG);
        if (i != null) startActivity(i);
        else startActivity(new Intent(this, WebActivity.class));
    }

    String calc(String s) {
        try {
            pos = 0;
            double v = parseExpr(s);
            if (pos != s.length()) return "Error";
            if (v == Math.floor(v) && Math.abs(v) < 1e15) return String.valueOf((long) v);
            return String.valueOf(v);
        } catch (Exception e) {
            return "Error";
        }
    }

    double parseExpr(String s) {
        double v = parseTerm(s);
        while (pos < s.length() && (s.charAt(pos) == '+' || s.charAt(pos) == '-')) {
            char op = s.charAt(pos++);
            double t = parseTerm(s);
            v = op == '+' ? v + t : v - t;
        }
        return v;
    }

    double parseTerm(String s) {
        double v = parseNum(s);
        while (pos < s.length() && (s.charAt(pos) == '*' || s.charAt(pos) == '/')) {
            char op = s.charAt(pos++);
            double t = parseNum(s);
            v = op == '*' ? v * t : v / t;
        }
        return v;
    }

    double parseNum(String s) {
        int st = pos;
        while (pos < s.length() && (Character.isDigit(s.charAt(pos)) || s.charAt(pos) == '.')) pos++;
        return Double.parseDouble(s.substring(st, pos));
    }
}
'''.replace("PKG_HERE", PKG))

w("app/src/main/java/com/sr/calc/WebActivity.java", r'''
package com.sr.calc;

import android.app.Activity;
import android.os.Bundle;
import android.webkit.WebView;
import android.webkit.WebViewClient;

public class WebActivity extends Activity {
    WebView web;

    @Override
    protected void onCreate(Bundle b) {
        super.onCreate(b);
        web = new WebView(this);
        web.getSettings().setJavaScriptEnabled(true);
        web.getSettings().setDomStorageEnabled(true);
        web.setWebViewClient(new WebViewClient());
        setContentView(web);
        web.loadUrl("https://www.instagram.com/");
    }

    @Override
    public void onBackPressed() {
        if (web.canGoBack()) web.goBack();
        else finish();
    }
}
''')
