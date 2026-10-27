# 厨房里的科学冒险

从一锅水到一桌饭，读懂化学、生物与物理。中文兴趣科普，2026-10-26扩展阅读稿。

本版28章，约5.5万汉字（含图注和章末资料），另有导读、观察手册、术语表及现象索引。42幅独立配图：14幅AI趣味漫画、28幅原创中文机制图。相邻章节有时共用同幅漫画，书内共56处配图引用；不把重复引用计为新图。

## 阅读顺序

1. [从现象开始：厨房里的观察方法](chapters/01-observe.md)
2. [水的多重身份：溶解、沸腾与结冰](chapters/02-water.md)
3. [盐与糖：浓度、结晶和水的去向](chapters/03-salt-sugar.md)
4. [酸与碱：从食醋到小苏打](chapters/04-acid-base.md)
5. [火候的物理学：热怎样进入食物](chapters/05-heat.md)
6. [蒸、煮与压力：气体怎样改变烹饪](chapters/06-pressure.md)
7. [油脂的性格：熔点、氧化与香气](chapters/07-fat.md)
8. [油水相处：乳化与酱汁](chapters/08-emulsion.md)
9. [把空气吃进去：泡沫与打发](chapters/09-foam.md)
10. [淀粉的旅程：米饭、面条与勾芡](chapters/10-starch.md)
11. [蛋白质的变化：鸡蛋、豆腐与肉](chapters/11-protein.md)
12. [面团的骨架：面筋、酵母与膨松](chapters/12-dough.md)
13. [柔软的网络：果冻、果酱与凝胶](chapters/13-gel.md)
14. [结晶的手艺：巧克力、黄油与冰淇淋](chapters/14-chocolate.md)
15. [褐变的三条路：烤香、焦糖与切面](chapters/15-browning.md)
16. [蔬果的颜色与脆度：细胞如何改变](chapters/16-plants.md)
17. [酶在厨房：从菠萝到洋葱](chapters/17-enzymes.md)
18. [微生物上桌：发酵的分工与边界](chapters/18-fermentation.md)
19. [风味的拼图：味觉、嗅觉与口感](chapters/19-flavor.md)
20. [把味道带出来：茶、咖啡与高汤](chapters/20-extraction.md)
21. [香辛料与刺激：葱姜蒜、辣椒和花椒](chapters/21-spice.md)
22. [低温的作用：冷藏、冷冻与解冻](chapters/22-cold.md)
23. [保存的科学：水活度、酸度与包装](chapters/23-preserve.md)
24. [看不见的风险：食安与交叉污染](chapters/24-safety.md)
25. [洗净厨房：油污、水垢与清洁剂](chapters/25-clean.md)
26. [锅具与炉灶：材料、能量与选择](chapters/26-tools.md)
27. [读懂配料表：添加剂与加工食品](chapters/27-labels.md)
28. [一顿饭的科学推演：从准备到收尾](chapters/28-meal.md)

## 阅读与构建

直接阅读分章Markdown；电子阅读版输出为 `build/Kitchen-Science-Expanded.epub`，适合手机或平板的EPUB阅读器。

依赖Python 3.10+和Pillow。安装与运行：

```bash
python3 -m pip install -r requirements.txt
python3 scripts/build_book.py --check-only
python3 scripts/build_book.py
```

重新生成原创机制图：

```bash
python3 scripts/draw_diagrams.py
```

漫画已作为实际图片包含在工程，不在构建时重新生成。构建只需Pillow，不需要浏览器、TeX、Pandoc或网络生图。网页发布使用独立轻量构建流程。EPUB内部XHTML是电子书格式组成部分。

## 文件约定

- `book.json`：统一书名、章节顺序、稳定ID与路径，便于后续主页发布复用。
- `chapters/`：28个分章主稿，事实附近有来源链接，章末保留资料。
- `appendices/`：导读、观察手册、术语和现象回查。
- `assets/images/`：已入书漫画与机制图；`assets/fonts/`是可复现绘图字体及许可。
- `references/`：分组来源核查表。
- `editorial/`：图像索引、提示词要点、机制图核查及交叉审稿记录，不进入阅读版。
- `scripts/`：绘图、资源索引、编辑统一与EPUB构建；`build/`为忽略入Git的产物。

## 图像与科学边界

漫画是AI教学示意，角色表情不代表分子的意愿；透明锅体等是帮助观察的艺术处理。概念图不按真实尺度，也不提供实测数据。科学解释以正文与资料为准，不能以成品外观判断安全或反推完整温度经历。

书中小观察不品尝观察样品。发酵、罐藏、消毒等机制不构成未经验证的通用配方。温度与时间应连同明确机构、食物和使用情境阅读。法规章节注明资料日期与新旧标准过渡条件。

仓库：https://github.com/YZYExp/Learn-Kitchen-Chemistry 。Git根提交仅包含零字节README，其后叠加内容。

## 网页与GitHub Pages

网页直接消费同一份book.json、章节、附录与图片，构建命令：

```bash
python3 -m pip install -r site/requirements.txt
python3 scripts/build_site.py --base-path /Learn-Kitchen-Chemistry/
```

生成目录为build/site。主页、章节导航、搜索与附录从统一内容清单派生；图片保持比例并按需加载。

`.github/workflows/pages.yml`在main推送后构建部署，PR仅检查。网页与`.github/workflows/epub.yml`整书导出互相独立；网页不安装排版系统、中文字库或浏览器。首次启用请在仓库Settings → Pages把Source设为GitHub Actions，随后重新运行网页工作流。

`downloads/`为已校验的2026-10-26阅读版及其SHA256元数据，网站显式引用该版本。后续书稿更新后，可从独立EPUB工作流取得新版文件，再替换downloads输入；网页不会悄悄复用本机build目录中的旧电子书。
