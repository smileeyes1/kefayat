#!/usr/bin/env python3
"""Structural and Golden Render regression for the browser-native PDF engine."""
from __future__ import annotations
import base64, json, re, subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
ENGINE=ROOT/'artifact'/'pdf-artifact-engine.js'


def node(script:str)->dict:
    p=subprocess.run(['node','-e',script],cwd=ROOT,text=True,capture_output=True,check=False)
    assert p.returncode==0,p.stderr
    return json.loads(p.stdout.strip())


def main()->None:
    assert ENGINE.is_file() and ENGINE.stat().st_size>5000
    source=ENGINE.read_text(encoding='utf-8')
    for marker in ('serializeImagePdf','buildLessonPdf','semanticMath','EXPLICIT_TOKEN_GEOMETRY_TO_CANVAS_RASTER_PDF','image/jpeg','toBlob'):
        assert marker in source,marker

    result=node(r'''
const A=require('./artifact/pdf-artifact-engine.js');
const m=A.semanticMath('٤','٣','□');
const jpeg=new Uint8Array([0xff,0xd8,0xff,0xd9]);
const pdf=A.serializeImagePdf([{bytes:jpeg,width:1,height:1},{bytes:jpeg,width:1,height:1}]);
console.log(JSON.stringify({m,len:pdf.length,b64:Buffer.from(pdf).toString('base64')}));
''')
    m=result['m']
    assert m['engine_text']=='□ = ٣ + ٤',m
    assert m['student_text']=='٤ + ٣ = □',m
    assert m['student']==['٤','+','٣','=','□'],m
    assert not re.search(r'[0-9]',m['student_text'])

    pdf=base64.b64decode(result['b64'])
    assert pdf.startswith(b'%PDF-1.4\n')
    assert pdf.rstrip().endswith(b'%%EOF')
    assert b'/Type /Pages /Count 2' in pdf
    assert pdf.count(b'/Type /Page ') == 2
    sx=re.search(rb'startxref\n(\d+)\n%%EOF',pdf)
    assert sx, 'startxref missing'
    pos=int(sx.group(1));assert pdf[pos:pos+4]==b'xref', (pos,pdf[pos:pos+20])
    assert b'/Filter /DCTDecode' in pdf
    print('PDF ARTIFACT ENGINE REGRESSION: PASS')

if __name__=='__main__':main()
