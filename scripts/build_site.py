#!/usr/bin/env python3
"""Build the reading website independently from EPUB export (Python + Pillow only)."""
from pathlib import Path
import argparse,hashlib,html,json,posixpath,re,shutil,sys,urllib.parse
from html.parser import HTMLParser
from xml.etree import ElementTree as ET
from PIL import Image
from build_book import markdown
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'build/site'
REPO='https://github.com/YZYExp/Learn-Kitchen-Chemistry'
EPUB=None
DOWNLOAD_DATE=None
PARTS={1:('认识物质与能量','从水、盐糖与酸碱，走到火候和油脂。'),2:('结构形成质地','乳化、泡沫、淀粉与蛋白质，如何变成口感。'),3:('颜色与风味的来源','酶、微生物与感官，把变化连接到风味。'),4:('把理解带回日常','低温、保存、清洁与器具，一路走到餐桌。')}

def esc(v):return html.escape(str(v),quote=True)
def textof(e):return ''.join(e.itertext())
def href(doc):return BASE+doc['url']
def dialog():return '<dialog data-image-dialog aria-label="图片放大查看"><button class="close" type="button">关闭 ×</button><img alt="" /><p></p></dialog>'
def header():return f'<a class="skip" href="#main">跳到正文</a><header class="topbar"><a class="brand" href="{BASE}"><span class="brand-mark" aria-hidden="true">🍅</span>厨房里的科学冒险</a><nav class="navlinks" aria-label="主导航"><a href="{BASE}#contents">目录</a><a href="{BASE}#download">电子书</a><a class="repo-link" href="{REPO}">GitHub ↗</a><button data-theme-toggle type="button" aria-label="切换亮暗主题" aria-pressed="false">暗色</button></nav></header>'
def footer():return f'<footer class="footer"><p>厨房里的科学冒险 · 图解知识书<br />漫画是 AI 教学示意，机制图不代表真实尺度；资料来源随正文就近标注。</p><p><a href="{REPO}">分章原稿与图片 ↗</a><br />© 原创编写与图解 · 资料与字体遵循各自来源和许可</p></footer>'
def shell(title,content,description='',reader=False):
 return '<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8" /><meta name="viewport" content="width=device-width,initial-scale=1" /><meta name="theme-color" content="#fffaf0" /><title>'+esc(title)+' · 厨房里的科学冒险</title><meta name="description" content="'+esc(description or BOOK['subtitle'])+'" /><link rel="icon" href="data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22%3E%3Ctext y=%22.9em%22 font-size=%2290%22%3E🍅%3C/text%3E%3C/svg%3E" /><link rel="stylesheet" href="'+BASE+'assets/style.css" /><script defer src="'+BASE+'assets/app.js"></script></head><body data-base="'+BASE+'">'+header()+('<div class="progress" aria-hidden="true"></div>' if reader else '')+content+footer()+dialog()+'</body></html>'
def chapterlink(c,current=None):
 return '<a class="chapterlink" href="'+href(c)+'" data-search-title="'+esc(c['id']+' '+c['title'])+'"'+(' aria-current="page"' if current==c['key'] else '')+'><span class="num">'+c['id']+'</span><span>'+esc(c['title'])+'</span></a>'
def directory(current=None,sidebar=False):
 out=[]
 for n,(name,desc) in PARTS.items():
  chapters=[c for c in CHAPTERS if c['part']==n]
  if sidebar:out.append('<section data-directory-part><h3>第'+str(n)+'部分 · '+name+'</h3>'+''.join(chapterlink(c,current) for c in chapters)+'</section>')
  else:out.append('<section class="part" data-directory-part><span class="partno">PART 0'+str(n)+'</span><h3>'+name+'</h3>'+''.join(chapterlink(c) for c in chapters)+'</section>')
 return ''.join(out)
def search_input(suffix=''):
 return f'<label class="searchlabel" for="chapter-search{suffix}">按章节标题查找</label><input class="search" id="chapter-search{suffix}" type="search" data-directory-search placeholder="试试：乳化、面团、保存……" autocomplete="off" /><p class="empty" data-search-empty hidden>没有找到相应章节，请换一个关键词。</p><p class="empty" data-search-status aria-live="polite"></p>'

def process_document(doc):
 tree=ET.fromstring('<section>'+markdown(doc['path'].read_text())+'</section>')
 headings=[]
 for i,e in enumerate(tree.iter()):
  if e.tag in ['h2','h3']:
   e.set('id','section-'+str(i));headings.append((textof(e),e.get('id'),e.tag))
  for attr in ['href','src']:
   ref=e.get(attr)
   if not ref or re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:',ref) or ref.startswith('#'):continue
   local,sep,fragment=ref.partition('#');resolved=(doc['path'].parent/urllib.parse.unquote(local)).resolve()
   if resolved in IMAGES:
    image=IMAGES[resolved];e.set(attr,BASE+image['url']);e.set('width',str(image['width']));e.set('height',str(image['height']));e.set('loading','lazy');e.set('decoding','async');e.set('data-zoom-image','')
   elif resolved in DOCMAP:e.set(attr,href(DOCMAP[resolved])+(sep+fragment if sep else ''))
   else:raise ValueError(f'Unresolved source link {doc["path"].name}: {ref}')
  if e.tag=='a' and e.get('href','').startswith('https://'):e.set('rel','noopener noreferrer')
 # Pair image paragraphs with their adjacent caption; preserve the original wording.
 children=list(tree);new=[];i=0
 while i<len(children):
  e=children[i]
  if e.tag=='p' and len(e)==1 and e[0].tag=='img':
   figure=ET.Element('figure');figure.append(e[0])
   if i+1<len(children) and children[i+1].tag=='p' and len(children[i+1])==1 and children[i+1][0].tag=='em':
    caption=ET.SubElement(figure,'figcaption');caption.append(children[i+1][0]);i+=1
   new.append(figure)
  elif e.tag=='table':
   wrapper=ET.Element('div',{'class':'tablewrap'});wrapper.append(e);new.append(wrapper)
  else:new.append(e)
  i+=1
 body=''.join(ET.tostring(e,encoding='unicode',method='html') for e in new)
 return body,headings

def reader_page(doc,index):
 body,heads=process_document(doc)
 sidebar='<aside class="sidebar"><details open><summary>全书目录 <span aria-hidden="true">⌄</span></summary><div class="navcontent">'+search_input('-reader')+directory(doc['key'],True)+'<h3>导读与附录</h3>'+''.join('<a class="appendix" href="'+href(d)+'"'+(' aria-current="page"' if d['key']==doc['key'] else '')+'>'+esc(d['title'])+'</a>' for d in APPENDICES)+'</div></details></aside>'
 tools='<aside class="reading-tools" aria-label="阅读工具"><div class="toolbox"><p>正文字号</p><div class="fontbuttons"><button type="button" data-font-change="-1" aria-label="减小字号">A−</button><span data-font-label>18px</span><button type="button" data-font-change="1" aria-label="增大字号">A+</button></div></div><details class="toc" open><summary>本页内容</summary>'+''.join('<a href="#'+anchor+'">'+esc(name)+'</a>' for name,anchor,tag in heads if tag=='h2')+'</details></aside>'
 previous=DOCS[index-1] if index>0 else None;following=DOCS[index+1] if index+1<len(DOCS) else None
 turns='<nav class="pageturn" aria-label="章节翻页">'+('<a href="'+href(previous)+'"><small>← 上一篇</small>'+esc(previous['title'])+'</a>' if previous else '<span></span>')+('<a href="'+href(following)+'"><small>下一篇 →</small>'+esc(following['title'])+'</a>' if following else '<a href="'+BASE+'#contents"><small>全书读完了</small>返回目录 →</a>')+'</nav>'
 meta=(('第 '+doc['id']+' 章 / 共 28 章') if 'id' in doc else '导读与附录')
 article='<main class="article" id="main"><div class="reader-meta"><span>'+meta+'</span><span>图解阅读 · 化学 / 生物 / 物理</span></div><div class="resume-note" data-resume-note hidden><span>这篇已有阅读记录</span><button type="button">回到上次位置</button></div><article class="reader">'+body+'</article>'+turns+'<a class="toplink" href="#main">回到本篇开头 ↑</a></main>'
 return shell(doc['title'],'<div class="reading-shell">'+sidebar+article+tools+'</div>',reader=True)

def homepage():
 hero=IMAGES[(ROOT/'assets/images/comic-01.png').resolve()]
 art=f'<div class="hero-art"><img src="{BASE}{hero["thumb"]}" width="{hero["thumb_width"]}" height="{hero["thumb_height"]}" alt="小番茄观察溶解、沸腾和苹果切面的漫画" fetchpriority="high" /><span class="sticker">今天，从一锅水开始。</span></div>'
 content='<main id="main" class="wrap"><section class="hero"><div><p class="eyebrow">一本可以带回厨房的科学书</p><h1>厨房里的<span>科学冒险</span></h1><p class="subtitle">'+esc(BOOK['subtitle'])+'</p><p class="lede">面团为什么留得住空气？酱汁为何刚打匀又分层？从看得见的变化出发，跟着小番茄走进食物内部，把日常经验变成有根据的理解。</p><div class="actions"><a class="button primary" href="'+href(CHAPTERS[0])+'">开始阅读 <span aria-hidden="true">→</span></a><a class="button" href="#contents">浏览全书目录</a></div><a class="button" data-resume-link hidden href="'+BASE+'">继续阅读</a><div class="statline"><div><strong>28</strong><small>循序展开的章节</small></div><div><strong>42</strong><small>漫画与原理图</small></div><div><strong>5.5万</strong><small>汉字与图注</small></div></div></div>'+art+'</section>'
 content+='<section class="section" id="contents"><div class="section-heading"><div><p class="eyebrow">从观察，到理解，再到应用</p><h2>四部分，走完一顿饭的科学</h2></div><p>既可以从第一章慢慢读，也可以带着一个厨房问题查找。每章独立成页，图片按需加载。</p></div>'+search_input()+'<div class="directory">'+directory()+'</div></section>'
 samples=[('comic-07.png','油与水的临时联盟','从分层到乳化，辨认液滴与界面的作用。','emulsion'),('comic-11.png','柔软食物里的骨架','鸡蛋、豆腐与面团，怎样形成不同结构。','protein'),('comic-17.png','看不见的厨房帮手','酶与微生物，参与变化的方式并不相同。','enzymes')]
 content+='<section class="section"><div class="section-heading"><div><p class="eyebrow">漫画看现象，图解读机制</p><h2>给好奇心留一张图的位置</h2></div><p>14 幅趣味漫画与 28 幅中文原理图，穿插在相关知识处。拟人角色帮助叙事，事实解释和资料来源紧随正文。</p></div><div class="gallery">'
 for name,title,desc,slug in samples:
  pic=IMAGES[(ROOT/'assets/images'/name).resolve()];c=next(c for c in CHAPTERS if c['slug']==slug)
  content+=f'<figure><img src="{BASE}{pic["thumb"]}" data-full="{BASE}{pic["url"]}" width="{pic["thumb_width"]}" height="{pic["thumb_height"]}" alt="{esc(title)}的AI教学漫画" loading="lazy" decoding="async" data-zoom-image /><figcaption><strong><a href="{href(c)}">{esc(title)} ↗</a></strong>{esc(desc)}</figcaption></figure>'
 content+='</div></section><section class="section"><div class="section-heading"><div><p class="eyebrow">把知识变成自己的观察</p><h2>导读与随手查</h2></div><p>观察记录、常用术语和现象索引，帮助你从一个具体问题回到相应解释。</p></div><div class="appendices">'+''.join('<a class="button" href="'+href(d)+'">'+esc(d['title'])+' →</a>' for d in APPENDICES)+'</div></section>'
 edition_text=('现有公共阅读版：'+esc(DOWNLOAD_DATE)+' 扩展版。' if EPUB else '公共阅读包暂未提供，可前往仓库下载最新导出产物。')
 download_button=('<a class="button primary" href="'+esc(EPUB)+'" download>下载 EPUB ↓</a>' if EPUB else '')
 content+='<section class="section" id="download"><div class="download"><div><h2>把整本书带走</h2><p>EPUB 适合手机和平板离线阅读。'+edition_text+'<br />最新导出保存在仓库独立的 EPUB 构建产物中，不影响网页发布。</p></div><div class="actions">'+download_button+'<a class="button" href="'+REPO+'/actions/workflows/epub.yml">查看最新导出 ↗</a></div></div></section></main>'
 return shell('在线阅读',content)

class Links(HTMLParser):
 def __init__(self):super().__init__();self.refs=[];self.ids=set()
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if 'id' in a:self.ids.add(a['id'])
  for key in ['href','src']:
   if a.get(key):self.refs.append(a[key])
def check_links():
 parsed={}
 for p in OUT.rglob('*.html'):
  parser=Links();parser.feed(p.read_text());parsed[p.resolve()]=parser
 errors=[]
 for p,parser in parsed.items():
  for ref in parser.refs:
   u=urllib.parse.urlsplit(ref)
   if u.scheme or u.netloc:continue
   if u.path.startswith('/'):
    if not u.path.startswith(BASE):errors.append(f'{p.relative_to(OUT)}: wrong base {ref}');continue
    target=OUT/urllib.parse.unquote(u.path[len(BASE):])
   else:target=p.parent/urllib.parse.unquote(u.path)
   if target.is_dir():target=target/'index.html'
   target=target.resolve()
   if not target.is_file():errors.append(f'{p.relative_to(OUT)}: missing {ref}');continue
   if u.fragment and target in parsed and urllib.parse.unquote(u.fragment) not in parsed[target].ids:errors.append(f'{p.relative_to(OUT)}: missing anchor {ref}')
 if errors:raise ValueError('\n'.join(errors))
 return len(parsed)

def main():
 global BASE,BOOK,CHAPTERS,APPENDICES,DOCS,DOCMAP,IMAGES,EPUB,DOWNLOAD_DATE
 ap=argparse.ArgumentParser();ap.add_argument('--base-path',default='/');args=ap.parse_args()
 BASE='/'+args.base_path.strip('/')+'/' if args.base_path.strip('/') else '/'
 if '..' in BASE or '?' in BASE or '#' in BASE:raise ValueError('Invalid base path')
 BOOK=json.loads((ROOT/'book.json').read_text());CHAPTERS=[]
 for c in BOOK['chapters']:
  CHAPTERS.append({**c,'key':'ch'+c['id'],'path':(ROOT/c['source']).resolve(),'url':'chapters/'+c['slug']+'/'})
 APPENDICES=[]
 for p in sorted((ROOT/'appendices').glob('*.md')):
  APPENDICES.append({'key':p.stem,'path':p.resolve(),'title':p.read_text().splitlines()[0].lstrip('# ').strip(),'url':'appendices/'+p.stem+'/'})
 guide=next(d for d in APPENDICES if d['key'].startswith('00-'))
 DOCS=[guide]+CHAPTERS+[d for d in APPENDICES if d!=guide];DOCMAP={d['path']:d for d in DOCS};IMAGES={}
 if len({d['url'] for d in DOCS})!=len(DOCS):raise ValueError('Duplicate document URL')
 if len({d['path'] for d in DOCS})!=len(DOCS):raise ValueError('Duplicate document source')
 if OUT.exists():shutil.rmtree(OUT)
 (OUT/'assets/images').mkdir(parents=True)
 edition_file=ROOT/'downloads/reading-edition.json'
 if edition_file.exists():
  metadata=json.loads(edition_file.read_text())
  filename=metadata.get('file','Kitchen-Science-Expanded.epub')
  if Path(filename).name!=filename:raise ValueError('Invalid reading edition filename')
  package=ROOT/'downloads'/filename
  if package.is_file():
   actual=hashlib.sha256(package.read_bytes()).hexdigest()
   if actual!=metadata.get('sha256'):raise ValueError('Reading edition SHA256 mismatch')
   if not metadata.get('edition_date'):raise ValueError('Reading edition date missing')
   (OUT/'downloads').mkdir();shutil.copy2(package,OUT/'downloads'/filename);shutil.copy2(edition_file,OUT/'downloads/reading-edition.json')
   EPUB=BASE+'downloads/'+filename;DOWNLOAD_DATE=metadata['edition_date']
 for d in DOCS:
  for ref in re.findall(r'!\[[^\]]*\]\(([^)]+)\)',d['path'].read_text()):
   p=(d['path'].parent/ref).resolve()
   if not p.is_file():raise ValueError(f'Missing image {p}')
   if p in IMAGES:continue
   im=Image.open(p).convert('RGB');im.thumbnail((1400,2000));dest='assets/images/'+p.stem+'.jpg';im.save(OUT/dest,quality=87,optimize=True)
   IMAGES[p]={'url':dest,'width':im.width,'height':im.height}
 for name in ['comic-01.png','comic-07.png','comic-11.png','comic-17.png']:
  p=(ROOT/'assets/images'/name).resolve();im=Image.open(p).convert('RGB');im.thumbnail((560,900));dest='assets/images/'+p.stem+'-thumb.jpg';im.save(OUT/dest,quality=85,optimize=True)
  IMAGES[p].update({'thumb':dest,'thumb_width':im.width,'thumb_height':im.height})
 for name in ['style.css','app.js']:shutil.copy2(ROOT/'site'/name,OUT/'assets'/name)
 (OUT/'index.html').write_text(homepage())
 for index,doc in enumerate(DOCS):
  folder=OUT/doc['url'];folder.mkdir(parents=True,exist_ok=True);(folder/'index.html').write_text(reader_page(doc,index))
 (OUT/'404.html').write_text(shell('页面未找到','<main id="main" class="wrap section"><h1>这条厨房小路暂时走不通。</h1><p>请从目录寻找想读的章节。</p><a class="button primary" href="'+BASE+'#contents">返回全书目录 →</a></main>'))
 (OUT/'.nojekyll').touch()
 (OUT/'chapters.json').write_text(json.dumps([{'id':c['id'],'title':c['title'],'url':href(c)} for c in CHAPTERS],ensure_ascii=False))
 count=check_links();report={'base_path':BASE,'html_pages':count,'chapters':len(CHAPTERS),'appendices':len(APPENDICES),'unique_images':len(IMAGES),'thumbnails':4,'local_links':'passed','output_bytes':sum(p.stat().st_size for p in OUT.rglob('*') if p.is_file()),'epub_required':False,'public_download':bool(EPUB),'download_edition':DOWNLOAD_DATE}
 (ROOT/'build/site-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
