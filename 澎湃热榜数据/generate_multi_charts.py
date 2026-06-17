#!/usr/bin/env python3
"""
澎湃新闻24h热榜 - 多张可视化图片生成器
生成多种风格的数据可视化图片：热榜排行图、热度区间图、分类分布图、词云风格图等
"""

from PIL import Image, ImageDraw, ImageFont
import os
import math
from pathlib import Path

# ==================== 热榜数据 ====================
HOT_DATA = [
    {"title": "刚完赛就被勒令离开美国！伊朗队主帅抱怨球队在世界杯受压迫", "hot": 476},
    {"title": "特朗普大发雷霆后，内塔尼亚胡回应：以军不撤", "hot": 383},
    {"title": "\u201c成都27岁女子遇害案\u201d二审维持原判：梁某滢死缓", "hot": 341},
    {"title": "lululemon向公众及朱一龙道歉：未能在前期充分识别潜在争议", "hot": 312},
    {"title": "黑龙江省纪委副书记、省监委副主任姜宏伟任上被查", "hot": 308},
    {"title": "上海链家通报调查细节：未吃差价！已主动联系主管部门指导", "hot": 287},
    {"title": "梅西第200场倒计时，阿根廷开始一个国家的告别", "hot": 282},
    {"title": "伊朗2比2新西兰，本届世界杯\u201c亚洲球队\u201d保持不败", "hot": 273},
    {"title": "新任国防部新闻发言人陈曦亮相", "hot": 270},
    {"title": "欧盟指控中方\u201c训练俄军事人员在乌作战\u201d，外交部：污蔑抹黑", "hot": 199},
    {"title": "山姆中国更换董事长：会员店业态总裁刘鹏接任", "hot": 196},
    {"title": "成都\u201c27岁王紫雅遇害案\u201d二审上午开庭", "hot": 181},
    {"title": "特朗普称美伊协议谈判进入第二阶段", "hot": 163},
    {"title": "深观察｜办好人民满意的教育：从\u201c有学上\u201d到\u201c上好学\u201d", "hot": 148},
    {"title": "伊朗队主帅：球队突然被勒令立即离开美国", "hot": 113},
    {"title": "青海海西州地震已致1人遇难、4人受伤", "hot": 87},
    {"title": "马上评｜在影院看世界杯，解锁的不只是看球新体验", "hot": 86},
    {"title": "观察｜美以伊战争结束的开始", "hot": 80},
    {"title": "江苏省副省长陈忠伟任江苏省委常委", "hot": 74},
    {"title": "\u201c成都27岁女子遇害案\u201d二审今日开庭", "hot": 30},
]

# ==================== 颜色方案 ====================
BG_DARK = (10, 14, 23)
BG_MID = (20, 27, 45)
BORDER = (42, 53, 85)
TEXT_WHITE = (224, 230, 240)
TEXT_GRAY = (122, 139, 168)
TEXT_DIM = (80, 96, 118)
RED = (255, 45, 45)
ORANGE = (255, 107, 53)
YELLOW = (255, 200, 64)
BLUE = (59, 130, 246)
GREEN = (34, 197, 94)
PURPLE = (168, 85, 247)
CYAN = (6, 182, 212)
PINK = (236, 72, 153)

BAR_COLORS = [RED, ORANGE, YELLOW, BLUE, GREEN, PURPLE, CYAN, PINK]

OUTPUT_DIR = Path(os.path.expanduser("~")) / "Desktop" / "澎湃热榜数据"


def get_font(size, bold=False):
    """加载中文字体"""
    candidates = [
        "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/msyhbd.ttc",
        "C:/Windows/Fonts/simhei.ttf",
        "C:/Windows/Fonts/simsun.ttc",
        "C:/Windows/Fonts/STKAITI.TTF",
        "C:/Windows/Fonts/STZHONGS.TTF",
    ]
    for fp in candidates:
        if os.path.exists(fp):
            try:
                return ImageFont.truetype(fp, size)
            except Exception:
                continue
    return ImageFont.load_default()


def truncate_text(draw, text, font, max_width):
    """截断文本"""
    if draw.textlength(text, font=font) <= max_width:
        return text
    while text and draw.textlength(text + "...", font=font) > max_width:
        text = text[:-1]
    return text + "..."


def draw_rounded_rect(draw, xy, radius, fill=None, outline=None, width=1):
    """绘制圆角矩形"""
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def draw_gradient_bar(draw, x, y, w, h, color_start, color_end, radius=4):
    """绘制渐变色条"""
    for i in range(h):
        ratio = i / h
        r = int(color_start[0] + (color_end[0] - color_start[0]) * ratio)
        g = int(color_start[1] + (color_end[1] - color_start[1]) * ratio)
        b = int(color_start[2] + (color_end[2] - color_start[2]) * ratio)
        draw_rounded_rect(draw, (x, y + i, x + w, y + i + 1), radius=radius if i == 0 else 0, fill=(r, g, b))


# ============================================================
# 图1：热榜TOP20排行大图（横向条形图 + 统计卡片）
# ============================================================
def generate_chart1_ranking():
    """图1：澎湃24h热榜 - 综合排行大图"""
    W, H = 1200, 1600
    img = Image.new("RGB", (W, H), BG_DARK)
    draw = ImageDraw.Draw(img)

    fonts = {
        "logo": get_font(42, True),
        "title": get_font(24, True),
        "text": get_font(17),
        "small": get_font(13),
        "rank": get_font(20, True),
        "stat_num": get_font(36, True),
        "stat_label": get_font(14),
        "hot_val": get_font(16, True),
    }

    # ---- 标题 ----
    y = 30
    title_text = "澎湃新闻 · 24小时热榜 TOP 20"
    tw = draw.textlength(title_text, font=fonts["logo"])
    draw.text(((W - tw) // 2, y), title_text, fill=TEXT_WHITE, font=fonts["logo"])
    y += 55
    sub = "数据来源：thepaper.cn  |  抓取时间：2026-06-17  |  共20条热榜新闻"
    sw = draw.textlength(sub, font=fonts["small"])
    draw.text(((W - sw) // 2, y), sub, fill=TEXT_GRAY, font=fonts["small"])

    # ---- 统计卡片 ----
    y += 50
    max_hot = max(d["hot"] for d in HOT_DATA)
    avg_hot = round(sum(d["hot"] for d in HOT_DATA) / len(HOT_DATA))
    over300 = sum(1 for d in HOT_DATA if d["hot"] >= 300)
    over200 = sum(1 for d in HOT_DATA if d["hot"] >= 200)
    total_hot = sum(d["hot"] for d in HOT_DATA)

    stats = [
        ("20", "热榜条目", ORANGE),
        (str(max_hot), "最高热度", RED),
        (str(avg_hot), "平均热度", YELLOW),
        (str(over300), "热度≥300", BLUE),
        (str(over200), "热度≥200", GREEN),
        (str(total_hot), "总热度值", PURPLE),
    ]

    card_w, card_h = 160, 80
    gap = 16
    total_w = len(stats) * card_w + (len(stats) - 1) * gap
    start_x = (W - total_w) // 2

    for i, (num, label, color) in enumerate(stats):
        cx = start_x + i * (card_w + gap)
        draw_rounded_rect(draw, (cx, y, cx + card_w, y + card_h), radius=12, fill=BG_MID, outline=BORDER, width=1)
        nw = draw.textlength(num, font=fonts["stat_num"])
        draw.text((cx + (card_w - nw) // 2, y + 8), num, fill=color, font=fonts["stat_num"])
        lw = draw.textlength(label, font=fonts["stat_label"])
        draw.text((cx + (card_w - lw) // 2, y + 52), label, fill=TEXT_GRAY, font=fonts["stat_label"])

    # ---- 排行列表 ----
    y += card_h + 40
    row_h = 56
    margin_l = 50
    margin_r = 30
    bar_area_w = W - margin_l - margin_r - 200

    # 列标题
    draw.text((margin_l + 6, y), "排名", fill=TEXT_DIM, font=fonts["small"])
    draw.text((margin_l + 68, y), "新闻标题", fill=TEXT_DIM, font=fonts["small"])
    draw.text((W - margin_r - 100, y), "热度值", fill=TEXT_DIM, font=fonts["small"])
    y += 24

    for i, item in enumerate(HOT_DATA):
        ry = y + i * (row_h + 4)
        rank = i + 1
        hot = item["hot"]
        pct = hot / max_hot

        # 行背景
        alpha_fill = (30, 40, 62) if rank % 2 == 0 else BG_DARK
        draw_rounded_rect(draw, (margin_l - 4, ry, W - margin_r, ry + row_h),
                          radius=8, fill=alpha_fill, outline=BORDER, width=1)

        # 排名徽章
        badge_colors = {1: RED, 2: ORANGE, 3: YELLOW}
        badge_c = badge_colors.get(rank, (35, 50, 75))
        badge_tc = (255, 255, 255) if rank <= 2 else (20, 20, 20) if rank == 3 else TEXT_GRAY
        draw_rounded_rect(draw, (margin_l + 6, ry + 10, margin_l + 44, ry + 46), radius=8, fill=badge_c)
        rw = draw.textlength(str(rank), font=fonts["rank"])
        draw.text((margin_l + 25 - rw // 2, ry + 14), str(rank), fill=badge_tc, font=fonts["rank"])

        # 标题
        tx = margin_l + 58
        title = truncate_text(draw, item["title"], fonts["text"], bar_area_w)
        draw.text((tx, ry + 6), title, fill=TEXT_WHITE, font=fonts["text"])

        # 热度进度条
        bar_x = tx
        bar_y = ry + 34
        bar_w = bar_area_w
        bar_h = 8
        draw_rounded_rect(draw, (bar_x, bar_y, bar_x + bar_w, bar_y + bar_h), radius=4, fill=(25, 35, 55))
        fill_w = max(6, int(bar_w * pct))
        if hot >= 300:
            bc = RED
        elif hot >= 200:
            bc = ORANGE
        elif hot >= 100:
            bc = YELLOW
        else:
            bc = BLUE
        draw_rounded_rect(draw, (bar_x, bar_y, bar_x + fill_w, bar_y + bar_h), radius=4, fill=bc)

        # 热度数值
        hx = W - margin_r - 110
        draw.text((hx, ry + 14), str(hot), fill=ORANGE, font=fonts["hot_val"])

    # ---- 底部 ----
    footer_y = H - 50
    footer = "澎湃新闻24h热榜可视化 · 数据仅供学习研究使用 · 目标网页：https://m.thepaper.cn/htmlstatic"
    fw = draw.textlength(footer, font=fonts["small"])
    draw.text(((W - fw) // 2, footer_y), footer, fill=TEXT_DIM, font=fonts["small"])

    path = OUTPUT_DIR / "图1_热榜TOP20排行大图.jpg"
    img.save(str(path), "JPEG", quality=95)
    print(f"[图1] 已保存: {path} ({W}x{H})")
    return path


# ============================================================
# 图2：热度区间环形饼图
# ============================================================
def generate_chart2_pie():
    """图2：热度区间分布 - 环形饼图"""
    W, H = 1000, 900
    img = Image.new("RGB", (W, H), BG_DARK)
    draw = ImageDraw.Draw(img)

    fonts = {
        "logo": get_font(36, True),
        "title": get_font(22, True),
        "text": get_font(16),
        "small": get_font(13),
        "stat_num": get_font(48, True),
        "stat_label": get_font(16),
        "legend": get_font(15),
        "pct": get_font(13),
    }

    # 标题
    y = 30
    title = "澎湃新闻24h热榜 · 热度区间分布"
    tw = draw.textlength(title, font=fonts["logo"])
    draw.text(((W - tw) // 2, y), title, fill=TEXT_WHITE, font=fonts["logo"])

    y += 55
    sub = "共20条热榜新闻  |  数据来源：thepaper.cn"
    sw = draw.textlength(sub, font=fonts["small"])
    draw.text(((W - sw) // 2, y), sub, fill=TEXT_GRAY, font=fonts["small"])

    # 区间统计
    ranges = [
        ("400+ 极热", 400, None, RED),
        ("200-399 高热", 200, 399, ORANGE),
        ("100-199 中热", 100, 199, YELLOW),
        ("50-99 低热", 50, 99, GREEN),
        ("<50 微热", 0, 49, BLUE),
    ]
    range_counts = []
    for label, lo, hi, _ in ranges:
        if hi:
            cnt = sum(1 for d in HOT_DATA if lo <= d["hot"] <= hi)
        else:
            cnt = sum(1 for d in HOT_DATA if d["hot"] >= lo)
        range_counts.append(cnt)

    total = sum(range_counts)
    pie_colors = [RED, ORANGE, YELLOW, GREEN, BLUE]

    # 画环形图
    pie_cx, pie_cy = 220, y + 280
    outer_r, inner_r = 170, 100
    start_angle = -90

    for i, cnt in enumerate(range_counts):
        if cnt == 0:
            continue
        sweep = (cnt / total) * 360
        draw.pieslice(
            [pie_cx - outer_r, pie_cy - outer_r, pie_cx + outer_r, pie_cy + outer_r],
            start_angle, start_angle + sweep,
            fill=pie_colors[i]
        )
        start_angle += sweep

    # 中心圆
    draw.ellipse(
        [pie_cx - inner_r, pie_cy - inner_r, pie_cx + inner_r, pie_cy + inner_r],
        fill=BG_DARK
    )
    tw20 = draw.textlength("20", font=fonts["stat_num"])
    draw.text((pie_cx - tw20 // 2, pie_cy - 28), "20", fill=TEXT_WHITE, font=fonts["stat_num"])
    lab = "热榜条目"
    lw = draw.textlength(lab, font=fonts["stat_label"])
    draw.text((pie_cx - lw // 2, pie_cy + 24), lab, fill=TEXT_GRAY, font=fonts["stat_label"])

    # 图例
    lx, ly = 460, y + 120
    for i, ((label, lo, hi, _color), cnt) in enumerate(zip(ranges, range_counts)):
        ry = ly + i * 56
        draw_rounded_rect(draw, (lx, ry, lx + 480, ry + 44), radius=10, fill=BG_MID, outline=BORDER, width=1)
        # 色块
        draw_rounded_rect(draw, (lx + 16, ry + 10, lx + 32, ry + 34), radius=4, fill=pie_colors[i])
        draw.text((lx + 48, ry + 8), label, fill=TEXT_WHITE, font=fonts["legend"])
        pct = (cnt / total * 100) if total > 0 else 0
        val_t = f"{cnt} 条  ({pct:.1f}%)"
        vw = draw.textlength(val_t, font=fonts["pct"])
        draw.text((lx + 456 - vw, ry + 10), val_t, fill=TEXT_GRAY, font=fonts["pct"])

    # 补充统计卡片
    card_y = ly + len(ranges) * 56 + 30
    max_hot = max(d["hot"] for d in HOT_DATA)
    min_hot = min(d["hot"] for d in HOT_DATA)
    avg_hot = round(sum(d["hot"] for d in HOT_DATA) / len(HOT_DATA))

    mini_stats = [
        (str(max_hot), "最高热度", RED),
        (str(avg_hot), "平均热度", YELLOW),
        (str(min_hot), "最低热度", GREEN),
    ]
    card_w2 = 140
    gap2 = 20
    total_w2 = len(mini_stats) * card_w2 + (len(mini_stats) - 1) * gap2
    sx = lx + (480 - total_w2) // 2

    for i, (num, label, color) in enumerate(mini_stats):
        cx = sx + i * (card_w2 + gap2)
        draw_rounded_rect(draw, (cx, card_y, cx + card_w2, card_y + 60), radius=10, fill=BG_MID, outline=BORDER, width=1)
        nw = draw.textlength(num, font=get_font(28, True))
        draw.text((cx + (card_w2 - nw) // 2, card_y + 4), num, fill=color, font=get_font(28, True))
        lw2 = draw.textlength(label, font=fonts["small"])
        draw.text((cx + (card_w2 - lw2) // 2, card_y + 36), label, fill=TEXT_GRAY, font=fonts["small"])

    # 底部
    footer = "澎湃新闻24h热榜可视化 · 数据仅供学习研究使用"
    fw = draw.textlength(footer, font=fonts["small"])
    draw.text(((W - fw) // 2, H - 40), footer, fill=TEXT_DIM, font=fonts["small"])

    path = OUTPUT_DIR / "图2_热度区间环形饼图.jpg"
    img.save(str(path), "JPEG", quality=95)
    print(f"[图2] 已保存: {path} ({W}x{H})")
    return path


# ============================================================
# 图3：热度趋势折线图
# ============================================================
def generate_chart3_trend():
    """图3：热度排行趋势折线图"""
    W, H = 1000, 800
    img = Image.new("RGB", (W, H), BG_DARK)
    draw = ImageDraw.Draw(img)

    fonts = {
        "logo": get_font(36, True),
        "title": get_font(20, True),
        "text": get_font(14),
        "small": get_font(12),
        "axis": get_font(13),
    }

    # 标题
    y = 30
    title = "澎湃新闻24h热榜 · 热度衰减趋势"
    tw = draw.textlength(title, font=fonts["logo"])
    draw.text(((W - tw) // 2, y), title, fill=TEXT_WHITE, font=fonts["logo"])
    y += 50

    # 图表区域
    chart_x, chart_y = 100, y + 30
    chart_w, chart_h = W - 200, 500

    # 坐标轴
    draw.line([(chart_x, chart_y), (chart_x, chart_y + chart_h)], fill=BORDER, width=2)
    draw.line([(chart_x, chart_y + chart_h), (chart_x + chart_w, chart_y + chart_h)], fill=BORDER, width=2)

    # Y轴刻度
    max_val = max(d["hot"] for d in HOT_DATA)
    for v in [0, 100, 200, 300, 400, 500]:
        py = chart_y + chart_h - int((v / 500) * chart_h)
        draw.line([(chart_x - 8, py), (chart_x, py)], fill=BORDER, width=1)
        draw.text((chart_x - 50, py - 8), str(v), fill=TEXT_GRAY, font=fonts["axis"])

    # 网格线
    for v in [100, 200, 300, 400]:
        py = chart_y + chart_h - int((v / 500) * chart_h)
        for gx in range(chart_x, chart_x + chart_w, 10):
            draw.point((gx, py), fill=(25, 35, 55))

    # X轴标签（每隔几条显示）
    for i in range(0, len(HOT_DATA), 3):
        px = chart_x + int((i / (len(HOT_DATA) - 1)) * chart_w) if len(HOT_DATA) > 1 else chart_x
        draw.text((px - 10, chart_y + chart_h + 10), str(i + 1), fill=TEXT_GRAY, font=fonts["axis"])

    draw.text((chart_x + chart_w // 2 - 30, chart_y + chart_h + 30), "排名", fill=TEXT_GRAY, font=fonts["axis"])

    # 填充区域（渐变）
    points_fill = [(chart_x, chart_y + chart_h)]
    for i, item in enumerate(HOT_DATA):
        px = chart_x + int((i / (len(HOT_DATA) - 1)) * chart_w) if len(HOT_DATA) > 1 else chart_x
        py = chart_y + chart_h - int((item["hot"] / 500) * chart_h)
        points_fill.append((px, py))
    points_fill.append((chart_x + chart_w, chart_y + chart_h))
    draw.polygon(points_fill, fill=(59, 130, 246, 30))

    # 折线
    points = []
    for i, item in enumerate(HOT_DATA):
        px = chart_x + int((i / (len(HOT_DATA) - 1)) * chart_w) if len(HOT_DATA) > 1 else chart_x
        py = chart_y + chart_h - int((item["hot"] / 500) * chart_h)
        points.append((px, py))

    for i in range(len(points) - 1):
        draw.line([points[i], points[i + 1]], fill=BLUE, width=3)

    # 数据点
    for i, (px, py) in enumerate(points):
        item = HOT_DATA[i]
        r = 6 if item["hot"] >= 300 else 4
        point_color = RED if item["hot"] >= 300 else ORANGE if item["hot"] >= 200 else BLUE
        draw.ellipse([px - r, py - r, px + r, py + r], fill=point_color)

        # 标注前3名
        if i < 3:
            label = f"#{i+1} {item['hot']}"
            lw = draw.textlength(label, font=fonts["small"])
            draw.text((px - lw // 2, py - 22), label, fill=point_color, font=fonts["small"])

    # 底部统计
    y_bottom = chart_y + chart_h + 60
    max_hot = max(d["hot"] for d in HOT_DATA)
    avg_hot = round(sum(d["hot"] for d in HOT_DATA) / len(HOT_DATA))
    mid_hot = sorted([d["hot"] for d in HOT_DATA])[len(HOT_DATA) // 2]

    mini = [
        (f"最高: {max_hot}", RED),
        (f"中位: {mid_hot}", YELLOW),
        (f"平均: {avg_hot}", BLUE),
    ]
    for i, (txt, color) in enumerate(mini):
        draw.text((chart_x + i * 200, y_bottom), txt, fill=color, font=fonts["title"])

    path = OUTPUT_DIR / "图3_热度衰减趋势折线图.jpg"
    img.save(str(path), "JPEG", quality=95)
    print(f"[图3] 已保存: {path} ({W}x{H})")
    return path


# ============================================================
# 图4：分类雷达图 / 柱状对比图
# ============================================================
def generate_chart4_category():
    """图4：话题分类热度对比柱状图"""
    W, H = 1000, 850
    img = Image.new("RGB", (W, H), BG_DARK)
    draw = ImageDraw.Draw(img)

    fonts = {
        "logo": get_font(36, True),
        "title": get_font(20, True),
        "text": get_font(15),
        "small": get_font(13),
        "bar_label": get_font(14, True),
        "axis": get_font(13),
    }

    # 标题
    y = 30
    title = "澎湃新闻24h热榜 · 话题分类热度对比"
    tw = draw.textlength(title, font=fonts["logo"])
    draw.text(((W - tw) // 2, y), title, fill=TEXT_WHITE, font=fonts["logo"])
    y += 50
    sub = "按话题类别聚合统计  |  数据来源：thepaper.cn"
    sw = draw.textlength(sub, font=fonts["small"])
    draw.text(((W - sw) // 2, y), sub, fill=TEXT_GRAY, font=fonts["small"])

    # 手动分类 + 聚合
    categories = {
        "国际/外交": [0, 1, 7, 9, 12, 14],
        "社会/法治": [2, 4, 5, 11, 15, 19],
        "商业/经济": [3, 10],
        "体育": [6],
        "政治/人事": [8, 18],
        "教育/评论": [13, 16, 17],
    }

    cat_data = []
    for cat, indices in categories.items():
        total_hot = sum(HOT_DATA[i]["hot"] for i in indices)
        cnt = len(indices)
        avg = round(total_hot / cnt)
        cat_data.append({"category": cat, "count": cnt, "total": total_hot, "avg": avg})

    cat_data.sort(key=lambda x: x["total"], reverse=True)

    # 柱状图区域
    chart_x, chart_y = 120, y + 50
    chart_w, chart_h = W - 240, 450

    max_total = max(c["total"] for c in cat_data)

    # Y轴
    draw.line([(chart_x, chart_y), (chart_x, chart_y + chart_h)], fill=BORDER, width=2)
    draw.line([(chart_x, chart_y + chart_h), (chart_x + chart_w, chart_y + chart_h)], fill=BORDER, width=2)

    for v in [0, 200, 400, 600, 800, 1000]:
        py = chart_y + chart_h - int((v / 1000) * chart_h)
        draw.line([(chart_x - 8, py), (chart_x, py)], fill=BORDER, width=1)
        draw.text((chart_x - 50, py - 8), str(v), fill=TEXT_GRAY, font=fonts["axis"])

    n = len(cat_data)
    bar_w = min(100, (chart_w - 100) // n)
    gap = (chart_w - n * bar_w) // (n + 1)

    for i, cat in enumerate(cat_data):
        bx = chart_x + gap + i * (bar_w + gap)
        bh = int((cat["total"] / max_total) * chart_h)
        by = chart_y + chart_h - bh

        # 柱子
        color = BAR_COLORS[i % len(BAR_COLORS)]
        draw.rounded_rectangle((bx, by, bx + bar_w, chart_y + chart_h), radius=6,
                               fill=color, outline=None)

        # 总数标注
        tw_v = draw.textlength(str(cat["total"]), font=fonts["bar_label"])
        draw.text((bx + (bar_w - tw_v) // 2, by - 24), str(cat["total"]), fill=TEXT_WHITE, font=fonts["bar_label"])

        # 平均标注
        avg_t = f"均{cat['avg']}"
        aw = draw.textlength(avg_t, font=fonts["small"])
        draw.text((bx + (bar_w - aw) // 2, by - 8), avg_t, fill=TEXT_GRAY, font=fonts["small"])

        # 类别标签
        cw = draw.textlength(cat["category"], font=fonts["text"])
        draw.text((bx + (bar_w - cw) // 2, chart_y + chart_h + 10), cat["category"], fill=TEXT_WHITE, font=fonts["text"])
        cnt_t = f"{cat['count']}条"
        cnw = draw.textlength(cnt_t, font=fonts["small"])
        draw.text((bx + (bar_w - cnw) // 2, chart_y + chart_h + 32), cnt_t, fill=TEXT_GRAY, font=fonts["small"])

    # 底部
    footer = "澎湃新闻24h热榜可视化 · 数据仅供学习研究使用"
    fw = draw.textlength(footer, font=fonts["small"])
    draw.text(((W - fw) // 2, H - 40), footer, fill=TEXT_DIM, font=fonts["small"])

    path = OUTPUT_DIR / "图4_话题分类热度对比柱状图.jpg"
    img.save(str(path), "JPEG", quality=95)
    print(f"[图4] 已保存: {path} ({W}x{H})")
    return path


# ============================================================
# 图5：热榜摘要信息卡片
# ============================================================
def generate_chart5_summary():
    """图5：澎湃热榜数据摘要信息图"""
    W, H = 1000, 700
    img = Image.new("RGB", (W, H), BG_DARK)
    draw = ImageDraw.Draw(img)

    fonts = {
        "logo": get_font(40, True),
        "title": get_font(24, True),
        "text": get_font(16),
        "small": get_font(13),
        "big_num": get_font(56, True),
        "card_title": get_font(18, True),
        "card_text": get_font(15),
        "icon": get_font(36, True),
    }

    # 标题
    y = 30
    title = "澎湃新闻 · 24h热榜数据摘要"
    tw = draw.textlength(title, font=fonts["logo"])
    draw.text(((W - tw) // 2, y), title, fill=TEXT_WHITE, font=fonts["logo"])
    y += 55
    sub = "数据来源：thepaper.cn  |  抓取时间：2026年6月17日"
    sw = draw.textlength(sub, font=fonts["small"])
    draw.text(((W - sw) // 2, y), sub, fill=TEXT_GRAY, font=fonts["small"])

    # ---- 顶部大卡片 ----
    y += 45
    max_hot = max(d["hot"] for d in HOT_DATA)
    total_hot = sum(d["hot"] for d in HOT_DATA)
    avg_hot = round(total_hot / len(HOT_DATA))

    # 大数字行
    big_cards = [
        ("🔥", str(max_hot), "最高热度", RED),
        ("📊", str(total_hot), "总热度值", ORANGE),
        ("📈", str(avg_hot), "平均热度", BLUE),
        ("📰", str(len(HOT_DATA)), "热榜条目", GREEN),
    ]

    cw, ch = 200, 110
    c_gap = 20
    total_cw = len(big_cards) * cw + (len(big_cards) - 1) * c_gap
    sx = (W - total_cw) // 2

    for i, (icon, num, label, color) in enumerate(big_cards):
        cx = sx + i * (cw + c_gap)
        draw_rounded_rect(draw, (cx, y, cx + cw, y + ch), radius=14, fill=BG_MID, outline=color, width=2)
        # 图标
        iw = draw.textlength(icon, font=fonts["icon"])
        draw.text((cx + (cw - iw) // 2, y + 4), icon, font=fonts["icon"])
        # 数字
        nw = draw.textlength(num, font=fonts["big_num"])
        draw.text((cx + (cw - nw) // 2, y + 28), num, fill=color, font=fonts["big_num"])
        # 标签
        lw = draw.textlength(label, font=fonts["small"])
        draw.text((cx + (cw - lw) // 2, y + 84), label, fill=TEXT_GRAY, font=fonts["small"])

    # ---- 热度区间横向条形图 ----
    y += ch + 40
    draw.text((50, y), "热度区间分布", fill=YELLOW, font=fonts["title"])
    draw.rectangle((38, y + 2, 44, y + 22), fill=YELLOW)
    y += 36

    range_data = [
        ("400+ 极热", sum(1 for d in HOT_DATA if d["hot"] >= 400), RED),
        ("300-399 高热", sum(1 for d in HOT_DATA if 300 <= d["hot"] <= 399), ORANGE),
        ("200-299 中热", sum(1 for d in HOT_DATA if 200 <= d["hot"] <= 299), YELLOW),
        ("100-199 低热", sum(1 for d in HOT_DATA if 100 <= d["hot"] <= 199), GREEN),
        ("<100 微热", sum(1 for d in HOT_DATA if d["hot"] < 100), BLUE),
    ]
    max_range = max(r[1] for r in range_data) if range_data else 1

    bar_area_x = 200
    bar_area_w = W - 280
    bar_h = 36
    bar_gap = 14

    for i, (label, cnt, color) in enumerate(range_data):
        ry = y + i * (bar_h + bar_gap)
        # 标签
        draw.text((50, ry + 6), label, fill=TEXT_WHITE, font=fonts["card_text"])
        # 背景条
        draw_rounded_rect(draw, (bar_area_x, ry, bar_area_x + bar_area_w, ry + bar_h),
                          radius=6, fill=(25, 35, 55))
        # 填充条
        if cnt > 0:
            fill_w = max(20, int(bar_area_w * cnt / max_range))
            draw_rounded_rect(draw, (bar_area_x, ry, bar_area_x + fill_w, ry + bar_h),
                              radius=6, fill=color)
        # 数值
        val_t = f"{cnt} 条"
        draw.text((bar_area_x + bar_area_w + 16, ry + 6), val_t, fill=TEXT_WHITE, font=fonts["card_text"])

    # 底部
    footer = "澎湃新闻24h热榜可视化 · 数据仅供学习研究使用"
    fw = draw.textlength(footer, font=fonts["small"])
    draw.text(((W - fw) // 2, H - 40), footer, fill=TEXT_DIM, font=fonts["small"])

    path = OUTPUT_DIR / "图5_热榜数据摘要信息图.jpg"
    img.save(str(path), "JPEG", quality=95)
    print(f"[图5] 已保存: {path} ({W}x{H})")
    return path


# ============================================================
# 图6：热榜TOP5横向展示卡片
# ============================================================
def generate_chart6_top5():
    """图6：TOP5新闻横向卡片展示"""
    W, H = 1200, 750
    img = Image.new("RGB", (W, H), BG_DARK)
    draw = ImageDraw.Draw(img)

    fonts = {
        "logo": get_font(40, True),
        "title": get_font(22, True),
        "text": get_font(16),
        "small": get_font(13),
        "rank_big": get_font(72, True),
        "hot": get_font(28, True),
        "hot_label": get_font(14),
    }

    # 标题
    y = 30
    title = "澎湃新闻24h热榜 · TOP 5 焦点新闻"
    tw = draw.textlength(title, font=fonts["logo"])
    draw.text(((W - tw) // 2, y), title, fill=TEXT_WHITE, font=fonts["logo"])
    y += 55
    sub = "数据来源：thepaper.cn  |  抓取时间：2026年6月17日"
    sw = draw.textlength(sub, font=fonts["small"])
    draw.text(((W - sw) // 2, y), sub, fill=TEXT_GRAY, font=fonts["small"])

    y += 50
    top5 = HOT_DATA[:5]
    rank_colors = [RED, ORANGE, YELLOW, BLUE, GREEN]

    card_w = 190
    card_h = 400
    gap = 30
    total_w = len(top5) * card_w + (len(top5) - 1) * gap
    start_x = (W - total_w) // 2

    for i, item in enumerate(top5):
        cx = start_x + i * (card_w + gap)
        color = rank_colors[i]

        # 卡片背景
        draw_rounded_rect(draw, (cx, y, cx + card_w, y + card_h), radius=16,
                          fill=BG_MID, outline=color, width=2)

        # 排名圈
        circle_cx = cx + card_w // 2
        circle_cy = y + 55
        draw.ellipse([circle_cx - 40, circle_cy - 40, circle_cx + 40, circle_cy + 40],
                     fill=color, outline=None)
        rw = draw.textlength(str(i + 1), font=fonts["rank_big"])
        draw.text((circle_cx - rw // 2, circle_cy - 36), str(i + 1),
                  fill=(255, 255, 255) if i < 2 else (20, 20, 20) if i == 2 else (255, 255, 255),
                  font=fonts["rank_big"])

        # 热度值
        cy2 = y + 140
        hot_t = str(item["hot"])
        hw = draw.textlength(hot_t, font=fonts["hot"])
        draw.text((cx + (card_w - hw) // 2, cy2), hot_t, fill=color, font=fonts["hot"])
        lab = "热度值"
        lw = draw.textlength(lab, font=fonts["hot_label"])
        draw.text((cx + (card_w - lw) // 2, cy2 + 36), lab, fill=TEXT_GRAY, font=fonts["hot_label"])

        # 分隔线
        draw.line([(cx + 20, cy2 + 60), (cx + card_w - 20, cy2 + 60)], fill=BORDER, width=1)

        # 标题（换行显示）
        title_text = item["title"]
        ty = cy2 + 80
        max_title_w = card_w - 24
        # 简单换行
        lines = []
        current_line = ""
        for ch in title_text:
            test_line = current_line + ch
            if draw.textlength(test_line, font=fonts["text"]) > max_title_w:
                if current_line:
                    lines.append(current_line)
                current_line = ch
            else:
                current_line = test_line
        if current_line:
            lines.append(current_line)

        for j, line in enumerate(lines[:6]):  # 最多6行
            lw2 = draw.textlength(line, font=fonts["text"])
            draw.text((cx + (card_w - lw2) // 2, ty + j * 24), line, fill=TEXT_WHITE, font=fonts["text"])

    # 底部
    footer = "澎湃新闻24h热榜可视化 · 数据仅供学习研究使用"
    fw = draw.textlength(footer, font=fonts["small"])
    draw.text(((W - fw) // 2, H - 40), footer, fill=TEXT_DIM, font=fonts["small"])

    path = OUTPUT_DIR / "图6_TOP5焦点新闻卡片.jpg"
    img.save(str(path), "JPEG", quality=95)
    print(f"[图6] 已保存: {path} ({W}x{H})")
    return path


# ============================================================
# 主函数
# ============================================================
def main():
    print("=" * 60)
    print("  澎湃新闻24h热榜 - 多张可视化图片生成器")
    print("=" * 60)
    print(f"  输出目录: {OUTPUT_DIR}")
    print(f"  数据条目: {len(HOT_DATA)} 条")
    print("=" * 60)

    # 确保输出目录存在
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 生成所有图片
    paths = []
    paths.append(generate_chart1_ranking())
    paths.append(generate_chart2_pie())
    paths.append(generate_chart3_trend())
    paths.append(generate_chart4_category())
    paths.append(generate_chart5_summary())
    paths.append(generate_chart6_top5())

    print("\n" + "=" * 60)
    print("  生成完成！共生成 6 张可视化图片：")
    print("=" * 60)
    for i, p in enumerate(paths, 1):
        size_kb = os.path.getsize(p) / 1024
        print(f"  {i}. {p.name} ({size_kb:.1f} KB)")
    print("=" * 60)
    print(f"\n所有图片已保存至: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
