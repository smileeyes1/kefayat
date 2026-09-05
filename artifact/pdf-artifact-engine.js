/* KEFAYAT Ω — Browser-native PDF Artifact Engine v1.0
 * Creates a real, dependency-free, raster A4 PDF from browser-rendered Arabic canvases.
 * The raster strategy deliberately lets the browser shape Arabic before embedding pixels,
 * while math tokens are positioned explicitly so RTL/BiDi cannot reorder semantics.
 */
(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports) module.exports=api;
  root.KefayatArtifact=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';
  const ENC=typeof TextEncoder!=='undefined'?new TextEncoder():null;
  const EASTERN='٠١٢٣٤٥٦٧٨٩';
  const PAGE_PT={w:595.28,h:841.89};
  const CANVAS={w:1240,h:1754};

  function ascii(s){
    if(ENC) return ENC.encode(s);
    if(typeof Buffer!=='undefined') return Uint8Array.from(Buffer.from(s,'utf8'));
    throw new Error('Text encoder unavailable');
  }
  function concat(parts){
    const len=parts.reduce((n,p)=>n+p.length,0),out=new Uint8Array(len);let off=0;
    for(const p of parts){out.set(p,off);off+=p.length;}return out;
  }
  function eastern(value){return String(value??'').replace(/\d/g,d=>EASTERN[d])}
  function safeName(contract){
    const s=contract?.subject==='mathematics'?'math':contract?.subject==='arabic'?'arabic':contract?.subject==='islamic_education'?'islamic':contract?.subject==='nurturing'?'nurturing':'education';
    return `kefayat_${s}_g${contract?.grade||'x'}_${Date.now()}.pdf`;
  }
  function requireBrowser(){if(typeof document==='undefined')throw new Error('BROWSER_CANVAS_REQUIRED')}

  function serializeImagePdf(images){
    if(!Array.isArray(images)||!images.length) throw new Error('PDF_REQUIRES_AT_LEAST_ONE_PAGE');
    const objects=new Map(),kids=[];
    objects.set(1,ascii('<< /Type /Catalog /Pages 2 0 R >>'));
    for(let i=0;i<images.length;i++){
      const pageObj=3+i*3,imageObj=4+i*3,contentObj=5+i*3,im=`Im${i+1}`,img=images[i];
      if(!(img?.bytes instanceof Uint8Array)||!img.bytes.length) throw new Error('INVALID_JPEG_PAGE');
      kids.push(`${pageObj} 0 R`);
      objects.set(pageObj,ascii(`<< /Type /Page /Parent 2 0 R /MediaBox [0 0 ${PAGE_PT.w} ${PAGE_PT.h}] /Resources << /XObject << /${im} ${imageObj} 0 R >> >> /Contents ${contentObj} 0 R >>`));
      const ip=ascii(`<< /Type /XObject /Subtype /Image /Width ${img.width} /Height ${img.height} /ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /DCTDecode /Length ${img.bytes.length} >>\nstream\n`);
      objects.set(imageObj,concat([ip,img.bytes,ascii('\nendstream')]));
      const stream=`q\n${PAGE_PT.w} 0 0 ${PAGE_PT.h} 0 0 cm\n/${im} Do\nQ\n`;
      objects.set(contentObj,ascii(`<< /Length ${ascii(stream).length} >>\nstream\n${stream}endstream`));
    }
    objects.set(2,ascii(`<< /Type /Pages /Count ${images.length} /Kids [${kids.join(' ')}] >>`));
    const count=2+images.length*3,header=ascii('%PDF-1.4\n%KEFAYAT-OMEGA\n'),parts=[header],offsets=[0];
    let pos=header.length;
    for(let id=1;id<=count;id++){
      const body=objects.get(id);if(!body)throw new Error(`MISSING_PDF_OBJECT_${id}`);
      const prefix=ascii(`${id} 0 obj\n`),suffix=ascii('\nendobj\n');offsets[id]=pos;parts.push(prefix,body,suffix);pos+=prefix.length+body.length+suffix.length;
    }
    const xrefPos=pos;let xref=`xref\n0 ${count+1}\n0000000000 65535 f \n`;
    for(let id=1;id<=count;id++) xref+=`${String(offsets[id]).padStart(10,'0')} 00000 n \n`;
    xref+=`trailer\n<< /Size ${count+1} /Root 1 0 R >>\nstartxref\n${xrefPos}\n%%EOF\n`;
    parts.push(ascii(xref));return concat(parts);
  }

  function baseContext(){
    requireBrowser();const c=document.createElement('canvas');c.width=CANVAS.w;c.height=CANVAS.h;const x=c.getContext('2d');
    x.fillStyle='#fff';x.fillRect(0,0,c.width,c.height);x.fillStyle='#172033';x.textBaseline='alphabetic';x.direction='rtl';return {canvas:c,ctx:x};
  }
  function font(ctx,size,weight='400'){ctx.font=`${weight} ${size}px Tahoma, Arial, sans-serif`;ctx.textAlign='right';ctx.direction='rtl'}
  function line(ctx,text,y,size=36,weight='400',x=1140){font(ctx,size,weight);ctx.fillText(String(text),x,y);}
  function wrap(ctx,text,x,y,maxWidth,lineHeight,size=34,weight='400',maxLines=8){
    font(ctx,size,weight);const words=String(text??'').replace(/\s+/g,' ').trim().split(' ').filter(Boolean);let row='',lines=0;
    for(const w of words){const candidate=row?`${row} ${w}`:w;if(ctx.measureText(candidate).width>maxWidth&&row){ctx.fillText(row,x,y);y+=lineHeight;lines++;row=w;if(lines>=maxLines)break}else row=candidate;}
    if(row&&lines<maxLines){ctx.fillText(row,x,y);y+=lineHeight;}return y;
  }
  function separator(ctx,y){ctx.strokeStyle='#cbd5e1';ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(100,y);ctx.lineTo(1140,y);ctx.stroke()}
  function rounded(ctx,x,y,w,h,r=20){ctx.beginPath();ctx.roundRect(x,y,w,h,r);ctx.strokeStyle='#cbd5e1';ctx.lineWidth=2;ctx.stroke()}
  function drawFooter(ctx,pageNo,refId){separator(ctx,1630);line(ctx,`كفايات Ω · الصفحة ${eastern(pageNo)} · المرجع ${refId||'غير محدد'}`,1690,24,'400',1140)}

  function semanticMath(a,b,result='□'){
    const engine=[result,'=',b,'+',a];
    const student=[...engine].reverse();
    return {engine,student,student_text:student.join(' '),engine_text:engine.join(' ')};
  }
  function drawMathRow(ctx,a,b,y,result='□'){
    const m=semanticMath(a,b,result),tokens=m.student;
    // Student-eye physical order is explicit L→R: A + B = R. No BiDi layout is delegated.
    const start=280,gap=170;ctx.direction='ltr';ctx.textAlign='center';ctx.fillStyle='#111827';ctx.font='700 72px Tahoma, Arial, sans-serif';
    const positions=[];tokens.forEach((t,i)=>{const x=start+i*gap;ctx.fillText(t,x,y);positions.push({token:t,x,y});});ctx.direction='rtl';ctx.textAlign='right';
    return {...m,positions,equals_index:3,answer_index:4};
  }
  function drawDots(ctx,count,x0,y,color='#17324d'){
    ctx.fillStyle=color;for(let i=0;i<count;i++){ctx.beginPath();ctx.arc(x0+i*58,y,18,0,Math.PI*2);ctx.fill();}
  }

  function teacherPage(contract,refs){
    const {canvas,ctx}=baseContext(),r=refs?.[0]||{};ctx.fillStyle='#17324d';ctx.fillRect(0,0,CANVAS.w,26);
    line(ctx,'خطة درس — كفايات Ω',120,58,'700');
    line(ctx,`المادة: ${contract.subject==='mathematics'?'الرياضيات':contract.subject==='arabic'?'اللغة العربية':contract.subject==='islamic_education'?'التربية الإسلامية':'التنشئة'}`,190,34,'700');
    line(ctx,`الصف: ${eastern(contract.grade||'—')}  ·  زمن مقترح: ٤٥ دقيقة`,245,32,'400');separator(ctx,285);
    line(ctx,'الغاية التي طلبها المستخدم',350,38,'700');let y=wrap(ctx,contract.goal,1140,405,1000,48,32,'400',4);
    line(ctx,'الهدف التعلمي',y+45,38,'700');const objective=r.criterion||r.main_competency||r.sub_competency||r.source_text||'هدف مرتبط مباشرة بالمرجع المسترجع';y=wrap(ctx,objective,1140,y+100,1000,48,32,'400',5);
    line(ctx,'نشاط رئيسي',y+45,38,'700');
    const activity=contract.subject==='mathematics'?'مثّل كميتين بمحسوسات، اجمعهما، ثم انتقل إلى الرسم والرمز مع الحفاظ على هوية كل كمية وترتيبها.':'نفّذ نشاطًا واحدًا مرتبطًا مباشرة بالهدف والمرجع، ثم اطلب أداءً ملاحظًا من المتعلم.';
    y=wrap(ctx,activity,1140,y+100,1000,48,32,'400',5);
    line(ctx,'تقويم ختامي سريع',y+45,38,'700');
    wrap(ctx,contract.subject==='mathematics'?'اعرض مسألة واحدة جديدة من النوع نفسه، واطلب من الطالب إكمالها وشرح ما فعل.':'اطلب أداءً قصيرًا يقيس الهدف نفسه مباشرة.',1140,y+100,1000,48,32,'400',4);
    rounded(ctx,100,1370,1040,170);line(ctx,`حالة المصدر: ${r.provenance?.status||'NOT PROVEN'}`,1430,28,'700');wrap(ctx,`معرّف المرجع: ${r.id||'غير محدد'} · لا تُفهم هذه البطاقة على أنها اعتماد رسمي ما لم يكن المصدر موثقًا بذلك.`,1100,1485,960,38,25,'400',3);
    drawFooter(ctx,1,r.id);return {canvas,meta:{page:'teacher',ref_id:r.id||null}};
  }

  function studentMathPage(contract,refs){
    const {canvas,ctx}=baseContext(),r=refs?.[0]||{};ctx.fillStyle='#17324d';ctx.fillRect(0,0,CANVAS.w,26);
    line(ctx,'ورقة الطالب — الجمع ضمن ١٠',120,58,'700');line(ctx,`الاسم: ____________________     الصف: ${eastern(contract.grade||'—')}`,190,32,'400');separator(ctx,235);
    line(ctx,'أعدّ المجموعتين، ثم أكمل.',310,38,'700');
    drawDots(ctx,4,260,415);ctx.fillStyle='#111827';ctx.direction='ltr';ctx.textAlign='center';ctx.font='700 54px Arial';ctx.fillText('+',610,432);drawDots(ctx,3,730,415);ctx.direction='rtl';ctx.textAlign='right';
    const rows=[];rows.push(drawMathRow(ctx,'٤','٣',585));separator(ctx,650);
    line(ctx,'أكمل المسائل.',725,38,'700');rows.push(drawMathRow(ctx,'٥','٢',880));rows.push(drawMathRow(ctx,'١','٨',1050));rows.push(drawMathRow(ctx,'٦','٣',1220));
    rounded(ctx,100,1320,1040,210);line(ctx,'تحقق من إجابتك:',1390,34,'700');wrap(ctx,'هل جمعت الكميتين؟ هل بقيت علامة = في مكانها بين العدد الثاني ومربع الإجابة؟',1100,1450,960,46,30,'400',3);
    drawFooter(ctx,2,r.id);
    return {canvas,meta:{page:'student',ref_id:r.id||null,math_rows:rows,student_eye_strings:rows.map(x=>x.student_text)}};
  }

  function genericStudentPage(contract,refs){
    const {canvas,ctx}=baseContext(),r=refs?.[0]||{};ctx.fillStyle='#17324d';ctx.fillRect(0,0,CANVAS.w,26);
    line(ctx,'ورقة تعلم — كفايات Ω',120,58,'700');line(ctx,`الصف: ${eastern(contract.grade||'—')}`,185,32,'400');separator(ctx,230);
    line(ctx,'المهمة',310,40,'700');let y=wrap(ctx,contract.goal,1140,370,1000,50,32,'400',5);
    line(ctx,'أعمل اعتمادًا على المرجع',y+50,38,'700');y=wrap(ctx,r.source_text||r.criterion||r.main_competency||'لا يوجد نص مرجعي مثبت.',1140,y+110,1000,48,30,'400',8);
    line(ctx,'أثر تعلم أقدمه',y+50,38,'700');rounded(ctx,120,y+100,1000,300);drawFooter(ctx,2,r.id);return {canvas,meta:{page:'student',ref_id:r.id||null,math_rows:[]}};
  }

  function canvasToJpeg(canvas,quality=.94){
    return new Promise((resolve,reject)=>canvas.toBlob(async blob=>{
      if(!blob)return reject(new Error('CANVAS_JPEG_FAILED'));resolve(new Uint8Array(await blob.arrayBuffer()));
    },'image/jpeg',quality));
  }
  async function buildLessonPdf(contract,refs=[]){
    requireBrowser();if(!contract?.grade||!contract?.subject)throw new Error('RESOLVED_CONTRACT_REQUIRED');
    const pages=[teacherPage(contract,refs),contract.subject==='mathematics'?studentMathPage(contract,refs):genericStudentPage(contract,refs)];
    const images=[];for(const p of pages)images.push({bytes:await canvasToJpeg(p.canvas),width:p.canvas.width,height:p.canvas.height});
    const bytes=serializeImagePdf(images),blob=new Blob([bytes],{type:'application/pdf'}),filename=safeName(contract);
    const mathRows=pages.flatMap(p=>p.meta.math_rows||[]),studentStrings=mathRows.map(r=>r.student_text);
    const evidence={
      actual_pdf_exists:bytes.length>1000&&String.fromCharCode(...bytes.slice(0,8)).startsWith('%PDF-1.'),
      actual_pdf_opens:false,
      all_pages_checked:false,
      print_pass:false,
      mobile_pass:false,
      student_eye_math_pass:contract.subject!=='mathematics'||studentStrings.every(s=>/^\s*[٠-٩]+\s+\+\s+[٠-٩]+\s+=\s+□\s*$/.test(s)),
      eastern_digits_pass:contract.subject!=='mathematics'||studentStrings.every(s=>!/[0-9]/.test(s)),
      equals_position_pass:contract.subject!=='mathematics'||mathRows.every(r=>r.student[3]==='='&&r.student[4]==='□'&&r.positions.every((p,i,a)=>i===0||p.x>a[i-1].x)),
      page_count:pages.length,
      student_eye_strings:studentStrings,
      engine_requests:mathRows.map(r=>r.engine_text),
      renderer:'EXPLICIT_TOKEN_GEOMETRY_TO_CANVAS_RASTER_PDF'
    };
    return {bytes,blob,filename,evidence,pages:pages.map(p=>p.meta),previewCanvases:pages.map(p=>p.canvas)};
  }
  function downloadArtifact(artifact){
    requireBrowser();const url=URL.createObjectURL(artifact.blob),a=document.createElement('a');a.href=url;a.download=artifact.filename;document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),30000);return artifact.filename;
  }

  return {eastern,semanticMath,serializeImagePdf,buildLessonPdf,downloadArtifact,PAGE_PT,CANVAS};
});
