#!/usr/bin/env python3
"""Validate chapter/image paths and build an EPUB 3 using standard library + Pillow."""
from pathlib import Path
import datetime,html,io,json,posixpath,re,uuid,zipfile
from xml.etree import ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
BUILD=ROOT/'build'
def inline(s):
 s=html.escape(s,quote=True)
 rules=[(r'!\[([^\]]*)\]\(([^\s)]+)\)',r'<img alt="\1" src="\2" />'),(r'\[([^\]]+)\]\(([^\s)]+)\)',r'<a href="\2">\1</a>'),(r'`([^`]+)`',r'<code>\1</code>'),(r'\*\*([^*]+)\*\*',r'<strong>\1</strong>'),(r'(?<!\*)\*([^*]+)\*(?!\*)',r'<em>\1</em>')]
 for p,r in rules:s=re.sub(p,r,s)
 return s
def markdown(t):
 lines=t.splitlines();out=[];i=0
 while i<len(lines):
  s=lines[i].strip()
  if not s:i+=1;continue
  h=re.match(r'^(#{1,6})\s+(.+)',s)
  if h:
   n=len(h[1]);out.append(f'<h{n}>'+inline(h[2])+f'</h{n}>');i+=1;continue
  if s.startswith('|'):
   rows=[]
   while i<len(lines) and lines[i].strip().startswith('|'):
    cells=[x.strip() for x in lines[i].strip().strip('|').split('|')]
    if not all(re.fullmatch(r':?-+:?',x.replace(' ','')) for x in cells):rows.append(cells)
    i+=1
   out.append('<table>')
   for k,cells in enumerate(rows):
    tag='th' if k==0 else 'td';out.append('<tr>'+''.join(f'<{tag}>'+inline(x)+f'</{tag}>' for x in cells)+'</tr>')
   out.append('</table>');continue
  if re.match(r'^([-*+] |\d+[.)] )',s):
   ordered=bool(re.match(r'^\d',s));tag='ol' if ordered else 'ul';out.append('<'+tag+'>')
   pattern=r'^\s*\d+[.)] ' if ordered else r'^\s*[-*+] '
   while i<len(lines) and re.match(pattern,lines[i]):
    out.append('<li>'+inline(re.sub(r'^\s*([-*+] |\d+[.)] )','',lines[i]))+'</li>');i+=1
   out.append('</'+tag+'>');continue
  if s.startswith('>'):out.append('<blockquote><p>'+inline(s.lstrip('> '))+'</p></blockquote>');i+=1;continue
  if re.fullmatch(r'[-*_]{3,}',s):out.append('<hr />');i+=1;continue
  para=[s];i+=1
  while i<len(lines) and lines[i].strip() and not re.match(r'^(#{1,6}\s|\||>|[-*+] |\d+[.)] )',lines[i].strip()):para.append(lines[i].strip());i+=1
  out.append('<p>'+inline(' '.join(para))+'</p>')
 return '\n'.join(out)
CSS='body{font-family:serif;line-height:1.85;margin:5%;color:#243b35}h1,h2,h3{color:#285344;line-height:1.4}h1{font-size:1.7em}h2{font-size:1.25em;margin-top:1.8em}p{margin:.85em 0}img{display:block;max-width:100%;height:auto;margin:1.5em auto .6em}em{font-size:.88em;color:#596861}a{color:#8b482f;overflow-wrap:anywhere}table{border-collapse:collapse;width:100%;font-size:.88em}td,th{border-bottom:1px solid #bdc9ba;padding:.5em;text-align:left}th{background:#e9eee3}blockquote{border-left:.2em solid #ca6a48;padding-left:1em;margin-left:0}li{margin:.5em 0}'
def document(title,body,css='../style.css'):
 return '<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE html><html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="zh-CN"><head><title>'+html.escape(title)+'</title><link rel="stylesheet" type="text/css" href="'+css+'" /></head><body>'+body+'</body></html>'

def source_documents(book):
    docs=[]
    guide=ROOT/'appendices/00-reading-guide.md'
    if guide.exists(): docs.append(('guide','导读',guide))
    docs.extend(('ch'+c['id'],c['title'],ROOT/c['source']) for c in book['chapters'])
    for n,p in enumerate(sorted((ROOT/'appendices').glob('*.md'))):
        if p!=guide:
            title=p.read_text().splitlines()[0].lstrip('# ').strip()
            docs.append(('app'+str(n),title,p))
    return docs

def validate(book):
    issues=[];stats=[];images=set();chapter_ids=set()
    if len(book['chapters'])!=28:issues.append('章节清单应为28章')
    for c in book['chapters']:
        if c['id'] in chapter_ids:issues.append('重复章节ID '+c['id'])
        chapter_ids.add(c['id']);p=ROOT/c['source']
        if not p.is_file():issues.append('缺章 '+c['source']);continue
        t=p.read_text();chars=len(re.findall(r'[\u3400-\u9fff]',t));pics=re.findall(r'!\[[^\]]*\]\(([^)]+)\)',t)
        if chars<1500:issues.append(f'短章 {p.name}: {chars}汉字')
        if len(pics)<2:issues.append('少于两幅图 '+p.name)
        if 'https://' not in t:issues.append('缺来源 '+p.name)
        if re.search(r'\bTODO\b|待补图|此处插图|占位图',t):issues.append('存在占位 '+p.name)
        stats.append({'id':c['id'],'han_characters':chars,'image_placements':len(pics)})
    for ident,title,p in source_documents(book):
        if not p.exists():continue
        for ref in re.findall(r'!\[[^\]]*\]\(([^)]+)\)',p.read_text()):
            f=(p.parent/ref).resolve()
            if not f.is_relative_to(ROOT):issues.append(f'图片超出工程目录 {p.name}: {ref}')
            elif not f.is_file():issues.append(f'缺图 {p.name}: {ref}')
            else:images.add(f)
    result={'title':book['title'],'chapter_count':len(stats),'han_characters':sum(x['han_characters'] for x in stats),'unique_referenced_images':len(images),'image_placements':sum(x['image_placements'] for x in stats),'chapters':stats,'issues':issues}
    BUILD.mkdir(exist_ok=True)
    (BUILD/'validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    return result,images

def make_epub(book,images):
    from PIL import Image
    import hashlib
    blobs={};items=[];spine=[];navigation=[];path_map={};hash_map={}
    def add(path,data,kind,ident,properties=''):
        if path in blobs:raise ValueError('Duplicate resource '+path)
        blobs[path]=data.encode('utf-8') if isinstance(data,str) else data
        items.append({'id':ident,'href':path,'media-type':kind,**({'properties':properties} if properties else {})})
    add('style.css',CSS,'text/css','css')
    for image_path in sorted(images):
        im=Image.open(image_path).convert('RGB');im.thumbnail((1400,2000));buffer=io.BytesIO();im.save(buffer,'JPEG',quality=88,optimize=True)
        data=buffer.getvalue();digest=hashlib.sha256(data).hexdigest()
        if digest not in hash_map:
            dest='images/'+image_path.stem+'.jpg'
            if dest in blobs:dest='images/'+image_path.stem+'-'+digest[:8]+'.jpg'
            hash_map[digest]=dest;add(dest,data,'image/jpeg','img'+str(len(hash_map)))
        path_map[image_path.resolve()]=hash_map[digest]
    documents=source_documents(book)
    doc_map={p.resolve():'text/'+ident+'.xhtml' for ident,title,p in documents}
    for ident,title,p in documents:
        tree=ET.fromstring('<section>'+markdown(p.read_text())+'</section>')
        for e in tree.iter():
            for attr in ['src','href']:
                ref=e.get(attr)
                if not ref or re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:',ref) or ref.startswith('#'):continue
                local,sep,fragment=ref.partition('#');resolved=(p.parent/local).resolve()
                dest=path_map.get(resolved) or doc_map.get(resolved)
                if not dest:raise ValueError(f'Unresolved local reference in {p.name}: {ref}')
                e.set(attr,posixpath.relpath(dest,'text')+(sep+fragment if sep else ''))
        body=''.join(ET.tostring(child,encoding='unicode') for child in tree)
        add(doc_map[p.resolve()],document(title,body),'application/xhtml+xml',ident)
        spine.append(ident);navigation.append((title,doc_map[p.resolve()]))
    first=(ROOT/'assets/images/comic-01.png').resolve()
    cover_image=path_map.get(first,next(iter(path_map.values())))
    cover='<section class="cover"><h1>'+html.escape(book['title'])+'</h1><p>'+html.escape(book['subtitle'])+'</p><p>中文图解知识书 · 扩展阅读稿</p><img src="../'+cover_image+'" alt="厨房观察漫画" /><p>从现象出发，理解机制，再回到日常判断。</p></section>'
    add('text/cover.xhtml',document(book['title'],cover),'application/xhtml+xml','cover')
    spine.insert(0,'cover')
    nav='<nav epub:type="toc" id="toc"><h1>目录</h1><ol>'+''.join('<li><a href="'+href+'">'+html.escape(title)+'</a></li>' for title,href in navigation)+'</ol></nav>'
    add('nav.xhtml',document('目录',nav,'style.css'),'application/xhtml+xml','nav','nav')
    # Legacy NCX improves navigation on older EPUB readers.
    uid='urn:uuid:'+str(uuid.uuid5(uuid.NAMESPACE_URL,'kitchen-science-expanded-20261026'))
    ncx='<?xml version="1.0" encoding="UTF-8"?><ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1"><head><meta name="dtb:uid" content="'+uid+'" /></head><docTitle><text>'+html.escape(book['title'])+'</text></docTitle><navMap>'+''.join('<navPoint id="n'+str(i)+'" playOrder="'+str(i)+'"><navLabel><text>'+html.escape(t)+'</text></navLabel><content src="'+h+'" /></navPoint>' for i,(t,h) in enumerate(navigation,1))+'</navMap></ncx>'
    add('toc.ncx',ncx,'application/x-dtbncx+xml','ncx')
    ns='http://www.idpf.org/2007/opf';dc='http://purl.org/dc/elements/1.1/'
    ET.register_namespace('',ns);ET.register_namespace('dc',dc)
    opf=ET.Element('{'+ns+'}package',{'version':'3.0','unique-identifier':'book-id','{http://www.w3.org/XML/1998/namespace}lang':'zh-CN'})
    metadata=ET.SubElement(opf,'{'+ns+'}metadata')
    for tag,value,attr in [('identifier',uid,{'id':'book-id'}),('title',book['title'],{}),('language','zh-CN',{}),('creator','厨房科学图解编辑组',{})]:ET.SubElement(metadata,'{'+dc+'}'+tag,attr).text=value
    ET.SubElement(metadata,'{'+ns+'}meta',{'property':'dcterms:modified'}).text=datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    manifest=ET.SubElement(opf,'{'+ns+'}manifest')
    for item in items:ET.SubElement(manifest,'{'+ns+'}item',item)
    spine_node=ET.SubElement(opf,'{'+ns+'}spine',{'toc':'ncx'})
    for ident in spine:ET.SubElement(spine_node,'{'+ns+'}itemref',{'idref':ident})
    blobs['package.opf']=ET.tostring(opf,encoding='utf-8',xml_declaration=True)
    check_epub_resources(blobs,items,spine)
    target=BUILD/'Kitchen-Science-Expanded.epub'
    with zipfile.ZipFile(target,'w') as z:
        z.writestr('mimetype','application/epub+zip',compress_type=zipfile.ZIP_STORED)
        container='<?xml version="1.0"?><container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles><rootfile full-path="OEBPS/package.opf" media-type="application/oebps-package+xml" /></rootfiles></container>'
        ET.fromstring(container);z.writestr('META-INF/container.xml',container,compress_type=zipfile.ZIP_DEFLATED)
        for path,data in blobs.items():z.writestr('OEBPS/'+path,data,compress_type=zipfile.ZIP_DEFLATED)
    with zipfile.ZipFile(target) as z:
        if z.infolist()[0].filename!='mimetype' or z.infolist()[0].compress_type!=zipfile.ZIP_STORED:raise ValueError('Invalid EPUB mimetype ordering')
        if z.testzip() is not None:raise ValueError('Corrupt ZIP entry')
    return target

def check_epub_resources(blobs,items,spine):
    ids={x['id'] for x in items}
    if len(ids)!=len(items):raise ValueError('Duplicate manifest IDs')
    if not set(spine).issubset(ids):raise ValueError('Missing spine manifest entries')
    for path,data in blobs.items():
        if path.endswith(('.xml','.opf','.xhtml','.ncx')):tree=ET.fromstring(data)
        else:continue
        if not path.endswith(('.xhtml','.ncx')):continue
        for e in tree.iter():
            for attr in ['src','href']:
                ref=e.get(attr)
                if not ref or re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:',ref) or ref.startswith('#'):continue
                target=posixpath.normpath(posixpath.join(posixpath.dirname(path),ref.split('#')[0]))
                if target not in blobs:raise ValueError(f'Broken EPUB reference {path}: {ref}')

def main():
    import argparse
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check-only',action='store_true');args=parser.parse_args()
    book=json.loads((ROOT/'book.json').read_text());stats,images=validate(book)
    print(json.dumps({k:v for k,v in stats.items() if k!='chapters'},ensure_ascii=False,indent=2))
    if stats['issues']:return 1
    if not args.check_only:print(make_epub(book,images))
    return 0

if __name__=='__main__':raise SystemExit(main())
