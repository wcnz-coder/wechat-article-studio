# wechat-article-studio

给公众号做推文的生产线：**一份素材 + 一句话要求 → 封面、正文、动效、可发布草稿**。

不是模板合集，是一套**判断流程**：先定审美方向，再补素材，最后才排版。方向错了，后面每一步都是在给错误加装饰。

## 里面有什么

| 目录 | 内容 |
|---|---|
| `SKILL.md` | 生产线总纲：审美方向表、五步流程、质检清单、翻车对照 |
| `INSTALL.md` | 装进 DSH 的三行命令 |
| `resources/gen-ornaments.py` | 纹样 / 印章 / 角花 / 宣纸底 生成器（43 件，参数化） |
| `resources/gen-motion.py` | 9 种中式动效 GIF 生成器（桂花、墨点、水波、雁阵、灯笼、雾、竹影、星火、落款） |
| `resources/template-chinese.html` | 中式版式模板，浏览器直接打开看效果 |
| `resources/xiumi-automation.md` | 秀米自动化选择器与十个坑 |
| `assets/ornaments/` | 103 件成品纹样（回纹、菱格、印章、角花、冰裂、纸底） |
| `assets/motion/` | 9 个成品动效 GIF |
| `assets/cover/` | 中式封面成品 ×4（2.35:1 / 1:1，带字与不带字） |
| `assets/demo/` | 示例长图切段 ×6，用来看"一次渲染再切片"的效果 |

## 快装

```bash
mkdir -p ~/.dsh/skills
cp -r wechat-article-studio ~/.dsh/skills/     # Windows: 复制到 C:\Users\<你>\.dsh\skills\
```

重启 DSH，对话里说「用 wechat-article-studio 做一篇推文」即可。

不装 DSH 也能用：脚本 `pip install pillow` 后直接跑，模板双击就能看。

## 快速用

```bash
# 生成一整套纹样
python resources/gen-ornaments.py -o assets/ornaments --palette gold

# 生成动效（底色从你的整页长图里裁，保证衔接无缝）
python resources/gen-motion.py --paper page.png --crop 80,330,680,730 -o out/motion
python resources/gen-motion.py --only 灯笼 竹影 --paper page.png
```

## 三条硬经验

1. **连续性靠一次渲染**：整篇 HTML 渲染成一张长图再切段，接缝天然连续；动效 GIF 的底色从同一张图的空白区裁。
2. **封面别让 AI 写字**：只出无字底图，标题后期叠（竖排宋体 + 朱印），错字率归零。
3. **秀米免费号只能图片化**：不能导 HTML、不能设全文背景。要"可编辑文字 + 纸质背景"，只有开会员或用公众号后台直贴。

更多坑见 `resources/xiumi-automation.md`（图片块 10px 外边距、插入 vs 替换、图库顺序不可靠……）。

## 许可

- 代码与文档：MIT
- `assets/` 下的全部图片与动效：**CC0**（程序生成，随便用，不用署名）

## 贡献

想加新纹样/动效，改 `resources/gen-*.py` 里的参数或加一个函数，然后：

```bash
python resources/gen-ornaments.py -o assets/ornaments
```

提 PR 时把生成的成品一起带上，别人拿到就能直接用。
