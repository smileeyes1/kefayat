package com.kefayat.gem;

import android.app.Activity;
import android.os.Bundle;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.graphics.Color;
import android.view.ViewGroup;
import android.widget.TextView;
import android.widget.LinearLayout;

public class MainActivity extends Activity {
    private static final String WEB_APP = "https://smileeyes1.github.io/kefayat/";
    private WebView web;

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        getWindow().setStatusBarColor(Color.rgb(244,247,251));
        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        TextView fallback = new TextView(this);
        fallback.setText("كفايات Ω\nجاري تشغيل التطبيق…");
        fallback.setTextSize(20);
        fallback.setPadding(32,48,32,32);
        root.addView(fallback, new LinearLayout.LayoutParams(-1,-2));
        web = new WebView(this);
        root.addView(web, new LinearLayout.LayoutParams(-1,0,1));
        setContentView(root);
        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setDatabaseEnabled(true);
        s.setAllowFileAccess(true);
        s.setAllowContentAccess(true);
        s.setCacheMode(WebSettings.LOAD_DEFAULT);
        web.setWebViewClient(new WebViewClient());
        web.loadUrl(WEB_APP);
    }

    @Override public void onBackPressed() {
        if (web != null && web.canGoBack()) web.goBack(); else super.onBackPressed();
    }
}
