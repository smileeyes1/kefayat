/* KEFAYAT Ω Intent Contract + Fulfillment Engine v1.1
 * Deterministic, local-first intent compiler. No network dependency.
 * Deep generation may be delegated to an AI provider only after this contract is frozen.
 */
(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports) module.exports=api;
  root.KefayatIntent=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';

  const SUBJECTS={
    mathematics:['رياض','جمع','طرح','ضرب','قسمة','كمية','هندسة','قياس','مساله','مسألة','كسور','اشكال','أشكال'],
    arabic:['حرف','قراءة','قراءه','كتابة','كتابه','استماع','تحدث','لغة','لغه','نص','هجاء','املاء','إملاء','قصة','قصه'],
    islamic_education:['وضوء','صلاة','صلاه','قران','قرآن','حديث','سيرة','سيره','اسلام','إسلام','عبادة','عباده','توحيد','فقه'],
    nurturing:['حواس','اسرة','اسرتي','اسره','بيئة','بيئه','حيوان','نبات','فصول','مواطن','مدرسة','مدرسه','مجتمع','فلسطين','وطن','حياة','حياه']
  };
  const GRADE_WORDS={
    1:['الصف الاول','صف اول','الأول','اول'],
    2:['الصف الثاني','صف ثاني','الثاني','ثاني'],
    3:['الصف الثالث','صف ثالث','الثالث','ثالث'],
    4:['الصف الرابع','صف رابع','الرابع','رابع']
  };
  const ARTIFACTS=[
    ['pdf',/\bpdf\b|بي\s*دي\s*اف|ملف\s*pdf|بصيغة\s*pdf/i],
    ['docx',/\bdocx\b|word|وورد/i],
    ['html',/\bhtml\b|صفحة\s*ويب|ملف\s*ويب/i],
    ['worksheet',/ورقة\s*عمل|ورقه\s*عمل/i],
    ['lesson_plan',/تحضير|خطة\s*درس|خطه\s*درس/i],
    ['text',/نص|صياغة|صياغه/i]
  ];
  const STOP_TERMS=new Set(['انشئ','اعمل','اريد','جهز','اصنع','اكتب','صمم','ملف','درس','كملف','بصيغه','بصيغة','للطالب','للمعلم']);

  function normalizeArabic(value){
    return String(value??'').normalize('NFKC')
      .replace(/[\u064B-\u065F\u0670]/g,'')
      .replace(/[أإآ]/g,'ا').replace(/ى/g,'ي').replace(/ة/g,'ه')
      .replace(/ـ/g,'').toLowerCase().replace(/\s+/g,' ').trim();
  }
  function westernDigits(value){
    return normalizeArabic(value).replace(/[٠-٩]/g,d=>String('٠١٢٣٤٥٦٧٨٩'.indexOf(d)));
  }
  function tokenize(value){
    return normalizeArabic(value).split(/[^\p{L}\p{N}]+/u).filter(Boolean);
  }
  function isNumericToken(t){return /^[٠-٩0-9]+$/.test(t)}
  function evidenceTerms(value){
    return tokenize(value).filter(t=>!STOP_TERMS.has(t)&&(t.length>2||isNumericToken(t)));
  }
  function uniq(xs){return [...new Set(xs.filter(Boolean))]}
  function hit(q,needles){return needles.reduce((n,x)=>n+(q.includes(normalizeArabic(x))?1:0),0)}

  function detectSubject(text,explicit){
    if(explicit&&explicit!=='all'&&SUBJECTS[explicit]) return {value:explicit,source:'explicit',confidence:1,scores:{[explicit]:100}};
    const q=normalizeArabic(text),scores={};
    for(const [subject,words] of Object.entries(SUBJECTS)) scores[subject]=hit(q,words)*8;
    // Generic words such as "عدد" and "رقم" are too ambiguous on their own (e.g. page count).
    // Treat them as mathematics only in educational-number contexts.
    if(/(?:درس|تعلم|تعليم|تمرين|تمارين)\s+(?:ال)?عدد/.test(q)||/(?:ال)?عدد\s*[٠-٩0-9]+/.test(q)||/الاعداد|اعداد\s+(?:ضمن|حتي|حتى)/.test(q)) scores.mathematics+=10;
    if(/عد\s+(?:الاشياء|الاشكال|العناصر)|العد\s+(?:ضمن|حتي|حتى)/.test(q)) scores.mathematics+=8;
    const ranked=Object.entries(scores).sort((a,b)=>b[1]-a[1]);
    if(!ranked[0]||ranked[0][1]===0) return {value:null,source:'unresolved',confidence:0,scores};
    const margin=ranked[0][1]-(ranked[1]?.[1]||0);
    if(margin===0) return {value:null,source:'ambiguous',confidence:0.4,scores};
    return {value:ranked[0][0],source:'lexical',confidence:Math.min(0.96,0.62+margin/32),scores};
  }

  function explicitGrade(text,gradeHint){
    if(gradeHint&&gradeHint!=='all'){
      const n=Number(westernDigits(gradeHint).match(/[1-4]/)?.[0]);
      if(n) return {value:n,source:'explicit',confidence:1};
    }
    const q=westernDigits(text);
    const numeric=q.match(/(?:الصف|صف)\s*([1-4])/);
    if(numeric) return {value:Number(numeric[1]),source:'explicit-text',confidence:1};
    for(const [g,words] of Object.entries(GRADE_WORDS)) if(words.some(w=>q.includes(normalizeArabic(w)))) return {value:Number(g),source:'explicit-text',confidence:0.98};
    return null;
  }

  function inferGradeFromEvidence(text,subject,records){
    if(!subject||!Array.isArray(records)||!records.length) return {value:null,source:'unresolved',confidence:0,scores:{}};
    const terms=evidenceTerms(text);
    const scores={1:0,2:0,3:0,4:0},hits={1:0,2:0,3:0,4:0},best_record_ids={1:null,2:null,3:null,4:null};
    for(const r of records){
      const grade=Number(r?.grade);
      if(r?.subject!==subject||![1,2,3,4].includes(grade)) continue;
      const hay=normalizeArabic([r.id,r.main_competency,r.sub_competency,r.domain,r.criterion,r.source_text].join(' '));
      let score=0,matched=0;
      for(const t of terms){
        if(!hay.includes(t)) continue;
        matched++;
        score+=isNumericToken(t)?20:Math.min(12,3+t.length);
      }
      // Compare the strongest matching evidence record per grade. This avoids a grade
      // winning merely because it contains more source records than another grade.
      if(score>scores[grade]){scores[grade]=score;hits[grade]=matched;best_record_ids[grade]=r.id||null;}
    }
    const ranked=Object.entries(scores).map(([g,s])=>[Number(g),s]).sort((a,b)=>b[1]-a[1]);
    const [best,second]=[ranked[0],ranked[1]||[0,0]];
    const margin=best?.[1]-(second?.[1]||0);
    if(!best||best[1]===0||margin<5) return {value:null,source:'ambiguous-evidence',confidence:0.35,scores,hits,best_record_ids};
    return {value:best[0],source:'evidence-inference',confidence:Math.min(0.94,0.62+margin/45),scores,hits,best_record_ids};
  }

  function detectArtifact(text){
    for(const [type,re] of ARTIFACTS) if(re.test(String(text))) return type;
    return 'response';
  }
  function detectTask(text){
    const q=normalizeArabic(text);
    if(/عدل|تعديل|اصلح|اصلاح|حدث|تحديث|طور|تطوير|حسن|تحسين/.test(q)) return 'modify';
    if(/راجع|مراجعه|دقق|تدقيق|افحص|تحقق|قيم|تقييم/.test(q)) return 'review';
    if(/ورقة عمل|ورقه عمل|تدريب|تمارين/.test(q)) return 'worksheet';
    if(/درس|تحضير|خطة درس|خطه درس|تعليم/.test(q)) return 'lesson';
    if(/انشئ|اصنع|جهز|اكتب|صمم/.test(q)) return 'create';
    return 'mission';
  }
  function detectAudience(text,context){
    const q=normalizeArabic(text);
    if(/للطالب|للطلاب|الطالب|الطلاب|التلميذ/.test(q)) return 'student';
    if(/للمعلم|المعلم/.test(q)) return 'teacher';
    return context?.role||'teacher';
  }

  function deriveRequirements(text,artifact,subject,task,context={}){
    const q=normalizeArabic(text),hard=[],preferences=[];
    if(artifact==='pdf') hard.push('DELIVER_ACTUAL_PDF','PDF_OPENS','TESTED_ARTIFACT_EQUALS_DELIVERED_ARTIFACT');
    if(artifact==='docx') hard.push('DELIVER_ACTUAL_DOCX','TESTED_ARTIFACT_EQUALS_DELIVERED_ARTIFACT');
    if(artifact==='html') hard.push('DELIVER_ACTUAL_HTML','OFFLINE_SAFE_WHEN_REQUESTED');
    if(subject==='mathematics') hard.push('P0_GOLDEN_RENDER','OPERAND_IDENTITY_IMMUTABLE','EASTERN_ARABIC_DIGITS','USER_EYE_RENDER_AUTHORITY');
    if(/عربي|العربيه|rtl|يمين/.test(q)||['mathematics','arabic','islamic_education','nurturing'].includes(subject)) hard.push('ARABIC_NATIVE','RTL_INTERFACE');
    if(/طباع|اطبع|جاهز للطباعة|جاهزه للطباعه/.test(q)||['pdf','worksheet','lesson_plan'].includes(artifact)) hard.push('PRINT_READY');
    if(/هاتف|موبايل|جوال/.test(q)) hard.push('MOBILE_USABLE');
    if(context.education_system==='palestinian'||/فلسطين|فلسطيني|المنهاج الفلسطيني|المنهج الفلسطيني/.test(q)) hard.push('PALESTINIAN_CONTEXT');
    if(/دون كسر|لا تغير|لا تغيّر|حافظ|ثبت|مثبت|baseline|golden/.test(q)||task==='modify') hard.push('PRESERVE_VERIFIED_BASELINES','NO_REGRESSION');
    if(/بسيط|بسيطه|مختصر/.test(q)) preferences.push('CONCISE');
    if(/اعلى|افضل|احتراف|مهني/.test(q)) preferences.push('MAXIMIZE_QUALITY_WITHIN_CONTRACT');
    return {hard:uniq(hard),preferences:uniq(preferences)};
  }

  function acceptanceFor(contract){
    const a=['INTENT_PRESERVED','RELEVANT_EVIDENCE_USED','NO_UNSUPPORTED_CLAIM','NO_REGRESSION'];
    if(contract.subject) a.push('SUBJECT_MATCH');
    if(contract.grade) a.push('GRADE_MATCH');
    if(contract.artifact_type==='pdf') a.push('ACTUAL_PDF_EXISTS','ACTUAL_PDF_OPENS','ALL_PAGES_CHECKED');
    if(contract.artifact_type==='docx') a.push('ACTUAL_DOCX_EXISTS','ACTUAL_DOCX_OPENS');
    if(contract.subject==='mathematics') a.push('STUDENT_EYE_MATH_PASS','EASTERN_DIGITS_PASS','EQUALS_POSITION_PASS');
    if(contract.hard_requirements.includes('PRINT_READY')) a.push('PRINT_PASS');
    if(contract.hard_requirements.includes('MOBILE_USABLE')) a.push('MOBILE_PASS');
    return uniq(a);
  }

  function compileContract(input,records=[],context={}){
    const request=String(input?.text??input??'').trim();
    const subjectInfo=detectSubject(request,input?.subject||context.subject);
    const eg=explicitGrade(request,input?.grade||context.grade);
    const gradeInfo=eg||inferGradeFromEvidence(request,subjectInfo.value,records);
    const artifact=detectArtifact(request),task=detectTask(request),audience=detectAudience(request,context);
    const req=deriveRequirements(request,artifact,subjectInfo.value,task,context);
    const unresolved=[];
    if(!request) unresolved.push('goal');
    if(!subjectInfo.value) unresolved.push('subject');
    if(!gradeInfo?.value&&['lesson','worksheet'].includes(task)) unresolved.push('grade');
    const contract={
      schema:'KEFAYAT_INTENT_CONTRACT_V1',
      engine_version:'1.1',
      request,
      goal:request,
      role:context.role||'teacher',
      audience,
      context_scope:context.education_system==='palestinian'?'PALESTINIAN_EDUCATION':(context.context_scope||null),
      task_type:task,
      subject:subjectInfo.value,
      subject_resolution:subjectInfo,
      grade:gradeInfo?.value||null,
      grade_resolution:gradeInfo||{value:null,source:'unresolved',confidence:0},
      artifact_type:artifact,
      hard_requirements:req.hard,
      preferences:req.preferences,
      protected_invariants:subjectInfo.value==='mathematics'?
        ['SEMANTIC_USER_EYE_A_PLUS_B_EQUALS_R','ENGINE_REQUEST_R_EQUALS_B_PLUS_A','OPERAND_IDENTITY_IMMUTABLE','FINAL_RENDER_IS_AUTHORITY']:[],
      unresolved,
      assumptions:[],
      acceptance_criteria:[],
      ready_for_execution:unresolved.length===0,
      confidence:Math.min(subjectInfo.confidence||0,gradeInfo?.confidence??1)
    };
    contract.acceptance_criteria=acceptanceFor(contract);
    return contract;
  }

  function retrieveEvidence(contract,records=[],limit=6){
    if(!contract||!Array.isArray(records)) return [];
    const terms=evidenceTerms(contract.request);
    return records.filter(r=>(!contract.subject||r.subject===contract.subject)&&(!contract.grade||Number(r.grade)===Number(contract.grade)))
      .map(r=>{
        const hay=normalizeArabic([r.id,r.main_competency,r.sub_competency,r.domain,r.criterion,r.source_text].join(' '));
        let score=(contract.subject===r.subject?50:0)+(contract.grade&&Number(contract.grade)===Number(r.grade)?25:0);
        for(const t of terms) if(hay.includes(t)) score+=isNumericToken(t)?14:Math.min(8,t.length);
        return {record:r,score};
      }).sort((a,b)=>b.score-a.score).slice(0,limit).map(x=>x.record);
  }

  function contractGate(contract,refs){
    const reasons=[];
    if(!contract?.request) reasons.push('الغاية فارغة');
    if(!contract?.subject) reasons.push('المجال غير محسوم');
    if(['lesson','worksheet'].includes(contract?.task_type)&&!contract?.grade) reasons.push('الصف غير محسوم بدليل كافٍ');
    if(!Array.isArray(refs)||!refs.length) reasons.push('لا يوجد دليل مطابق كافٍ');
    if(Array.isArray(refs)&&contract?.subject&&refs.some(r=>r.subject!==contract.subject)) reasons.push('Cross-Domain contamination');
    return {pass:reasons.length===0,reasons};
  }

  function buildPlan(contract,refs){
    const steps=['FREEZE_INTENT_CONTRACT','RETRIEVE_AUTHORITATIVE_EVIDENCE','DESIGN_FROM_CONTRACT'];
    if(contract.artifact_type!=='response') steps.push('BUILD_REAL_ARTIFACT');
    steps.push('STRUCTURAL_QA','SEMANTIC_QA');
    if(contract.subject==='mathematics') steps.push('P0_GOLDEN_RENDER_QA','USER_EYE_QA');
    if(contract.artifact_type==='pdf') steps.push('OPEN_PDF','ALL_PAGES_QA','PRINT_QA');
    steps.push('ADVERSARIAL_CHECK','REPAIR_IF_NEEDED','REGRESSION','ACCEPTANCE_ORACLE','DELIVER_EXACT_VERIFIED_ARTIFACT');
    return {steps,evidence_ids:(refs||[]).map(r=>r.id),terminal_rule:'PASS only when every applicable acceptance criterion is evidenced'};
  }

  function localDraft(contract,refs){
    const gate=contractGate(contract,refs);
    if(!gate.pass) return {status:'NO-GO',text:'لا يجوز التنفيذ النهائي بعد: '+gate.reasons.join('؛ '),gate};
    const r=refs[0]||{};
    const title=contract.request;
    let body=`الغاية: ${title}\nالمادة: ${contract.subject}\nالصف: ${contract.grade}\nنوع المهمة: ${contract.task_type}\nالمرجع: ${r.id||'غير محدد'}\n`;
    if(contract.task_type==='lesson') body+=`\nتصميم أولي منضبط بالعقد:\n- هدف تعلم واحد قابل للملاحظة.\n- نشاط رئيسي واحد مرتبط بالدليل.\n- تقويم ختامي قصير يقيس الهدف نفسه.\n`;
    if(contract.subject==='mathematics') body+=`\nقفل العرض الرياضي P0: الناتج النهائي لعين الطالب هو السلطة؛ البناء الداخلي المحمي R = B + A لا يبرر تبديل هوية الحدود.\n`;
    if(contract.artifact_type==='pdf') body+=`\nحالة التسليم: لم يُنشأ PDF ثنائي فعلي داخل هذا المسار المحلي بعد؛ لذلك لا تُعد المهمة مكتملة حتى يوجد PDF حقيقي ويفتح ويجتاز فحص جميع الصفحات.\n`;
    body+=`\nمعايير القبول: ${contract.acceptance_criteria.join('، ')}.`;
    return {status:contract.artifact_type==='response'?'DRAFT_READY':'ARTIFACT_BUILD_REQUIRED',text:body,gate};
  }

  function acceptanceOracle(contract,refs,evidence={}){
    const gate=contractGate(contract,refs),failed=[];
    if(!gate.pass) failed.push(...gate.reasons.map(x=>'CONTRACT:'+x));
    if(contract?.artifact_type==='pdf'){
      if(!evidence.actual_pdf_exists) failed.push('ACTUAL_PDF_EXISTS');
      if(!evidence.actual_pdf_opens) failed.push('ACTUAL_PDF_OPENS');
      if(!evidence.all_pages_checked) failed.push('ALL_PAGES_CHECKED');
    }
    if(contract?.subject==='mathematics'){
      if(!evidence.student_eye_math_pass) failed.push('STUDENT_EYE_MATH_PASS');
      if(!evidence.eastern_digits_pass) failed.push('EASTERN_DIGITS_PASS');
      if(!evidence.equals_position_pass) failed.push('EQUALS_POSITION_PASS');
    }
    if(contract?.hard_requirements?.includes('PRINT_READY')&&!evidence.print_pass) failed.push('PRINT_PASS');
    if(contract?.hard_requirements?.includes('MOBILE_USABLE')&&!evidence.mobile_pass) failed.push('MOBILE_PASS');
    return {decision:failed.length?'NOT_PROVEN':'PASS',failed:uniq(failed),claim_scope:failed.length?'Do not claim fulfillment':'Intent fulfilled within evidenced acceptance scope'};
  }

  return {normalizeArabic,westernDigits,detectSubject,explicitGrade,inferGradeFromEvidence,detectArtifact,detectTask,compileContract,retrieveEvidence,contractGate,buildPlan,localDraft,acceptanceOracle};
});