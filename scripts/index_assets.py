from pathlib import Path
import hashlib,json,re
from PIL import Image
root=Path(__file__).resolve().parents[1]
book=json.loads((root/'book.json').read_text())
# Keep one canonical file when neighboring chapters share a comic.
for even in range(2,29,2):
 a=root/f'assets/images/comic-{even-1:02}.png';b=root/f'assets/images/comic-{even:02}.png'
 if b.exists() and a.exists() and a.read_bytes()==b.read_bytes():
  p=root/book['chapters'][even-1]['source'];p.write_text(p.read_text().replace(f'comic-{even:02}.png',f'comic-{even-1:02}.png'));b.unlink()
rows=[]
for p in sorted((root/'assets/images').glob('*.png')):
 im=Image.open(p);im.load();chap=[]
 for c in book['chapters']:
  if p.name in (root/c['source']).read_text():chap.append(c['id'])
 rows.append({'file':p.relative_to(root).as_posix(),'type':'AI漫画教学示意' if p.name.startswith('comic') else '原创机制概念图','chapters':chap,'dimensions':list(im.size),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(root/'editorial/image-index.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
lines=['# 全图索引（编辑审查，不进入阅读版）','','| 文件 | 类型 | 对应章节 | 尺寸 |','|---|---|---|---|']
lines += [f'| [{Path(r["file"]).name}](../{r["file"]}) | {r["type"]} | {", ".join(r["chapters"])} | {r["dimensions"][0]}×{r["dimensions"][1]} |' for r in rows]
(root/'editorial/image-index.md').write_text('\n'.join(lines)+'\n')
print(json.dumps({'unique_files':len(rows),'comics':sum(r['file'].split('/')[-1].startswith('comic') for r in rows),'diagrams':sum(r['file'].split('/')[-1].startswith('diagram') for r in rows)},ensure_ascii=False))
