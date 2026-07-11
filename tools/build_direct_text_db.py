import re, json, subprocess, pathlib, unicodedata, copy
BASE=pathlib.Path('/mnt/data')
WORK=BASE/'engine_work'
master=json.load(open(WORK/'data/tokyo_master.json',encoding='utf-8'))
files={
  2021:(BASE/'r3mondaiam.pdf',BASE/'r3mondaipm.pdf'),
  2022:(BASE/'r04mondaiam.pdf',BASE/'r04mondaipm.pdf'),
  2023:(BASE/'r5mondaiam.pdf',BASE/'r5mondaipm.pdf'),
  2024:(BASE/'掲載ファイル_令和6年度東京都登録販売者試験　試験問題（午前）.pdf',BASE/'掲載ファイル_令和6年度東京都登録販売者試験　試験問題（午後）.pdf'),
}
FW='０１２３４５６７８９'
def nnum(s):
    return int(''.join(str(FW.index(c)) if c in FW else c for c in s))

def extract_pdf(pdf):
    out=BASE/'pdftext'/f'{pdf.stem}_layout.txt'; out.parent.mkdir(exist_ok=True)
    subprocess.run(['pdftotext','-layout',str(pdf),str(out)],check=True)
    t=out.read_text(encoding='utf-8',errors='replace')
    t=t.replace('\x03','').replace('\u000b','').replace('\r','')
    return t

def clean_lines(block):
    lines=[]
    for raw in block.splitlines():
        s=raw.strip()
        if not s: continue
        if re.fullmatch(r'\d{1,2}',s): continue
        # isolated furigana lines
        if re.fullmatch(r'[ぁ-んァ-ヶー]{1,8}',s): continue
        s=re.sub(r'[\u0000-\u001f]','',s)
        s=re.sub(r'[ \t　]+',' ',s).strip()
        if s: lines.append(s)
    return lines

def split_questions(text):
    # Normalize question numbers and capture only 1..120
    pat=re.compile(r'(?m)(?<!解答例)(?:^|\f)\s*問\s*([０-９0-9]{1,3})\s*')
    ms=list(pat.finditer(text)); out={}
    for i,m in enumerate(ms):
        try:n=nnum(m.group(1))
        except:continue
        if not 1<=n<=120: continue
        end=ms[i+1].start() if i+1<len(ms) else len(text)
        block='問'+str(n)+' '+text[m.end():end]
        # prefer first occurrence, duplicates from repeated pages ignored
        if n not in out or len(block)>len(out[n]): out[n]=block
    return out

def parse_choices(lines):
    # Find numbered option starts, supporting full-width digits and inline options
    joined='\n'.join(lines)
    # inline combo options
    combo=[]
    for m in re.finditer(r'(?:^|\s)([１-５1-5])\s*[（(]\s*([ａ-ｄa-d])\s*[、,，]\s*([ａ-ｄa-d])\s*[）)]',joined):
        combo.append((nnum(m.group(1)),f'({m.group(2).lower()},{m.group(3).lower()})'))
    if len({i for i,_ in combo})==5:
        return [dict(combo)[i] for i in range(1,6)]
    # numbered rows / prose options. split globally from final section
    matches=list(re.finditer(r'(?m)(?:^|\n)\s*([１-５1-5])\s+([^\n]+)',joined))
    by={}
    for idx,m in enumerate(matches):
        i=nnum(m.group(1)); val=m.group(2).strip()
        if 1<=i<=5:
            # accept likely choice rows, later occurrences override only if plausible
            if re.search(r'正|誤|増|減|有|無|[（(]|[ぁ-んァ-ヶ一-龯]',val): by[i]=val
    if len(by)==5: return [by[i] for i in range(1,6)]
    # same-line rows such as １ 正... ２ ...
    by={}
    for m in re.finditer(r'([１-５1-5])\s+(.+?)(?=\s+[１-５1-5]\s+|$)',joined.replace('\n',' ')):
        i=nnum(m.group(1)); v=m.group(2).strip()
        if 1<=i<=5 and v: by[i]=v
    if len(by)==5:return [by[i] for i in range(1,6)]
    return None

def clean_question(block, fallback_choices):
    lines=clean_lines(block)
    choices=parse_choices(lines)
    # Remove option rows from displayed question, retain a-d statements and tables
    kept=[]
    for s in lines:
        if re.match(r'^[１-５1-5]\s+',s):
            continue
        if re.match(r'^[１-５1-5][（(]',s):
            continue
        # remove header/footer garbage
        if s in {'医薬品に共通する特性と基本的な知識','人体の働きと医薬品','薬事に関する法規と制度','主な医薬品とその作用','医薬品の適正使用と安全対策'}: continue
        kept.append(s)
    # join wrapped prose while preserving statement markers
    text='\n'.join(kept)
    text=re.sub(r'\n(?=[^ａｂｃｄabcd問])','',text)
    text=re.sub(r'\n(?=[ａｂｃｄabcd]\s)','\n',text)
    text=re.sub(r'\s+',' ',text)
    # restore line breaks before statement markers
    text=re.sub(r'\s([ａｂｃｄ])\s+',r'\n\1 ',text)
    text=re.sub(r'^問(\d+)\s*',lambda m:f'問{m.group(1)} ',text)
    text=text.strip()
    return text, choices or fallback_choices

allq=master['questions']; index={(int(q['year']),int(q['question_no'])):q for q in allq}
report={}
for year,(am,pm) in files.items():
    blocks={}; blocks.update(split_questions(extract_pdf(am))); blocks.update(split_questions(extract_pdf(pm)))
    ok=0; bad=[]
    for n in range(1,121):
        q=index[(year,n)]
        b=blocks.get(n)
        if not b: bad.append((n,'missing')); continue
        text,choices=clean_question(b,q.get('choices',[]))
        if len(text)<30 or len(choices)!=5:
            bad.append((n,f'text={len(text)},choices={len(choices)}')); continue
        q['question_text']=text
        q['choices']=choices
        q['raw_text']=b
        q['source_type']='official_pdf_text'
        q['source_file']={'pdf':str(am.name if n<=60 else pm.name)}
        ok+=1
    report[year]={'blocks':len(blocks),'updated':ok,'issues':bad[:20]}
master['generated_at']='2026-07-12T00:00:00+09:00'
master['extraction_mode']='official_pdf_text_first_ocr_fallback'
master['count']=len(allq)
out=WORK/'data/tokyo_master.json'
json.dump(master,open(out,'w',encoding='utf-8'),ensure_ascii=False,indent=2)
json.dump(report,open(WORK/'data/direct_text_report.json','w',encoding='utf-8'),ensure_ascii=False,indent=2)
print(json.dumps(report,ensure_ascii=False,indent=2))
