#!/usr/bin/env python3
"""
澎湃新闻24h热榜数据爬虫
功能：反爬适配、数据清洗、本地文件存储
目标网站：https://m.thepaper.cn/htmlstatic
"""

import requests
import json
import time
import csv
import os
import re
from datetime import datetime
from pathlib import Path

# ==================== 配置区 ====================

# 输出目录 - 桌面
DESKTOP_DIR = Path(os.path.expanduser("~")) / "Desktop"
OUTPUT_DIR = DESKTOP_DIR / "澎湃热榜数据"

# 目标URL
TARGET_URL = "https://m.thepaper.cn/htmlstatic"

# API端点（多策略）
API_ENDPOINTS = {
    # 策略1: 澎湃新闻官方热榜API（移动端）
    "official_hot_rank": "https://www.thepaper.cn//load_hot_top.jsp",
    # 策略2: 澎湃新闻缓存API
    "cache_api": "https://cache.thepaper.cn/content/www/hotNewsRank",
    # 策略3: 澎湃新闻移动端Next.js数据路由（推测）
    "nextjs_data": "https://m.thepaper.cn/htmlstatic",
}

# 反爬请求头池
HEADERS_POOL = [
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://www.thepaper.cn/",
        "Connection": "keep-alive",
        "Cache-Control": "no-cache",
    },
    {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Referer": "https://m.thepaper.cn/",
        "Connection": "keep-alive",
    },
    {
        "User-Agent": "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Mobile Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Referer": "https://m.thepaper.cn/",
        "Connection": "keep-alive",
    },
]

# 请求超时与重试配置
REQUEST_TIMEOUT = 15  # 秒
MAX_RETRIES = 3
RETRY_DELAY = 3  # 重试间隔秒
REQUEST_DELAY = 2  # 请求间隔秒（反爬限速）


# ==================== 反爬适配模块 ====================

class AntiCrawlAdapter:
    """反爬适配器：处理请求头轮换、重试、限速、Cookie管理"""

    def __init__(self):
        self.session = requests.Session()
        self.header_index = 0
        self.retry_count = 0

    def _rotate_headers(self):
        """轮换请求头，模拟不同设备访问"""
        headers = HEADERS_POOL[self.header_index % len(HEADERS_POOL)]
        self.header_index += 1
        return headers

    def _add_timestamp_param(self, params=None):
        """添加时间戳参数，防止缓存拦截"""
        if params is None:
            params = {}
        params["_"] = int(time.time() * 1000)
        return params

    def request_with_retry(self, url, method="GET", params=None, data=None):
        """
        带重试机制的请求方法
        - 自动轮换请求头
        - 添加时间戳防缓存
        - 失败后自动重试，逐步增加延迟
        - 限速：每次请求间增加延迟
        """
        params = self._add_timestamp_param(params)
        headers = self._rotate_headers()

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                # 限速：请求间隔
                if attempt > 1:
                    delay = RETRY_DELAY * attempt  # 逐步增加重试延迟
                    print(f"  [重试] 第{attempt}次尝试，等待{delay}秒...")
                    time.sleep(delay)
                else:
                    time.sleep(REQUEST_DELAY)

                print(f"  [请求] {method} {url} (尝试 {attempt}/{MAX_RETRIES})")

                if method.upper() == "GET":
                    resp = self.session.get(
                        url, params=params, headers=headers,
                        timeout=REQUEST_TIMEOUT, allow_redirects=True
                    )
                else:
                    resp = self.session.post(
                        url, params=params, data=data, headers=headers,
                        timeout=REQUEST_TIMEOUT, allow_redirects=True
                    )

                # 检查响应状态
                if resp.status_code == 200:
                    print(f"  [成功] 状态码 200，数据长度 {len(resp.content)} 字节")
                    return resp
                elif resp.status_code == 403:
                    print(f"  [反爬] 403 Forbidden，可能被识别为爬虫，切换策略...")
                    # 切换请求头再试
                    headers = self._rotate_headers()
                    continue
                elif resp.status_code == 404:
                    print(f"  [缺失] 404 Not Found，接口可能已变更")
                    # 404通常不需要重试，直接返回
                    return resp
                elif resp.status_code == 429:
                    print(f"  [限速] 429 Too Many Requests，等待更长时间...")
                    time.sleep(30)
                    continue
                else:
                    print(f"  [异常] 状态码 {resp.status_code}")
                    continue

            except requests.exceptions.Timeout:
                print(f"  [超时] 请求超时 ({REQUEST_TIMEOUT}s)")
                continue
            except requests.exceptions.ConnectionError as e:
                print(f"  [连接] 连接错误: {e}")
                continue
            except requests.exceptions.RequestException as e:
                print(f"  [异常] 请求异常: {e}")
                continue

        print(f"  [失败] 所有重试均未成功")
        return None


# ==================== 数据抓取模块 ====================

class ThePaperHotRankScraper:
    """澎湃新闻24h热榜爬虫核心"""

    def __init__(self):
        self.adapter = AntiCrawlAdapter()
        self.raw_data = None
        self.cleaned_data = []

    def fetch_official_api(self):
        """策略1: 尝试官方热榜API"""
        print("\n[策略1] 尝试官方热榜API...")
        url = API_ENDPOINTS["official_hot_rank"]
        params = {"hotIds": "1,2,3,4,5,6,7,8,9,10"}
        resp = self.adapter.request_with_retry(url, params=params)
        if resp and resp.status_code == 200:
            try:
                data = resp.json()
                if isinstance(data, list) and len(data) > 0:
                    print(f"  [获取] 成功获取 {len(data)} 条热榜数据")
                    return data
            except json.JSONDecodeError:
                print(f"  [解析] JSON解析失败，尝试HTML解析...")
                return self._parse_html_response(resp.text)
        print("  [结果] 官方API不可用，切换策略")
        return None

    def fetch_cache_api(self):
        """策略2: 尝试缓存API"""
        print("\n[策略2] 尝试缓存API...")
        url = API_ENDPOINTS["cache_api"]
        resp = self.adapter.request_with_retry(url)
        if resp and resp.status_code == 200:
            try:
                data = resp.json()
                if isinstance(data, list) and len(data) > 0:
                    print(f"  [获取] 成功获取 {len(data)} 条数据")
                    return data
                elif isinstance(data, dict) and "data" in data:
                    items = data.get("data", {}).get("hotNews", data.get("data", []))
                    if items:
                        print(f"  [获取] 成功获取 {len(items)} 条数据")
                        return items
            except json.JSONDecodeError:
                return self._parse_html_response(resp.text)
        print("  [结果] 缓存API不可用，切换策略")
        return None

    def fetch_nextjs_page(self):
        """策略3: 尝试Next.js页面渲染数据"""
        print("\n[策略3] 尝试移动端页面数据提取...")
        url = API_ENDPOINTS["nextjs_data"]
        resp = self.adapter.request_with_retry(url)
        if resp and resp.status_code == 200:
            return self._parse_nextjs_page(resp.text)
        print("  [结果] 移动端页面不可用，切换策略")
        return None

    def _parse_html_response(self, html_text):
        """从HTML响应中提取热榜数据"""
        # 尝试提取 __NEXT_DATA__ 中的JSON数据
        next_data_match = re.search(
            r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>',
            html_text, re.DOTALL
        )
        if next_data_match:
            try:
                next_data = json.loads(next_data_match.group(1))
                page_props = next_data.get("props", {}).get("pageProps", {})
                hot_list = page_props.get("hotList", page_props.get("hotNews", []))
                if hot_list:
                    return hot_list
            except json.JSONDecodeError:
                pass

        # 尝试提取HTML中的热榜条目
        items = []
        rank_pattern = re.findall(
            r'class="[^"]*rank[^"]*"[^>]*>(\d+)</[^>]+>|'
            r'class="[^"]*title[^"]*"[^>]*>([^<]+)</[^>]+>|'
            r'newsDetail_forward_(\d+)',
            html_text
        )
        if items:
            return items

        return None

    def _parse_nextjs_page(self, html_text):
        """从Next.js页面中提取数据"""
        # 提取 __NEXT_DATA__
        match = re.search(
            r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>',
            html_text, re.DOTALL
        )
        if match:
            try:
                data = json.loads(match.group(1))
                props = data.get("props", {}).get("pageProps", {})
                # 尝试多种可能的字段名
                for key in ["hotList", "hotNews", "rankList", "newsList", "list"]:
                    if key in props:
                        print(f"  [提取] 从__NEXT_DATA__中找到 {key} 字段，共 {len(props[key])} 条")
                        return props[key]
                # 递归搜索
                result = self._deep_search_data(props, ["hot", "rank", "news"])
                if result:
                    return result
            except json.JSONDecodeError:
                pass

        # 尝试提取内嵌的JSON数据块
        json_blocks = re.findall(r'\{["\'][\w]+["\']:\s*\[', html_text)
        for block_start in json_blocks:
            try:
                # 找到完整的JSON块
                start_idx = html_text.index(block_start)
                end_idx = self._find_json_end(html_text, start_idx)
                json_str = html_text[start_idx:end_idx]
                data = json.loads(json_str)
                if isinstance(data, dict):
                    for key in data:
                        if isinstance(data[key], list) and len(data[key]) > 3:
                            return data[key]
            except (json.JSONDecodeError, ValueError):
                continue

        print("  [结果] 未从Next.js页面中提取到热榜数据")
        return None

    def _deep_search_data(self, obj, keywords, depth=5):
        """递归搜索包含关键词的数据"""
        if depth <= 0 or not isinstance(obj, dict):
            return None
        for key, value in obj.items():
            if any(kw in key.lower() for kw in keywords):
                if isinstance(value, list) and len(value) > 0:
                    return value
            if isinstance(value, dict):
                result = self._deep_search_data(value, keywords, depth - 1)
                if result:
                    return result
        return None

    def _find_json_end(self, text, start):
        """找到JSON块的结束位置"""
        brace_count = 0
        for i in range(start, len(text)):
            if text[i] == '{':
                brace_count += 1
            elif text[i] == '}':
                brace_count -= 1
                if brace_count == 0:
                    return i + 1
        return len(text)

    def fetch_data(self):
        """执行多策略数据抓取"""
        print("=" * 60)
        print("澎湃新闻24h热榜数据爬虫 - 启动")
        print("=" * 60)
        print(f"目标网站: {TARGET_URL}")
        print(f"抓取时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)

        # 按优先级尝试各策略
        strategies = [
            ("官方热榜API", self.fetch_official_api),
            ("缓存API", self.fetch_cache_api),
            ("移动端页面", self.fetch_nextjs_page),
        ]

        for name, strategy in strategies:
            result = strategy()
            if result and len(result) > 0:
                print(f"\n[最终] 使用策略 [{name}] 成功获取数据")
                self.raw_data = result
                return True

        # 所有策略失败时，使用Selenium渲染方案
        print("\n[降级] 所有API策略失败，尝试Selenium浏览器渲染...")
        selenium_result = self._fetch_with_selenium()
        if selenium_result:
            self.raw_data = selenium_result
            return True

        print("\n[失败] 所有策略均未能获取数据")
        return False

    def _fetch_with_selenium(self):
        """使用Selenium浏览器渲染获取数据（降级方案）"""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC

            print("  [Selenium] 正在启动Chrome浏览器...")
            options = Options()
            options.add_argument("--headless")
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--window-size=1920,1080")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option("useAutomationExtension", False)

            # 反爬：设置navigator.webdriver为undefined
            options.add_argument("--disable-blink-features=AutomationControlled")

            try:
                driver = webdriver.Chrome(options=options)
            except Exception:
                # Chrome驱动未安装，尝试自动检测
                print("  [Selenium] Chrome驱动未找到，跳过此策略")
                return None

            # 反爬：注入JS隐藏自动化特征
            driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            })

            driver.get(TARGET_URL)
            print("  [Selenium] 页面加载完成，等待数据渲染...")
            time.sleep(5)  # 等待数据渲染

            # 尝试提取页面中的热榜数据
            try:
                # 查找热榜列表元素
                items = driver.find_elements(By.CSS_SELECTOR, "[class*='rank'], [class*='hot'], [class*='item']")
                if not items:
                    items = driver.find_elements(By.CSS_SELECTOR, "li, .news-item")

                results = []
                for idx, item in enumerate(items[:20], 1):
                    title_el = item.find_element(By.CSS_SELECTOR, "[class*='title'], a, h3, h4")
                    title = title_el.text.strip() if title_el else ""
                    link = title_el.get_attribute("href") if title_el else ""
                    results.append({
                        "rank": idx,
                        "cont_title": title,
                        "cont_id": link,
                        "total": 0,
                    })

                driver.quit()
                if results:
                    print(f"  [Selenium] 成功获取 {len(results)} 条数据")
                    return results
            except Exception as e:
                print(f"  [Selenium] 数据提取失败: {e}")
                driver.quit()

        except ImportError:
            print("  [Selenium] selenium库未安装，跳过此策略")
        except Exception as e:
            print(f"  [Selenium] 异常: {e}")

        return None


# ==================== 数据清洗模块 ====================

class DataCleaner:
    """数据清洗与标准化"""

    # 字段映射表（适配不同API的数据结构）
    FIELD_MAPPINGS = {
        # 官方API字段 -> 标准字段
        "cont_title": "title",
        "contId": "title_id",
        "cont_id": "title_id",
        "total": "hot_value",
        "name": "title",
        "pubTime": "publish_time",
        "rank": "rank",
        "hotScore": "hot_value",
        "views": "hot_value",
        "url": "url",
    }

    def clean(self, raw_data):
        """清洗原始数据，输出标准化格式"""
        print("\n[清洗] 开始数据清洗...")
        cleaned = []

        if not raw_data:
            print("  [清洗] 无原始数据可清洗")
            return cleaned

        for idx, item in enumerate(raw_data, 1):
            if not isinstance(item, dict):
                continue

            # 标准化字段名
            standardized = {}
            for src_key, dst_key in self.FIELD_MAPPINGS.items():
                if src_key in item:
                    standardized[dst_key] = item[src_key]

            # 直接匹配标准字段
            for key in ["title", "rank", "hot_value", "url", "publish_time", "title_id"]:
                if key in item and key not in standardized:
                    standardized[key] = item[key]

            # 确保必有字段
            standardized["rank"] = standardized.get("rank", idx)

            # 清洗标题
            title = standardized.get("title", "")
            if not title and "cont_title" in item:
                title = item["cont_title"]
            standardized["title"] = self._clean_title(title)

            # 构建URL
            if not standardized.get("url"):
                title_id = standardized.get("title_id") or item.get("contId") or item.get("cont_id")
                if title_id:
                    # 如果title_id是完整URL则直接使用
                    if str(title_id).startswith("http"):
                        standardized["url"] = str(title_id)
                    else:
                        standardized["url"] = f"https://www.thepaper.cn/newsDetail_forward_{title_id}"

            # 清洗热度值
            hot_val = standardized.get("hot_value") or item.get("total") or item.get("views") or 0
            standardized["hot_value"] = self._clean_hot_value(hot_val)

            # 清洗发布时间
            pub_time = standardized.get("publish_time") or item.get("pubTime") or ""
            standardized["publish_time"] = self._clean_time(pub_time)

            # 只保留有效标题的条目
            if standardized["title"]:
                cleaned.append(standardized)

        # 按排名排序
        cleaned.sort(key=lambda x: int(x.get("rank", 999)))

        # 重新编号排名（确保连续）
        for idx, item in enumerate(cleaned, 1):
            item["rank"] = idx

        print(f"  [清洗] 清洗完成：原始 {len(raw_data)} 条 -> 有效 {len(cleaned)} 条")
        return cleaned

    def _clean_title(self, title):
        """清洗标题文本"""
        if not title:
            return ""
        title = str(title).strip()
        # 去除HTML标签
        title = re.sub(r'<[^>]+>', '', title)
        # 去除多余空白
        title = re.sub(r'\s+', ' ', title)
        # 去除特殊字符
        title = title.replace('\n', '').replace('\r', '').replace('\t', '')
        return title

    def _clean_hot_value(self, val):
        """清洗热度值，确保为整数"""
        try:
            return int(val)
        except (ValueError, TypeError):
            # 处理如"1.2万"这种格式
            if isinstance(val, str):
                val = val.replace(",", "").replace(",", "")
                match = re.search(r'([\d.]+)(万)?', val)
                if match:
                    num = float(match.group(1))
                    if match.group(2) == "万":
                        num *= 10000
                    return int(num)
            return 0

    def _clean_time(self, time_str):
        """清洗时间格式"""
        if not time_str:
            return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        time_str = str(time_str).strip()
        # 尝试多种时间格式
        formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S",
            "%Y/%m/%d %H:%M:%S",
            "%Y年%m月%d日 %H:%M",
        ]
        for fmt in formats:
            try:
                dt = datetime.strptime(time_str, fmt)
                return dt.strftime("%Y-%m-%d %H:%M:%S")
            except ValueError:
                continue
        return time_str


# ==================== 数据存储模块 ====================

class DataStorage:
    """本地文件存储：JSON + CSV"""

    def __init__(self, output_dir=None):
        self.output_dir = Path(output_dir) if output_dir else OUTPUT_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    def save_json(self, data, filename=None):
        """保存为JSON文件"""
        if not filename:
            filename = f"澎湃24h热榜_{self.timestamp}.json"
        filepath = self.output_dir / filename

        output = {
            "source": "澎湃新闻24h热榜",
            "target_url": TARGET_URL,
            "fetch_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_count": len(data),
            "data": data,
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

        print(f"  [存储] JSON文件已保存: {filepath}")
        print(f"  [存储] 文件大小: {os.path.getsize(filepath)} 字节")
        return filepath

    def save_csv(self, data, filename=None):
        """保存为CSV文件"""
        if not filename:
            filename = f"澎湃24h热榜_{self.timestamp}.csv"
        filepath = self.output_dir / filename

        if not data:
            print("  [存储] 无数据可保存为CSV")
            return None

        # CSV字段
        fieldnames = ["rank", "title", "url", "hot_value", "publish_time"]

        with open(filepath, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            for item in data:
                # 确保每个字段都有值
                row = {k: item.get(k, "") for k in fieldnames}
                writer.writerow(row)

        print(f"  [存储] CSV文件已保存: {filepath}")
        print(f"  [存储] 文件大小: {os.path.getsize(filepath)} 字节")
        return filepath

    def save_source_code(self, code_content, filename=None):
        """保存爬虫源代码"""
        if not filename:
            filename = "pengpai_hot_rank_scraper.py"
        filepath = self.output_dir / filename

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(code_content)

        print(f"  [存储] 源代码已保存: {filepath}")
        return filepath

    def save_prompt(self, prompt_text, filename=None):
        """保存完整提示词文本"""
        if not filename:
            filename = "提示词文本.txt"
        filepath = self.output_dir / filename

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(prompt_text)

        print(f"  [存储] 提示词已保存: {filepath}")
        return filepath

    def save_target_url(self, url, filename=None):
        """保存原始目标网页链接"""
        if not filename:
            filename = "目标网页链接.txt"
        filepath = self.output_dir / filename

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"原始目标网页链接:\n{url}\n")
            f.write(f"\n抓取时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        print(f"  [存储] 目标链接已保存: {filepath}")
        return filepath


# ==================== 主程序 ====================

def main():
    print("=" * 60)
    print("  澎湃新闻24h热榜数据爬虫")
    print("  目标: https://m.thepaper.cn/htmlstatic")
    print("=" * 60)

    # 1. 创建各模块实例
    scraper = ThePaperHotRankScraper()
    cleaner = DataCleaner()
    storage = DataStorage()

    # 2. 抓取数据
    success = scraper.fetch_data()

    if not success:
        print("\n[提示] 直接API策略均未成功，尝试使用公开聚合数据源...")
        # 使用公开的热榜聚合API作为最终降级方案
        aggregator_url = "https://apiserver.alcex.cn/daily-hot/thepaper"
        resp = scraper.adapter.request_with_retry(aggregator_url)
        if resp and resp.status_code == 200:
            try:
                agg_data = resp.json()
                # 聚合API的数据结构: {"code": 200, "data": [...]}
                if isinstance(agg_data, dict):
                    items = agg_data.get("data", [])
                    if items:
                        print(f"\n[降级] 通过聚合数据源获取 {len(items)} 条热榜数据")
                        # 转换聚合API字段为内部格式
                        converted = []
                        for item in items:
                            converted.append({
                                "rank": item.get("rank", 0),
                                "title": item.get("title", ""),
                                "url": item.get("url", ""),
                                "hot_value": item.get("hotValue", item.get("views", 0)),
                                "publish_time": item.get("pubTime", item.get("publishTime", "")),
                                "title_id": item.get("contId", item.get("id", "")),
                            })
                        scraper.raw_data = converted
                        success = True
                elif isinstance(agg_data, list):
                    scraper.raw_data = agg_data
                    success = True
            except json.JSONDecodeError:
                pass

    if not success:
        print("\n[错误] 无法获取任何数据，程序终止")
        print("[建议] 请检查网络连接或目标网站是否可访问")
        return

    # 3. 清洗数据
    cleaned_data = cleaner.clean(scraper.raw_data)

    if not cleaned_data:
        print("\n[错误] 数据清洗后无有效数据，程序终止")
        return

    # 4. 打印热榜结果
    print("\n" + "=" * 60)
    print("  澎湃新闻24h热榜 - 数据结果")
    print("=" * 60)
    print(f"{'排名':>4} | {'标题':<40} | {'热度':>8}")
    print("-" * 60)
    for item in cleaned_data:
        title = item.get("title", "")[:38]
        hot = item.get("hot_value", 0)
        rank = item.get("rank", 0)
        print(f"{rank:>4} | {title:<40} | {hot:>8}")
    print("=" * 60)

    # 5. 存储数据
    print("\n[存储] 开始保存数据文件...")
    json_path = storage.save_json(cleaned_data)
    csv_path = storage.save_csv(cleaned_data)

    # 6. 保存源代码
    scraper_file = os.path.abspath(__file__)
    with open(scraper_file, "r", encoding="utf-8") as f:
        code_content = f.read()
    storage.save_source_code(code_content)

    # 7. 保存提示词
    prompt_text = (
        "你是专业Python爬虫工程师，擅长抓取权威平台公开数据，熟练应对各类网站反爬限制、网页解析与数据落地存储。\n"
        "请开发完整可运行的爬虫程序，抓取澎湃新闻24h热榜数据，程序需实现反爬适配、数据清洗、本地文件存储三大核心功能。\n"
        "完成开发后，将原始目标网页链接、完整提示词文本、爬虫源代码文件、爬虫运行导出的数据结果文件统一保存至电脑桌面。\n"
        f"\n目标网页链接: https://m.thepaper.cn/htmlstatic"
    )
    storage.save_prompt(prompt_text)

    # 8. 保存目标URL
    storage.save_target_url(TARGET_URL)

    # 9. 完成报告
    print("\n" + "=" * 60)
    print("  任务完成 - 文件清单")
    print("=" * 60)
    print(f"  输出目录: {storage.output_dir}")
    for f in os.listdir(storage.output_dir):
        filepath = storage.output_dir / f
        size = os.path.getsize(filepath)
        print(f"  - {f} ({size} 字节)")
    print("=" * 60)
    print("\n[完成] 所有文件已保存至桌面「澎湃热榜数据」目录")


if __name__ == "__main__":
    main()