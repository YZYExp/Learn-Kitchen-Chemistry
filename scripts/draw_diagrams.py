#!/usr/bin/env python3
"""Reproducible original kitchen-science concept figures; no quantitative claims."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import math, random, json
ROOT=Path(__file__).resolve().parents[1]
FONT=ROOT/'assets/fonts/NotoSansSC-Regular.ttf'
W,H=1200,1450
BG='#faf6eb'; INK='#244c42'; RED='#b44b38'; GOLD='#d4a441'; BLUE='#78a9b1'; PALE='#dbe8df'; WATER='#d9eaf0'; GRAY='#69756d'; WHITE='#fffdf8'
F=lambda n: ImageFont.truetype(str(FONT),n)
random.seed(42)

def txt(x,y,s,size=34,color=INK,anchor=None):
    d.text((x,y),s,font=F(size),fill=color,anchor=anchor)
def wrap(x,y,s,width=1050,size=34,color=INK,leading=1.6):
    line=''; yy=y
    for c in s:
        if c=='\n' or d.textlength(line+c,font=F(size))>width:
            txt(x,yy,line,size,color);yy+=size*leading;line='' if c=='\n' else c
        else:line+=c
    if line:txt(x,yy,line,size,color)
    return yy+size*leading

def arrow(a,b,color=RED,width=7):
    d.line([a,b],fill=color,width=width)
    dx,dy=b[0]-a[0],b[1]-a[1];a0=math.atan2(dy,dx);l=20
    pts=[b,(b[0]-l*math.cos(a0-.5),b[1]-l*math.sin(a0-.5)),(b[0]-l*math.cos(a0+.5),b[1]-l*math.sin(a0+.5))]
    d.polygon(pts,fill=color)
def circ(x,y,r,fill=GOLD,outline=INK,width=4):
    d.ellipse((x-r,y-r,x+r,y+r),fill=fill,outline=outline,width=width)
def panel(y,title,note=None):
    d.line((65,y-18,1135,y-18),fill='#cbd7c9',width=3)
    txt(70,y,title,38)
    if note:wrap(70,y+57,note,size=31,color=GRAY)
def label(x,y,s,size=32,color=INK): txt(x,y,s,size,color,anchor='mm')
def cup(x,y,w=240,h=240,level=.7,color=WATER,oil=False):
    d.rectangle((x+5,y+h*(1-level),x+w-5,y+h-5),fill=color)
    if oil:d.rectangle((x+5,y+h*(1-level),x+w-5,y+h*(1-level)+65),fill='#f1d581')
    d.line([(x,y),(x,y+h),(x+w,y+h),(x+w,y)],fill=INK,width=6)
    return x,y,w,h

def dots(x,y,w,h,n=16,color=GOLD,r=10):
    for _ in range(n): circ(x+random.randrange(int(w)),y+random.randrange(int(h)),r,color,outline=None)
def chain(points,color=RED,width=8):
    d.line(points,fill=color,width=width,joint='curve')
    for x,y in points: circ(x,y,5,color,outline=None)
def wave(x,y,w=240,h=25,n=24,color=RED):
    pts=[(x+i*w/n,y+h*math.sin(i*math.pi*4/n)) for i in range(n+1)]
    chain(pts,color,6)
def net(x,y,w=340,h=220,step=65,color=INK):
    for i in range(0,w+1,step):
        pts=[(x+i+15*math.sin(k),y+k*h/6) for k in range(7)];chain(pts,color,5)
    for j in range(0,h+1,step):
        pts=[(x+k*w/7,y+j+12*math.sin(k)) for k in range(8)];chain(pts,color,5)
def plate(x,y,r=115,color='#dfb77f'):
    d.ellipse((x-r-22,y-r*.4-20,x+r+22,y+r*.4+20),fill=WHITE,outline=INK,width=4)
    d.ellipse((x-r,y-r*.4,x+r,y+r*.4),fill=color,outline=INK,width=3)
def cell(x,y,w=280,h=220,damaged=False):
    d.rounded_rectangle((x,y,x+w,y+h),radius=35,outline=INK,width=7,fill=PALE)
    d.rounded_rectangle((x+18,y+18,x+w-18,y+h-18),radius=30,outline=BLUE,width=4,fill=WATER)
    d.ellipse((x+50,y+50,x+w-55,y+h-35),fill='#b7d0d1',outline=BLUE,width=3)
    circ(x+w-45,y+45,16,GOLD)
    if damaged:d.line((x+w-25,y+50,x+w+25,y+85,x+w-25,y+120,x+w+25,y+150),fill=RED,width=8)
def jar(x,y,w=180,h=220,color=PALE):
    d.rounded_rectangle((x,y,x+w,y+h),radius=20,fill=color,outline=INK,width=5)
    d.rectangle((x-5,y-20,x+w+5,y+10),fill=GOLD,outline=INK,width=4)
def bug(x,y,color=RED):
    d.rounded_rectangle((x-30,y-15,x+30,y+15),radius=15,fill=color,outline=INK,width=3)
    for dy in [-20,20]:
        for dx in [-20,0,20]:d.line((x+dx,y+dy*.65,x+dx+5,y+dy),fill=color,width=3)
def yeast(x,y,color=GOLD):
    d.ellipse((x-25,y-34,x+25,y+34),fill=color,outline=INK,width=3)
    d.ellipse((x+10,y-43,x+35,y-15),fill=color,outline=INK,width=3)

def snow(x,y,r=35):
    for a in [0,math.pi/3,2*math.pi/3]:
        d.line((x-r*math.cos(a),y-r*math.sin(a),x+r*math.cos(a),y+r*math.sin(a)),fill=BLUE,width=6)
def thermometer(x,y,labeltext):
    d.rounded_rectangle((x-13,y-85,x+13,y+40),radius=13,outline=INK,width=4,fill=WHITE)
    d.line((x,y-40,x,y+50),fill=RED,width=7);circ(x,y+60,25,RED)
    label(x,y+110,labeltext)
def gear(x,y,r=58):
    for a in range(0,360,30):
        xx=x+math.cos(math.radians(a))*r; yy=y+math.sin(math.radians(a))*r
        d.line((x,y,xx,yy),fill=INK,width=23)
    circ(x,y,r*.75,PALE);circ(x,y,r*.25,BG)
def food(x,y,w=280,h=150):d.rounded_rectangle((x,y,x+w,y+h),radius=28,fill='#e8bd82',outline=INK,width=5)
def heading(n,title):
    txt(65,45,f'厨房科学 · 原理图 {n:02}',30,RED)
    wrap(65,100,title,size=47,width=1080,leading=1.25)
    txt(65,1380,'原创概念图｜非真实尺度；不用于推算数值或食安结论',30,GRAY)

TITLES=[
'比较条件，才能解释变化','水的状态改变，不等于糖的溶解','浓度与水活度，是两个问题','当前酸碱状态，不等于酸的总量','热先经过表面，再进入中心','压力改变沸点，蒸汽也会传热','油脂的排列与氧化','乳化：分散液滴，保护界面','泡沫：气泡之间还有液体','淀粉：加热膨胀，冷却重排','蛋白质：主链保留，折叠改变','面团：产气、留气、定型','凝胶：网络限制水的流动','结晶大小与排列，改变口感','三种褐变，不是同一条反应','蔬果：组织与色素同时变化','酶与底物接触，反应才有机会','发酵：不同微生物，不同产物','风味由多种感觉共同组成','萃取：从内部到水中','香辛料：香气和刺激分开看','冻结改变水的分布','保存依靠多种条件共同控制','污染沿接触路径转移','去油与除垢，面对不同对象','加热方式与锅具材料配合','配料顺序，不等于健康排名','一顿饭，是多种机制的合作']

for n,title in enumerate(TITLES,1):
    im=Image.new('RGB',(W,H),BG);d=ImageDraw.Draw(im);heading(n,title)
    if n==1:
        panel(215,'只改变一个条件','同一批糖、相同水量与温度；这一轮只比较是否搅拌。')
        for x,cap in [(180,'不搅拌'),(720,'搅拌')]:
            cup(x,360);dots(x+25,540,190,40,24);label(x+120,665,cap)
        d.arc((780,395,900,515),40,330,fill=RED,width=7);arrow((900,450),(895,420))
        panel(795,'记录之后，再检验解释','画下剩余颗粒、记录用时；换一批样品重复比较。')
        for i,(cap,col) in enumerate([('条件',GOLD),('现象',BLUE),('解释',RED)]):
            x=235+i*360;circ(x,1060,83,PALE,outline=col);label(x,1060,cap,35)
            if i<2:arrow((x+100,1060),(x+255,1060))
        wrap(110,1215,'结果不符合预测，也要保留记录。',size=34)
    elif n==2:
        panel(215,'同一种水，可以有不同状态')
        for i,cap in enumerate(['冰','液态水','水蒸气']):
            x=230+370*i;label(x,650,cap)
            if i==0:
                for a in range(4):
                    for b in range(4):circ(x-75+a*50,400+b*50,15,BLUE)
            elif i==1:dots(x-100,390,200,190,26,BLUE,13)
            else:
                for dx,dy in [(-90,390),(50,440),(-30,550),(90,600)]:circ(x+dx,dy,14,BLUE)
            if i<2:arrow((x+125,490),(x+235,490));arrow((x+235,540),(x+125,540),BLUE)
        panel(790,'糖进入水：形成混合物','糖仍以溶质形式存在；没有因此变成另一种水。')
        cup(190,970);dots(210,1040,200,150,16,GOLD,11);dots(210,1040,200,150,25,BLUE,8)
        arrow((500,1100),(680,1100));txt(730,1040,'溶解',40);wrap(730,1105,'不是融化\n不是水的相变',width=350,size=34)
    elif n==3:
        panel(215,'相同溶质，分配进不同水量')
        cup(180,370,240,250,.8);cup(730,370,240,250,.4)
        for x,top in [(180,430),(730,530)]:dots(x+20,top,200,70,12,GOLD,10)
        label(300,680,'较稀');label(850,680,'较浓');label(580,340,'两杯溶质总量相同',34,RED)
        panel(815,'含水率与水活度不能互换','含水率问“有多少水”；水活度描述水的热力学状态。')
        jar(190,1020,240,170,WATER);jar(730,1020,240,170,WATER)
        dots(210,1040,190,125,6,GOLD);dots(750,1040,190,125,24,GOLD)
        label(310,1240,'配方不同');label(850,1240,'水的状态也可不同')
    elif n==4:
        panel(215,'当前状态：测量水溶液的酸碱程度')
        d.line((160,480,1040,480),fill=INK,width=6)
        for i,(cap,col) in enumerate([('偏酸',RED),('近中性',GOLD),('偏碱',BLUE)]):
            x=240+360*i;circ(x,480,35,col);label(x,565,cap)
        wrap(120,660,'pH不是把所有酸性成分逐个加起来。',size=34)
        panel(815,'酸的储备：规定方法下的可滴定酸','同样的起始pH，不保证中和至规定终点所需的碱量相同。')
        for x,count in [(190,7),(740,19)]:
            cup(x,1020,230,180,.8);dots(x+20,1070,190,100,count,RED,9)
            d.line((x+100,950,x+100,1010),fill=INK,width=8);circ(x+100,1000,12,BLUE)
        label(570,1255,'点数仅示意储备差异，不是酸度数值',32)
    elif n==5:
        panel(215,'热量沿温度差传递','图示是食物受热早期的截面；中心不与表面瞬间同温。')
        d.rectangle((140,650,1060,700),fill=GRAY);food(260,380,680,260)
        for x in [360,600,840]:arrow((x,740),(x,570));arrow((x,570),(x,470),GOLD)
        label(600,795,'锅具 → 食物表面 → 食物内部',36)
        for x in [350,850]:wave(x-40,345,80,8,16,BLUE);arrow((x,375),(x,320),BLUE)
        label(1000,350,'蒸发',32,BLUE)
        panel(940,'厚度、时间与水分共同影响结果')
        food(180,1080,300,65);food(730,1030,300,165)
        arrow((330,1230),(330,1160));arrow((880,1230),(880,1130))
        label(330,1295,'薄片');label(880,1295,'厚块')
    elif n==6:
        panel(215,'外部压力提高，水的沸点随之提高')
        for x,cap,closed in [(170,'普通锅',False),(740,'压力锅',True)]:
            cup(x,400,280,230,.6);d.rectangle((x-20,380,x+300,405),fill=GRAY,outline=INK,width=4)
            if closed:d.rectangle((x+105,340,x+175,380),fill=INK)
            else:wave(x+85,320,110,10,16,BLUE)
            label(x+140,690,cap)
        wrap(160,770,'普通锅盖不等于密闭压力容器。',size=34)
        panel(930,'蒸汽遇较冷表面凝结，也能传递能量')
        food(520,1030,220,180)
        for x,y in [(250,1090),(290,1180),(920,1090)]:circ(x,y,18,BLUE)
        arrow((320,1100),(510,1100),BLUE);arrow((900,1100),(755,1100),BLUE)
        label(630,1260,'凝结与传热',35)
    elif n==7:
        panel(215,'脂肪链的排列，会影响熔融行为','图中线条只代表排列差别，不是完整化学结构。')
        for y in [390,440,490,540]:chain([(170,y),(430,y)],INK,10)
        for i,y in enumerate([390,445,500,555]):chain([(740,y),(820,y),(850,y+30),(980,y+30)],RED,10)
        label(300,650,'较容易紧密排列');label(865,650,'弯折使排列受扰')
        panel(820,'氧化还受环境与时间影响')
        jar(460,1010,280,180,GOLD)
        for x,y,cap in [(210,1000,'氧气'),(940,1000,'光'),(600,1230,'热与时间')]:
            label(x,y,cap,35,RED)
        arrow((280,1030),(450,1090));arrow((870,1030),(750,1090));arrow((600,1200),(600,1160))
    elif n==8:
        panel(215,'水相连续，油滴分散在其中')
        cup(110,370,400,290,.9);cup(690,370,400,290,.9)
        for x,y,r in [(210,460,43),(370,550,60),(290,600,32)]:circ(x,y,r,GOLD)
        for x,y,r in [(790,460,43),(950,550,60),(870,600,32)]:
            circ(x,y,r,GOLD)
            for a in range(0,360,30):circ(x+(r+8)*math.cos(math.radians(a)),y+(r+8)*math.sin(math.radians(a)),6,RED,outline=None)
        label(310,720,'新生油滴');label(890,720,'界面成分帮助稳定')
        panel(865,'上浮与合并，是两种不同变化')
        circ(250,1110,42,GOLD);arrow((250,1050),(250,980),BLUE);label(250,1230,'上浮：位置改变')
        circ(720,1070,32,GOLD);circ(800,1120,32,GOLD);arrow((850,1100),(920,1100));circ(1000,1100,52,GOLD);label(850,1230,'合并：液滴变大')
    elif n==9:
        panel(215,'气泡表面与气泡之间，都有液膜')
        for x,y,r in [(250,460,100),(460,480,100),(350,650,100),(570,660,90),(720,470,110),(900,630,100)]:
            circ(x,y,r,WHITE,BLUE,9)
        arrow((460,550),(460,780),BLUE);label(900,820,'液体向下排出',34,BLUE)
        panel(950,'薄膜破裂可合并；气体迁移也会改变泡径')
        circ(240,1130,60,WHITE,BLUE);circ(370,1130,60,WHITE,BLUE);arrow((470,1130),(650,1130));circ(790,1130,100,WHITE,BLUE)
        label(330,1265,'相邻小泡');label(790,1265,'较大的气泡')
    elif n==10:
        panel(215,'加热并有足够水：颗粒吸水膨胀与结构改变')
        for x,y in [(220,440),(360,530),(240,600)]:circ(x,y,35,PALE)
        arrow((460,510),(650,510));circ(820,510,120,PALE);wave(720,480,200,20,30,INK);wave(720,550,210,17,30,INK);wave(740,660,280,14,30,INK)
        label(290,720,'未糊化颗粒');label(820,720,'膨胀与链段进入水相')
        panel(865,'冷却储存：部分链段重新靠近')
        for y in [1070,1125,1180]:wave(200,y,280,15,20,RED)
        arrow((560,1130),(690,1130))
        for y in [1090,1120,1150]:chain([(770,y),(1020,y)],INK,7)
        label(350,1270,'分散链段');label(890,1270,'重新排列：回生')
    elif n==11:
        panel(215,'变性：折叠结构改变，主链仍连续')
        pts=[(300+100*math.cos(t)*math.sin(t*.7),500+100*math.sin(t)) for t in [i*.2 for i in range(70)]];chain(pts,RED,7)
        arrow((470,500),(650,500));wave(720,500,300,65,50,RED)
        label(300,720,'折叠');label(870,720,'展开：不是切成小段')
        panel(865,'多条链彼此联系，可形成凝胶网络')
        net(220,1030,750,220,95,RED);dots(240,1050,710,170,28,BLUE,8)
        label(600,1290,'网络限制流动，水分留在其中',35)
    elif n==12:
        panel(215,'产气和留气，是两个合作任务')
        for x,y in [(200,440),(270,550),(350,430)]:yeast(x,y,GOLD)
        for x,y in [(420,450),(480,530),(570,440)]:circ(x,y,15,WHITE,BLUE)
        arrow((390,560),(570,560),BLUE);net(700,380,320,260,75)
        for x,y in [(780,450),(940,560),(840,580)]:circ(x,y,32,WHITE,BLUE)
        label(300,720,'酵母代谢产生气体');label(870,720,'面筋等结构帮助留气')
        panel(875,'加热中：气体膨胀，淀粉与蛋白质参与定型')
        food(260,1040,680,190)
        for x,y,r in [(350,1130,27),(450,1090,35),(570,1160,42),(700,1100,44),(840,1160,28)]:circ(x,y,r,BG)
        label(600,1300,'多孔组织的形成，不只靠酵母',35)
    elif n==13:
        panel(215,'水多，也可以形成能保持形状的凝胶')
        dots(160,390,310,230,32,BLUE,9);arrow((520,510),(680,510));net(750,370,290,250,75,RED);dots(770,390,250,200,25,BLUE,8)
        label(320,720,'可以流动的分散体系');label(890,720,'连续网络限制流动')
        panel(865,'不同胶体，成胶条件不同')
        for x,cap in [(230,'吉利丁'),(600,'琼脂'),(970,'果胶')]:
            d.rounded_rectangle((x-90,1040,x+90,1190),radius=25,fill=PALE,outline=INK,width=5);wave(x-70,1110,140,15,25,RED);label(x,1250,cap)
        wrap(100,1305,'温度、酸度、糖和离子条件不能直接互换。',size=30)
    elif n==14:
        panel(215,'晶体大小与排列，都能影响质地','示意比较结晶状态；不提供通用于所有配方的调温曲线。')
        for x,large in [(140,False),(700,True)]:
            d.rectangle((x,390,x+340,650),fill='#d9c5ab',outline=INK,width=4)
            if not large:
                for i in range(5):
                    for j in range(4):d.polygon([(x+30+i*60,410+j*55),(x+10+i*60,440+j*55),(x+50+i*60,440+j*55)],fill=WHITE,outline=INK)
            else:
                for dx,dy in [(80,80),(240,165)]:d.polygon([(x+dx,390+dy-60),(x+dx-60,390+dy+45),(x+dx+65,390+dy+45)],fill=WHITE,outline=INK)
        label(310,730,'较细小');label(870,730,'较粗大')
        panel(900,'巧克力、黄油、冰淇淋：结晶对象并不相同')
        for x,cap,col in [(230,'可可脂', '#79533c'),(600,'乳脂',GOLD),(970,'冰与脂肪',PALE)]:
            circ(x,1120,80,col);label(x,1250,cap)
    elif n==15:
        for y,cap,react,out in [(245,'美拉德反应','还原糖 ＋ 氨基成分','烤香与褐色产物'),(610,'焦糖化','糖的受热变化','多种颜色与风味物质'),(975,'酶促褐变','酚类 ＋ 氧 ＋ 酶','切面逐渐褐变')]:
            panel(y,cap);circ(190,y+145,45,GOLD);circ(310,y+145,45,PALE);arrow((390,y+145),(590,y+145));plate(840,y+145,110,'#ae744e');txt(120,y+225,react,32);txt(670,y+225,out,32)
    elif n==16:
        panel(215,'组织层面：细胞壁、膜与细胞间连接')
        cell(150,390,320,240);cell(710,390,320,240,True);arrow((520,510),(650,510));label(310,720,'结构相对完整');label(870,720,'加热等处理改变结构')
        panel(870,'色素层面：不同色素，对环境响应不同')
        for x,col,cap in [(230,'#4a8a57','叶绿素'),(600,'#8a5480','花青素'),(970,'#d59540','类胡萝卜素')]:
            circ(x,1090,72,col,outline=None);label(x,1210,cap)
        wrap(100,1300,'看到颜色变了，还要辨认色素、酸碱和溶出。',size=30)
    elif n==17:
        panel(215,'完整组织中，部分酶与底物原本分隔')
        cell(150,390,320,240);gear(250,500,45);circ(390,530,25,GOLD)
        for yy in range(420,610,35):d.line((330,yy,330,yy+20),fill=BLUE,width=6)
        cell(710,390,320,240,True);gear(810,500,45);circ(880,520,25,GOLD);arrow((520,510),(650,510));label(310,720,'分隔');label(870,720,'切开后接触机会增加')
        panel(875,'酶促水解与蛋白质变性，不是同一件事')
        wave(150,1100,300,35,32,RED);arrow((520,1100),(650,1100));wave(740,1070,125,25,16,RED);wave(910,1140,125,25,16,RED)
        label(310,1245,'连续长链');label(890,1245,'特定酶作用：切成较短链')
    elif n==18:
        for y,cap,prod,col in [(245,'酵母','糖 → 二氧化碳、乙醇等',GOLD),(610,'乳酸菌','糖 → 乳酸等',RED),(975,'醋酸菌','乙醇 ＋ 氧 → 醋酸等',BLUE)]:
            panel(y,cap)
            for x,dy in [(170,100),(260,150),(190,210)]:
                if cap=='酵母':yeast(x,y+dy,col)
                else:d.rounded_rectangle((x-30,y+dy-15,x+30,y+dy+15),radius=15,fill=col,outline=INK,width=3)
            arrow((370,y+150),(560,y+150),col)
            for x,dy in [(650,120),(770,180),(900,100)]:circ(x,y+dy,24,col)
            txt(570,y+245,prod,32)
    elif n==19:
        panel(215,'口腔与鼻腔，共同参与风味')
        d.arc((360,360,900,830),90,270,fill=INK,width=9)
        d.line([(630,360),(740,440),(700,510),(780,560),(700,600),(730,650),(650,690)],fill=INK,width=8)
        d.ellipse((440,600,650,650),fill=RED,outline=INK,width=4);label(270,620,'味觉',35);arrow((320,620),(425,620))
        arrow((510,570),(580,440),GOLD);label(290,400,'鼻后嗅觉',35,GOLD);label(930,550,'气味',35,GOLD)
        panel(945,'还有温度、质地与化学刺激')
        for x,cap,col in [(230,'味觉',RED),(600,'嗅觉',GOLD),(970,'口腔感觉',BLUE)]:circ(x,1120,70,PALE,col);label(x,1240,cap)
        wrap(125,1310,'风味不是味蕾地图，也不只是舌头的任务。',size=30)
    elif n==20:
        panel(215,'先润湿，再从食材内部向水相转移')
        d.rounded_rectangle((160,365,460,650),radius=35,fill='#a57c55',outline=INK,width=5)
        dots(180,390,250,230,30,RED,9)
        for y in [420,510,600]:arrow((420,y),(770,y),RED)
        cup(730,365,300,285,.9);dots(750,410,250,210,23,RED,9)
        label(310,740,'食材中的可萃取成分');label(880,740,'进入水相')
        panel(885,'温度、时间、粒径和水量共同影响结果')
        thermometer(230,1100,'温度');circ(600,1095,65,WHITE);d.line((600,1095,600,1050),fill=INK,width=5);d.line((600,1095,640,1115),fill=INK,width=5);label(600,1240,'时间')
        for x,y in [(900,1070),(965,1130),(1030,1065)]:circ(x,y,17,GOLD)
        label(970,1240,'粒径与水量')
    elif n==21:
        panel(215,'挥发性成分进入鼻腔，形成香气')
        food(160,420,280,160)
        for x,y in [(520,440),(650,380),(780,450),(940,390)]:circ(x,y,13,GOLD)
        arrow((470,510),(1000,510),GOLD);label(300,710,'香辛料');label(870,710,'嗅觉通路')
        panel(870,'辣与麻还涉及口腔感觉系统')
        d.ellipse((180,1030,470,1170),fill='#d8a091',outline=INK,width=5);circ(310,1100,27,RED);arrow((520,1100),(700,1100),RED)
        for x,y in [(790,1090),(870,1050),(950,1120)]:circ(x,y,24,PALE)
        d.line((790,1090,870,1050,950,1120),fill=INK,width=5);label(870,1240,'刺激信号，不是基本味')
    elif n==22:
        panel(215,'冻结前后，水分分布与组织可发生变化')
        cell(110,390,280,240);cell(790,390,280,240,True)
        for x,y in [(850,450),(960,540),(880,570)]:snow(x,y,28)
        arrow((450,510),(720,510),BLUE);label(250,730,'液态水分布');label(930,730,'部分结冰与组织改变')
        panel(890,'解冻：水重新分布，可能出现汁液流出')
        food(260,1040,680,150)
        for x,y in [(400,1230),(530,1250),(700,1220),(850,1250)]:circ(x,y,13,BLUE)
        label(600,1320,'冷冻通常抑制生长，并不等于灭菌',34,RED)
    elif n==23:
        panel(215,'保存不是任选一种“保险”')
        for x,y,cap,col in [(300,430,'温度',BLUE),(900,430,'水活度',GOLD),(300,700,'酸度',RED),(900,700,'包装与卫生',INK)]:
            circ(x,y,80,PALE,col)
            if cap=='包装与卫生':label(x,y-22,'包装与',31);label(x,y+22,'卫生',31)
            else:label(x,y,cap,34)
            arrow((x+(-90 if x>600 else 90),y),(600+(-70 if x<600 else 70),565),col)
        jar(510,475,180,180,WHITE);label(600,795,'共同影响食品中的微生物与反应',34)
        panel(940,'同样湿润，不保证同样容易变质')
        for x,col,cap in [(250,WATER,'配方'),(600,PALE,'加工'),(950,GOLD,'储存')]:
            jar(x-65,1060,130,150,col);label(x,1270,cap)
    elif n==24:
        panel(215,'接触路径：把生食与即食食物分开')
        plate(240,470,100,'#d9a18b');food(530,400,150,120);plate(930,470,100,PALE)
        for x,y in [(270,460),(565,430),(960,460)]:bug(x,y,RED)
        arrow((360,470),(510,470));arrow((710,470),(800,470));label(240,650,'生食');label(610,650,'手与器具');label(930,650,'即食食品')
        d.line((700,380,800,580),fill=RED,width=10);label(600,780,'在转移发生前，阻断这条路径',35,RED)
        panel(930,'时间与温度：另一个独立维度')
        thermometer(250,1110,'温度控制');d.line((520,1120,1030,1120),fill=INK,width=6)
        for x in [540,730,920]:d.line((x,1105,x,1135),fill=INK,width=4)
        arrow((540,1170),(1020,1170),BLUE);label(790,1260,'及时处理与储存')
    elif n==25:
        panel(215,'油污：表面活性剂帮助分散与带走')
        circ(300,510,85,GOLD)
        for a in range(0,360,30):
            x=300+100*math.cos(math.radians(a));y=510+100*math.sin(math.radians(a));circ(x,y,8,RED,outline=None)
        arrow((460,510),(680,510),BLUE)
        for x,y in [(770,450),(900,530),(780,610)]:circ(x,y,30,GOLD);circ(x,y,37,None,RED,4)
        label(300,740,'油污与界面');label(870,740,'分散后随冲洗带走')
        panel(880,'水垢：矿物沉积与去油不是同一问题')
        d.arc((220,1010,510,1220),0,180,fill=INK,width=12)
        for x,y in [(270,1170),(350,1200),(430,1170)]:circ(x,y,16,GRAY)
        jar(790,1030,140,170,PALE);label(860,1255,'按单一产品标签使用')
        wrap(100,1320,'清洁剂不混用；含氯产品尤其不能混酸或氨。',size=30,color=RED)
    elif n==26:
        panel(215,'传热材料和储热能力，影响受热过程')
        for x,col,cap in [(170,GRAY,'金属锅体'),(730,'#b4977b','陶瓷等材料')]:
            d.rectangle((x,430,x+280,560),fill=col,outline=INK,width=5)
            for xx in [x+70,x+140,x+210]:arrow((xx,650),(xx,570));arrow((xx,420),(xx,350),GOLD)
            label(x+140,740,cap)
        panel(890,'电磁炉：交变磁场使合适锅底产生热')
        d.rectangle((260,1040,940,1090),fill=GRAY,outline=INK,width=4)
        wave(330,1190,540,35,36,RED)
        for x in [420,600,780]:arrow((x,1160),(x,1100),BLUE)
        label(600,1310,'适配性、厚度与复合结构都要一起看',33)
    elif n==27:
        panel(215,'配料顺序提供组成线索，不能包办评价')
        d.rounded_rectangle((170,360,1030,730),radius=25,fill=WHITE,outline=INK,width=5)
        txt(220,405,'示例配料',38);txt(220,475,'燕麦、水、糖、植物油……',36)
        for x,col,h in [(300,PALE,110),(500,WATER,90),(700,GOLD,45),(900,RED,25)]:d.rectangle((x-40,670-h,x+40,670),fill=col,outline=INK,width=2)
        panel(880,'把功能、用量与整份营养信息放在一起')
        for x,cap,col in [(240,'功能',BLUE),(600,'用量',GOLD),(960,'营养组成',RED)]:
            jar(x-65,1040,130,160,PALE);label(x,1260,cap);circ(x,1115,25,col)
        wrap(100,1320,'图中为虚构食品示例，不代表具体产品或法规阈值。',size=30)
    elif n==28:
        panel(215,'准备、烹调与收尾，是连续的过程')
        for x,cap,col in [(240,'食材准备',PALE),(600,'烹调变化',GOLD),(960,'及时分装',WATER)]:
            plate(x,490,100,col);label(x,680,cap)
        arrow((360,490),(470,490));arrow((720,490),(830,490))
        panel(870,'每道菜都可以同时包含多种机制')
        plate(600,1110,320,'#f0dfc4')
        for x,y,col in [(430,1100,PALE),(600,1135,GOLD),(770,1080,'#dfac88')]:circ(x,y,52,col)
        label(270,1010,'传热',35,RED);label(930,1010,'结构改变',35,RED);label(600,1290,'风味 · 质地 · 食品安全',35)
    out=ROOT/'assets/images'/f'diagram-{n:02}.png';out.parent.mkdir(parents=True,exist_ok=True);tmp=out.with_suffix('.tmp.png'); im.save(tmp,format='PNG',compress_level=6); tmp.replace(out)

# A review contact sheet is an editorial intermediate, not a chapter asset.
thumbs=[]
for n in range(1,29):
    a=Image.open(ROOT/'assets/images'/f'diagram-{n:02}.png');a.thumbnail((240,290));thumbs.append(a)
sheet=Image.new('RGB',(240*7,290*4),'white')
for i,a in enumerate(thumbs):sheet.paste(a,((i%7)*240,(i//7)*290))
(ROOT/'editorial').mkdir(exist_ok=True);sheet.save(ROOT/'editorial/diagram-contact-sheet.jpg',quality=90)
print('Generated 28 concept figures and contact sheet.')
