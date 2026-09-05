package com.kefayat.gem;

import android.app.Activity;
import android.content.ContentValues;
import android.graphics.Color;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.Environment;
import android.provider.MediaStore;
import android.util.Base64;
import android.webkit.JavascriptInterface;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Toast;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;

public class MainActivity extends Activity {
    private static final String LOCAL_PREFIX = "file:///android_asset/";
    private WebView web;
    private File pendingPdfFile;
    private FileOutputStream pendingPdfOut;
    private String pendingPdfName;

    @Override
    @SuppressWarnings("SetJavaScriptEnabled")
    public void onCreate(Bundle state) {
        super.onCreate(state);
        getWindow().setStatusBarColor(Color.rgb(244, 247, 251));

        web = new WebView(this);
        WebSettings settings = web.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setDatabaseEnabled(true);
        settings.setAllowFileAccess(true);
        settings.setAllowContentAccess(false);
        settings.setBuiltInZoomControls(false);
        settings.setDisplayZoomControls(false);
        settings.setCacheMode(WebSettings.LOAD_DEFAULT);
        settings.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);

        // Expose only a narrow local-artifact bridge. Large PDFs are streamed in
        // bounded base64 chunks instead of crossing the WebView boundary in one payload.
        web.addJavascriptInterface(new PdfBridge(), "KefayatAndroid");
        web.setWebViewClient(new WebViewClient() {
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                Uri uri = request.getUrl();
                String value = uri == null ? "" : uri.toString();
                return !(value.startsWith(LOCAL_PREFIX) || value.startsWith("about:blank"));
            }

            @Override
            public void onPageFinished(WebView view, String url) {
                super.onPageFinished(view, url);
                if (url != null && url.startsWith(LOCAL_PREFIX)) {
                    // Keep Android-specific transport outside the web artifact. The adapter
                    // wraps KefayatArtifact.downloadArtifact only inside this trusted shell.
                    view.evaluateJavascript(
                        "(function(){if(!window.__KEFAYAT_ANDROID_PDF_ADAPTER_LOADING__){" +
                        "window.__KEFAYAT_ANDROID_PDF_ADAPTER_LOADING__=true;" +
                        "var s=document.createElement('script');" +
                        "s.src='file:///android_asset/artifact/android-webview-bridge.js';" +
                        "s.onload=function(){window.__KEFAYAT_ANDROID_PDF_ADAPTER_LOADING__=false;};" +
                        "s.onerror=function(){window.__KEFAYAT_ANDROID_PDF_ADAPTER_LOADING__=false;};" +
                        "document.head.appendChild(s);}})();",
                        null
                    );
                }
            }
        });

        setContentView(web);
        web.loadUrl(LOCAL_PREFIX + "index.html");
    }

    private static String safePdfName(String requested) {
        String value = requested == null ? "" : requested.trim();
        value = value.replaceAll("[^A-Za-z0-9._-]", "_");
        if (value.isEmpty()) value = "kefayat.pdf";
        if (!value.toLowerCase().endsWith(".pdf")) value += ".pdf";
        if (value.length() > 96) value = value.substring(0, 92) + ".pdf";
        return value;
    }

    private synchronized void resetPendingPdf() {
        if (pendingPdfOut != null) {
            try { pendingPdfOut.close(); } catch (IOException ignored) { }
        }
        pendingPdfOut = null;
        if (pendingPdfFile != null && pendingPdfFile.exists()) {
            //noinspection ResultOfMethodCallIgnored
            pendingPdfFile.delete();
        }
        pendingPdfFile = null;
        pendingPdfName = null;
    }

    private static void copy(InputStream in, OutputStream out) throws IOException {
        byte[] buffer = new byte[64 * 1024];
        int read;
        while ((read = in.read(buffer)) != -1) out.write(buffer, 0, read);
        out.flush();
    }

    private String publishPendingPdf() throws IOException {
        if (pendingPdfFile == null || pendingPdfName == null || !pendingPdfFile.isFile()) {
            throw new IOException("No pending PDF");
        }

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            ContentValues values = new ContentValues();
            values.put(MediaStore.Downloads.DISPLAY_NAME, pendingPdfName);
            values.put(MediaStore.Downloads.MIME_TYPE, "application/pdf");
            values.put(MediaStore.Downloads.RELATIVE_PATH, Environment.DIRECTORY_DOWNLOADS + "/Kefayat");
            values.put(MediaStore.Downloads.IS_PENDING, 1);
            Uri uri = getContentResolver().insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI, values);
            if (uri == null) throw new IOException("MediaStore insert failed");
            try (InputStream in = new FileInputStream(pendingPdfFile);
                 OutputStream out = getContentResolver().openOutputStream(uri, "w")) {
                if (out == null) throw new IOException("MediaStore output failed");
                copy(in, out);
            } catch (IOException failure) {
                getContentResolver().delete(uri, null, null);
                throw failure;
            }
            ContentValues complete = new ContentValues();
            complete.put(MediaStore.Downloads.IS_PENDING, 0);
            getContentResolver().update(uri, complete, null, null);
            return uri.toString();
        }

        File root = getExternalFilesDir(Environment.DIRECTORY_DOWNLOADS);
        if (root == null) root = getFilesDir();
        File dir = new File(root, "Kefayat");
        if (!dir.exists() && !dir.mkdirs()) throw new IOException("Cannot create PDF directory");
        File target = new File(dir, pendingPdfName);
        try (InputStream in = new FileInputStream(pendingPdfFile);
             OutputStream out = new FileOutputStream(target)) {
            copy(in, out);
        }
        return target.getAbsolutePath();
    }

    private void toast(final String text) {
        runOnUiThread(() -> Toast.makeText(MainActivity.this, text, Toast.LENGTH_LONG).show());
    }

    public final class PdfBridge {
        @JavascriptInterface
        public synchronized boolean beginPdf(String filename) {
            resetPendingPdf();
            try {
                pendingPdfName = safePdfName(filename);
                pendingPdfFile = File.createTempFile("kefayat-pdf-", ".tmp", getCacheDir());
                pendingPdfOut = new FileOutputStream(pendingPdfFile);
                return true;
            } catch (IOException error) {
                resetPendingPdf();
                toast("تعذر بدء حفظ ملف PDF");
                return false;
            }
        }

        @JavascriptInterface
        public synchronized boolean appendPdfChunk(String base64Chunk) {
            if (pendingPdfOut == null || base64Chunk == null) return false;
            try {
                byte[] bytes = Base64.decode(base64Chunk, Base64.DEFAULT);
                pendingPdfOut.write(bytes);
                return true;
            } catch (Exception error) {
                resetPendingPdf();
                toast("تعذر كتابة ملف PDF");
                return false;
            }
        }

        @JavascriptInterface
        public synchronized String finishPdf() {
            if (pendingPdfOut == null || pendingPdfFile == null) return "";
            try {
                pendingPdfOut.flush();
                pendingPdfOut.close();
                pendingPdfOut = null;
                if (pendingPdfFile.length() < 1024) throw new IOException("PDF payload too small");
                String destination = publishPendingPdf();
                toast("تم حفظ PDF في مجلد التنزيلات / Kefayat");
                resetPendingPdf();
                return destination;
            } catch (IOException error) {
                resetPendingPdf();
                toast("تعذر حفظ ملف PDF النهائي");
                return "";
            }
        }

        @JavascriptInterface
        public synchronized void cancelPdf() {
            resetPendingPdf();
        }
    }

    @Override
    @SuppressWarnings("deprecation")
    public void onBackPressed() {
        if (web != null && web.canGoBack()) web.goBack(); else super.onBackPressed();
    }

    @Override
    protected void onDestroy() {
        resetPendingPdf();
        if (web != null) {
            web.removeJavascriptInterface("KefayatAndroid");
            web.destroy();
            web = null;
        }
        super.onDestroy();
    }
}
