#!/usr/bin/env python3
"""生成澎湃新闻24h热榜可视化效果图 (JPG)"""

from PIL import Image, ImageDraw, ImageFont
import os
from pathlib import Path

# ==================== 热榜数据 ====================
HOT_DATA = [
    {"title": "刚完赛就被勒令离开美国！伊朗队主帅抱怨球队在世界杯受压迫", "hot": 476},
    {"title": "特朗普大发雷霆后，内塔尼亚胡回应：以军不撤", "hot": 383},
    {"title": ""成都27岁女子遇害案"二审维持原判：梁某滢死缓", "hot": 341},
    {"title": "lululemon向公众及朱一龙道歉：未能在前期充分识别潜在争议", "hot": 312},
    {"title": "黑龙江省纪委副书记、省监委副主任姜宏伟任上被查", "hot": 308},
    {"title": "上海链家通报调查细节：未吃差价！已主动联系主管部门指导", "hot": 287},
    {"title": "梅西第200场倒计时，阿根廷开始一个国家的告别", "hot": 282},
    {"title": "伊朗2比2新西兰，本届世界杯"亚洲球队"保持不败", "hot": 273},
    {"title": "新任国防部新闻发言人陈曦亮相", "hot": 270},
    {"title": "欧盟指控中方"训练俄军事人员在乌作战"，外交部：污蔑抹黑", "hot": 199},
    {"title": "山姆中国更换董事长：会员店业态总裁刘鹏接任", "hot": 196},
    {"title": "成都"27岁王紫雅遇害案"二审上午开庭", "hot": 181},
    {"title": "特朗普称美伊协议谈判进入第二阶段", "hot": 163},
    {"title": "深观察｜办好人民满意的教育：从"有学上"到"上好学"", "hot": 148},
    {"title": "伊朗队主帅：球队突然被勒令立即离开美国", "hot": 113},
    {"title": "青海海西州地震已致1人遇难、4人受伤", "hot": 87},
    {"title": "马上评｜在影院看世界杯，解锁的不只是看球新体验", "hot": 86},
    {"title": "观察｜美以伊战争结束的开始", "hot": 80},
    {"title": "江苏省副省长陈忠伟任江苏省委常委", "hot": 74},
    {"title": ""成都27岁女子遇害案"二审今日开庭", "hot": 30},
]

# ==================== 颜色常量 ====================
BG_COLOR = (10, 14, 23)
CARD_BG = (20, 27, 45)
CARD_BORDER = (42, 53, 85)
TEXT_WHITE = (224, 230, 240)
TEXT_GRAY = (122, 139, 168)
TEXT_DIM = (80, 96, 118)
HOT_RED = (255, 45, 45)
HOT_ORANGE = (255, 107, 53)
HOT_YELLOW = (255, 165, 64)
HOT_BLUE = (59, 130, 246)
HOT_GRAY = (122, 139, 168)
BAR_BG = (30, 42, 66)
RANK_TOP1 = (255, 45, 45)
RANK_TOP2 = (255, 107, 53)
RANK_TOP3 = (255, 200, 64)
RANK_NORMAL = (30, 42, 66)
PIE_COLORS = [HOT_RED, HOT_ORANGE, HOT_YELLOW, HOT_BLUE, HOT_GRAY]


def get_font(size, bold=False):
    """尝试加载中文字体"""
    candidates = [
        "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/msyhbd.ttc",
        "C:/Windows/Fonts/simhei.ttf",
        "C:/Windows/Fonts/simsun.ttc",
    ]
    for fp in candidates:
        if os.path.exists(fp):
            try:
                return ImageFont.truetype(fp, size)
            except Exception:
                continue
    return ImageFont.load_default()


def truncate_text(draw, text, font, max_width):
    """截断文本以适应最大宽度"""
    if draw.textlength(text, font=font) <= max_width:
        return text
    while text and draw.textlength(text + "...", font=font) > max_width:
        text = text[:-1]
    return text + "..."


def draw_rounded_rect(draw, xy, radius, fill=None, outline=None, width=1):
    """绘制圆角矩形"""
    x1, y1, x2, y2 = xy
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def draw_bar_chart(draw, data, start_y, width, fonts):
    """绘制热度排行条形图"""
    font_title = fonts["title"]
    font_text = fonts["text"]
    font_small = fonts["small"]
    font_rank = fonts["rank"]

    max_hot = max(d["hot"] for d in data)
    row_height = 48
    margin_left = 40
    margin_right = 100
    bar_area_width = width - margin_left - margin_right - 80

    # 区域标题
    draw.text((margin_left, start_y), "热度排行 TOP 20", fill=HOT_ORANGE, font=font_title)
    draw.rectangle((margin_left - 12, start_y + 2, margin_left - 6, start_y + 22), fill=HOT_ORANGE)
    start_y += 40

    for i, item in enumerate(data):
        y = start_y + i * (row_height + 6)
        rank = i + 1
        hot = item["hot"]
        pct = hot / max_hot

        # 行背景
        draw_rounded_rect(draw, (margin_left - 8, y, width - 40, y + row_height),
                          radius=8, fill=CARD_BG, outline=CARD_BORDER, width=1)

        # 排名徽章
        if rank == 1:
            badge_color = RANK_TOP1
        elif rank == 2:
            badge_color = RANK_TOP2
        elif rank == 3:
            badge_color = RANK_TOP3
        else:
            badge_color = RANK_NORMAL

        badge_x = margin_left + 4
        badge_y = y + 8
        draw_rounded_rect(draw, (badge_x, badge_y, badge_x + 32, badge_y + 32),
                          radius=6, fill=badge_color)
        rank_text_color = (255, 255, 255) if rank <= 2 else (26, 26, 26) if rank == 3 else TEXT_GRAY
        draw.text((badge_x + 16 - draw.textlength(str(rank), font=font_rank) / 2, badge_y + 4),
                  str(rank), fill=rank_text_color, font=font_rank)

        # 标题
        text_x = margin_left + 46
        max_title_w = bar_area_width - 20
        title = truncate_text(draw, item["title"], font_text, max_title_w)
        draw.text((text_x, y + 6), title, fill=TEXT_WHITE, font=font_text)

        # 进度条
        bar_x = text_x
        bar_y = y + 30
        bar_w = bar_area_width
        bar_h = 8
        draw_rounded_rect(draw, (bar_x, bar_y, bar_x + bar_w, bar_y + bar_h),
                          radius=4, fill=BAR_BG)
        fill_w = max(4, int(bar_w * pct))
        # 渐变色：高热度红色->低热度蓝色
        if hot >= 300:
            bar_color = HOT_RED
        elif hot >= 200:
            bar_color = HOT_ORANGE
        elif hot >= 100:
            bar_color = HOT_YELLOW
        else:
            bar_color = HOT_BLUE
        draw_rounded_rect(draw, (bar_x, bar_y, bar_x + fill_w, bar_y + bar_h),
                          radius=4, fill=bar_color)

        # 热度值
        hot_x = width - 40 - draw.textlength(str(hot), font=font_text) - 4
        draw.text((hot_x, y + 12), str(hot), fill=HOT_ORANGE, font=font_text)

    return start_y + len(data) * (row_height + 6)


def draw_pie_chart(draw, center_x, center_y, outer_r, inner_r, data, colors):
    """绘制环形饼图"""
    total = sum(data)
    start_angle = -90

    for i, count in enumerate(data):
        if count == 0:
            continue
        sweep = (count / total) * 360
        draw.pieslice(
            [center_x - outer_r, center_y - outer_r,
             center_x + outer_r, center_y + outer_r],
            start_angle, start_angle + sweep,
            fill=colors[i]
        )
        start_angle += sweep

    # 挖出中心圆
    draw.ellipse(
        [center_x - inner_r, center_y - inner_r,
         center_x + inner_r, center_y + inner_r],
        fill=BG_COLOR
    )


def main():
    # 画布尺寸
    W = 1000
    row_h = 54
    bar_section_h = 40 + 20 * (row_h + 6) + 40
    pie_section_h = 280
    total_h = 160 + bar_section_h + pie_section_h + 120

    img = Image.new("RGB", (W, total_h), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # 字体
    fonts = {
        "logo": get_font(36, bold=True),
        "title": get_font(20, bold=True),
        "subtitle": get_font(14),
        "text": get_font(15),
        "small": get_font(12),
        "rank": get_font(18, bold=True),
        "stat_num": get_font(28, bold=True),
        "stat_label": get_font(12),
        "pie_center": get_font(26, bold=True),
        "pie_center_sub": get_font(12),
        "legend": get_font(14),
    }

    # ========== 标题区 ==========
    y = 30
    draw.text((W // 2 - draw.textlength("澎湃新闻 · 24h热榜", font=fonts["logo"]) // 2, y),
              "澎湃新闻 · 24h热榜", fill=TEXT_WHITE, font=fonts["logo"])
    y += 50
    sub = "数据来源：thepaper.cn  |  抓取时间：2026-06-17  |  共20条热榜新闻"
    draw.text((W // 2 - draw.textlength(sub, font=fonts["subtitle"]) // 2, y),
              sub, fill=TEXT_GRAY, font=fonts["subtitle"])

    # ========== 统计卡片 ==========
    y += 40
    max_hot = max(d["hot"] for d in HOT_DATA)
    avg_hot = round(sum(d["hot"] for d in HOT_DATA) / len(HOT_DATA))
    over200 = sum(1 for d in HOT_DATA if d["hot"] >= 200)

    stats = [
        ("20", "热榜条目", HOT_ORANGE),
        (str(max_hot), "最高热度", HOT_RED),
        (str(avg_hot), "平均热度", HOT_YELLOW),
        (str(over200), "热度≥200", HOT_BLUE),
    ]

    card_w = 180
    card_h = 70
    gap = 20
    total_cards_w = len(stats) * card_w + (len(stats) - 1) * gap
    start_x = (W - total_cards_w) // 2

    for i, (num, label, color) in enumerate(stats):
        cx = start_x + i * (card_w + gap)
        draw_rounded_rect(draw, (cx, y, cx + card_w, y + card_h),
                          radius=10, fill=CARD_BG, outline=CARD_BORDER, width=1)
        num_w = draw.textlength(num, font=fonts["stat_num"])
        draw.text((cx + (card_w - num_w) // 2, y + 10), num, fill=color, font=fonts["stat_num"])
        label_w = draw.textlength(label, font=fonts["stat_label"])
        draw.text((cx + (card_w - label_w) // 2, y + 46), label, fill=TEXT_GRAY, font=fonts["stat_label"])

    # ========== 条形图 ==========
    y += card_h + 30
    bar_end_y = draw_bar_chart(draw, HOT_DATA, y, W, fonts)

    # ========== 热度分布饼图 ==========
    y = bar_end_y + 10
    draw.text((40, y), "热度区间分布", fill=HOT_YELLOW, font=fonts["title"])
    draw.rectangle((28, y + 2, 34, y + 22), fill=HOT_YELLOW)
    y += 40

    # 统计各区间
    ranges = [
        ("400+ 极热", 400, None),
        ("200-399 高热", 200, 399),
        ("100-199 中热", 100, 199),
        ("50-99 低热", 50, 99),
        ("<50 微热", 0, 49),
    ]
    range_counts = []
    for label, lo, hi in ranges:
        if hi:
            cnt = sum(1 for d in HOT_DATA if lo <= d["hot"] <= hi)
        else:
            cnt = sum(1 for d in HOT_DATA if d["hot"] >= lo)
        range_counts.append(cnt)

    total_count = sum(range_counts)

    # 画饼图
    pie_cx = 160
    pie_cy = y + 110
    draw_pie_chart(draw, pie_cx, pie_cy, 90, 52, range_counts, PIE_COLORS)

    # 饼图中心文字
    draw.text((pie_cx - draw.textlength("20", font=fonts["pie_center"]) // 2, pie_cy - 14),
              "20", fill=TEXT_WHITE, font=fonts["pie_center"])
    draw.text((pie_cx - draw.textlength("热榜条目", font=fonts["pie_center_sub"]) // 2, pie_cy + 16),
              "热榜条目", fill=TEXT_GRAY, font=fonts["pie_center_sub"])

    # 图例
    legend_x = 300
    legend_y = y + 20
    for i, ((label, _, _), cnt) in enumerate(zip(ranges, range_counts)):
        pct = (cnt / total_count * 100) if total_count > 0 else 0
        ly = legend_y + i * 42
        draw_rounded_rect(draw, (legend_x, ly, legend_x + 620, ly + 34),
                          radius=6, fill=CARD_BG, outline=CARD_BORDER, width=1)
        # 色块
        draw_rounded_rect(draw, (legend_x + 12, ly + 8, legend_x + 26, ly + 26),
                          radius=3, fill=PIE_COLORS[i])
        draw.text((legend_x + 36, ly + 8), label, fill=TEXT_WHITE, font=fonts["legend"])
        val_text = f"{cnt}条 ({pct:.0f}%)"
        draw.text((legend_x + 560, ly + 8), val_text, fill=TEXT_GRAY, font=fonts["legend"])

    # ========== 底部 ==========
    footer_y = pie_cy + 120
    footer = "澎湃新闻24h热榜可视化  |  数据仅供学习研究使用  |  目标网页：https://m.thepaper.cn/htmlstatic"
    draw.text((W // 2 - draw.textlength(footer, font=fonts["small"]) // 2, footer_y),
              footer, fill=TEXT_DIM, font=fonts["small"])

    # 保存
    output_path = Path(os.path.expanduser("~")) / "Desktop" / "澎湃热榜数据" / "澎湃24h热榜可视化.jpg"
    img.save(str(output_path), "JPEG", quality=95)
    print(f"可视化效果图已保存: {output_path}")
    print(f"文件大小: {os.path.getsize(output_path)} 字节")
    print(f"图片尺寸: {W} x {total_h}")


if __name__ == "__main__":
    main()