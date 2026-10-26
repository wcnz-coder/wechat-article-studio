# 安装说明

这是一个 **DSH 技能包**（DeepSeek Harness / Claude 类技能格式），装好后在对话里说「用 wechat-article-studio 做一篇推文」就会自动调用。

## Windows

1. 解压，得到 `wechat-article-studio` 文件夹
2. 把它整个复制到：

```
C:\Users\<你的用户名>\.dsh\skills\
```

最终路径应该是：

```
C:\Users\<你的用户名>\.dsh\skills\wechat-article-studio\SKILL.md
```

3. 重启 DSH（或新开一个会话），技能列表里会多出 `wechat-article-studio`

## macOS / Linux

```bash
mkdir -p ~/.dsh/skills
cp -r wechat-article-studio ~/.dsh/skills/
```

## 检查是否装好

```bash
ls ~/.dsh/skills/wechat-article-studio/
# 应该看到 SKILL.md 和 resources/
```

## 不装 DSH 也能用

包里这些是独立的，可以单独拿走：

| 文件 | 用途 |
|---|---|
| `resources/gen-ornaments.py` | 生成中式纹样、印章、宣纸底（Pillow） |
| `resources/gen-motion.py` | 生成 9 种动效 GIF（Pillow） |
| `resources/template-chinese.html` | 中式推文版式模板，浏览器打开即可看效果 |
| `resources/xiumi-automation.md` | 秀米自动化的选择器与踩坑记录 |

脚本依赖：`pip install pillow`，字体用系统自带（`C:/Windows/Fonts/simsun.ttc`、`msyh.ttc`）。

## 使用时需要准备

- 素材文件夹：版头、logo、照片、吉祥物
- 一句话要求：主题 + 调性（例如「中秋，清冷雅致」）
- 如果要落到秀米：秀米账号（免费号只能图片版；开会员才能导 HTML）

## 注意

技能里写的自动化参数基于 1440 宽的窗口坐标，换机器可能要重测；优先用 `xiumi-automation.md` 里的 DOM 选择器，别硬编码坐标。
