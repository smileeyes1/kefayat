/* KEFAYAT Ω — Android WebView PDF delivery adapter.
 * Loaded only by the native Android shell. It wraps the browser PDF download
 * with a bounded chunked JavascriptInterface transport, then falls back to the
 * ordinary browser download path if the bridge is unavailable.
 */
(function(){
  'use strict';
  if(typeof window==='undefined'||!window.KefayatArtifact||!window.KefayatAndroid) return;
  if(window.__KEFAYAT_ANDROID_PDF_BRIDGE__==='READY') return;

  const original=window.KefayatArtifact.downloadArtifact;
  const CHUNK_BYTES=48*1024;

  function toBase64(bytes){
    let binary='';
    for(let i=0;i<bytes.length;i++) binary+=String.fromCharCode(bytes[i]);
    return btoa(binary);
  }

  function saveThroughAndroid(artifact){
    if(!artifact||!(artifact.bytes instanceof Uint8Array)||!artifact.bytes.length) throw new Error('INVALID_PDF_ARTIFACT');
    if(!window.KefayatAndroid.beginPdf(String(artifact.filename||'kefayat.pdf'))) throw new Error('ANDROID_PDF_BEGIN_FAILED');
    try{
      for(let offset=0;offset<artifact.bytes.length;offset+=CHUNK_BYTES){
        const piece=artifact.bytes.slice(offset,Math.min(offset+CHUNK_BYTES,artifact.bytes.length));
        if(!window.KefayatAndroid.appendPdfChunk(toBase64(piece))) throw new Error('ANDROID_PDF_CHUNK_FAILED');
      }
      const destination=window.KefayatAndroid.finishPdf();
      if(!destination) throw new Error('ANDROID_PDF_FINISH_FAILED');
      artifact.androidDestination=String(destination);
      return artifact.filename;
    }catch(error){
      try{window.KefayatAndroid.cancelPdf()}catch(_){ }
      throw error;
    }
  }

  window.KefayatArtifact.downloadArtifact=function(artifact){
    try{return saveThroughAndroid(artifact)}
    catch(error){
      console.warn('KEFAYAT_ANDROID_PDF_BRIDGE_FALLBACK',error);
      return typeof original==='function'?original(artifact):artifact?.filename;
    }
  };
  window.__KEFAYAT_ANDROID_PDF_BRIDGE__='READY';
})();
