# 秀米 / 公众号 自动化踩坑记录

用 Playwright 连本机 Chrome（`--remote-debugging-port=9222`，独立 user-data-dir）操作秀米。
下面每条都是实测踩过的，按这个做能省几个小时。

## 连接

```js
const browser = await chromium.connectOverCDP('http://127.0.0.1:9222');
const ctx = browser.contexts()[0];
const page = ctx.pages().find(p => p.url().includes('xiumi.us') && !p.url().startsWith('chrome-extension'));
```

Chrome 用 `start-browser.mjs` 那种方式拉起：

```js
spawn('C:/Program Files/Google/Chrome/Application/chrome.exe', [
  '--remote-debugging-port=9222', '--user-data-dir=./profile',
  '--no-first-run', '--disable-blink-features=AutomationControlled', 'https://xiumi.us/'
], { detached: true, stdio: 'ignore' });
```

## 免费号的硬限制（先确认，再动手）

| 功能 | 表现 | 验证方式 |
|---|---|---|
| 导入 HTML 代码 | 弹窗里 textarea `disabled`，提示"该功能对等级会员VIP开放" | 打开「更多 → 导入HTML代码」读 `textarea.disabled` |
| 全文背景 / 背景组 | 入口在会员区；`创建背景组`、`以本图为背景` 存在于 DOM 但点不到 | grep DOM `.op-dock-item` |
| 粘贴带样式 HTML | 被拍平成纯文本 | 用 CF_HTML 写剪贴板后 Ctrl+V，检查是否保留 `style` |

**结论**：免费号只能"图片 + 纯文字样式"。想要纸质背景 + 可编辑文字，只有开 VIP 导 HTML。

## 插入图片：插入 vs 替换

- 光标在**空文本格**里点图库图片 → **插入**
- 选中了某个图块再点 → **替换那块**（会静默吃掉原图，很容易毁稿）

安全做法：先 `Ctrl+Home` 把光标移到最前，或在文末按 `Enter` 造一个空行，再点缩略图。

## 图库顺序不可靠

图库是"最新在前"，批量上传后按坐标点会错位。可靠方案：

1. 给每个待插入文件做一份**带不可见标记的副本**（改左上角 1 个像素的 RGB）
2. 上传一份 → 立刻插入最左上那张 → 下一份
3. 每次插入后核对 `.tn-editing-desk img` 数量 +1

```python
px = img.load(); r,g,b = px[0,0]; px[0,0] = (min(255,r+1), g, max(0,b-1))
```

## 块间 10px 白缝

每个图片块自带 10px 上下外边距，`基础格式 → 段落间距 0` 管不到它。

修法（每个块都要做一遍）：

1. 双击图块（第一次点选块，第二次选中组件）
2. 点「组件定位」
3. 面板里两个值为 `10` 的输入 → 改成 `0`

批量验证：

```js
const gaps = await page.evaluate(() => {
  const L = [...document.querySelectorAll('.tn-editing-desk img')].filter(i => i.clientWidth > 200)
    .map(i => { const r = i.getBoundingClientRect(); return [r.top, r.bottom]; })
    .sort((a,b) => a[0]-b[0]);
  return L.slice(1).map((c,i) => Math.round(c[0] - L[i][1]));
});
// 目标：[0,0,0,…]
```

## 左右白边

标题面板 → 打开「开启音乐视频等增强模式」后，面板里出现 **「两边不留白」** 复选框，勾上即可。
（该复选框只在增强模式开启、且面板展开时渲染；找不到就先把面板滚动到底。）

## 其它固定坐标（1440 宽窗口，仅供参考，优先用 DOM 查）

| 元素 | 选择器 |
|---|---|
| 左侧导航 | `31, 95` 图文模板 / `31, 340` 我的图库 |
| 基础格式 | `text=基础格式` |
| 保存 | `text=保存` 或 `Control+S` |
| 复制模式提示 | `先退出复制模式` → 点 `退出` 才能继续编辑 |

## 保存与恢复

- `Control+S` 后 URL 会带 `/paper/for/<id>/cube/0`，`id` 就是草稿号
- 重新打开时若弹「上次没有保存到服务器，是否恢复」，点 **确定**（点取消会加载旧的服务器版本）
