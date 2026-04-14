import tkinter as tk
from tkinter import ttk, messagebox
import requests
from bs4 import BeautifulSoup
import re
import os
from datetime import datetime
import time
import logging
import html2text

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cnblogs_to_hugo.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CnblogsToHugo:
    def __init__(self, root):
        self.root = root
        self.root.title("博客园文章转Hugo工具")
        self.root.geometry("900x600")

        self.articles = []
        self.checkbox_vars = {}

        self.base_url = ""
        self.username = ""

        self.setup_ui()

    def setup_ui(self):
        top_frame = ttk.Frame(self.root, padding="10")
        top_frame.pack(fill=tk.X)

        ttk.Label(top_frame, text="博客园用户名:").pack(side=tk.LEFT)
        self.username_entry = ttk.Entry(top_frame, width=20)
        self.username_entry.pack(side=tk.LEFT, padx=5)
        self.username_entry.insert(0, "")

        ttk.Label(top_frame, text="输出目录:").pack(side=tk.LEFT, padx=(20, 0))
        self.output_entry = ttk.Entry(top_frame, width=30)
        self.output_entry.pack(side=tk.LEFT, padx=5)
        self.output_entry.insert(0, "./hugo_content")

        ttk.Button(top_frame, text="获取文章列表", command=self.fetch_article_list).pack(side=tk.LEFT, padx=5)
        ttk.Button(top_frame, text="全选", command=self.select_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(top_frame, text="反选", command=self.invert_selection).pack(side=tk.LEFT, padx=5)
        ttk.Button(top_frame, text="下载选中文章", command=self.download_articles).pack(side=tk.LEFT, padx=5)

        self.progress = ttk.Label(top_frame, text="")
        self.progress.pack(side=tk.LEFT, padx=10)

        list_frame = ttk.Frame(self.root, padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(list_frame, columns=("selected", "title", "date", "status"), show="headings")
        self.tree.heading("selected", text="选择")
        self.tree.heading("title", text="标题")
        self.tree.heading("date", text="发布日期")
        self.tree.heading("status", text="状态")
        self.tree.column("selected", width=50, anchor="center")
        self.tree.column("title", width=450)
        self.tree.column("date", width=150)
        self.tree.column("status", width=100)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.bind("<Button-1>", self.on_tree_click)

        status_frame = ttk.Frame(self.root, padding="10")
        status_frame.pack(fill=tk.X)
        self.status_label = ttk.Label(status_frame, text="就绪")
        self.status_label.pack(side=tk.LEFT)

    def on_tree_click(self, event):
        region = self.tree.identify_region(event.x, event.y)
        if region == "cell":
            column = self.tree.identify_column(event.x)
            if column == "#1":
                item_id = self.tree.identify_row(event.y)
                if item_id:
                    for i, article in enumerate(self.articles):
                        if article.get("tree_id") == item_id:
                            current_val = self.checkbox_vars[i].get()
                            self.checkbox_vars[i].set(not current_val)
                            self.update_tree_display()
                            break

    def fetch_article_list(self):
        self.username = self.username_entry.get().strip()
        if not self.username:
            messagebox.showwarning("警告", "请输入博客园用户名")
            return

        logger.info(f"开始获取用户 {self.username} 的文章列表")
        self.base_url = f"https://www.cnblogs.com/{self.username}"
        self.articles = []

        for page in range(1, 100):
            self.status_label.config(text=f"正在获取第 {page} 页...")
            self.root.update()

            url = f"{self.base_url}?page={page}"
            logger.info(f"正在获取第 {page} 页，URL: {url}")
            try:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                }
                response = requests.get(url, headers=headers, timeout=10)
                response.encoding = 'utf-8'
                logger.info(f"第 {page} 页响应状态码: {response.status_code}")
                logger.info(f"第 {page} 页响应内容: {response.text[:200]}...")
                soup = BeautifulSoup(response.text, 'html.parser')
                post_items = soup.select("div.day")
                logger.info(f"第 {page} 页找到 {len(post_items)} 篇文章")

                if not post_items:
                    logger.info(f"第 {page} 页无文章，停止翻页")
                    break

                for item in post_items:
                    title_elem = item.select_one("div.postTitle a")
                    date_elem = item.select_one("div.postTitle")
                    link = title_elem['href'] if title_elem else ""
                    title_text = title_elem.get_text(strip=True) if title_elem else (date_elem.get_text(strip=True) if date_elem else "")

                    if title_elem and link:
                        article = {
                            "title": title_text,
                            "link": link if link.startswith("http") else f"https://www.cnblogs.com{link}",
                            "date": date_elem.get_text(strip=True) if date_elem else "",
                            "selected": False
                        }
                        logger.info(f"解析文章: {article['title']} | 链接: {article['link']}")
                        self.articles.append(article)

                time.sleep(0.5)

            except Exception as e:
                logger.error(f"获取第 {page} 页失败: {str(e)}")
                self.status_label.config(text=f"获取失败: {str(e)}")
                break

        logger.info(f"文章列表获取完成，共 {len(self.articles)} 篇文章")
        self.update_tree()
        self.status_label.config(text=f"共获取 {len(self.articles)} 篇文章")

    def update_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for i, article in enumerate(self.articles):
            var = tk.BooleanVar(value=False)
            self.checkbox_vars[i] = var

            status = "待下载" if not article.get("downloaded") else "已完成"

            item = self.tree.insert("", tk.END, values=(
                "☐",
                article["title"],
                article["date"],
                status
            ))
            article["tree_id"] = item

    def update_tree_display(self):
        for i, article in enumerate(self.articles):
            checked = "☑" if self.checkbox_vars[i].get() else "☐"
            self.tree.item(article["tree_id"], values=(
                checked,
                article["title"],
                article["date"],
                article.get("status", "待下载")
            ))

    def select_all(self):
        for i, article in enumerate(self.articles):
            self.checkbox_vars[i].set(True)
        self.update_tree_display()

    def invert_selection(self):
        for i, article in enumerate(self.articles):
            self.checkbox_vars[i].set(not self.checkbox_vars[i].get())
        self.update_tree_display()

    def download_articles(self):
        selected_indices = [i for i, var in self.checkbox_vars.items() if var.get()]

        if not selected_indices:
            messagebox.showwarning("警告", "请至少选择一篇文章")
            return

        output_dir = self.output_entry.get().strip()
        if not output_dir:
            output_dir = "./hugo_content"

        os.makedirs(output_dir, exist_ok=True)

        self.status_label.config(text="开始下载...")
        self.progress.config(text="0%")

        total = len(selected_indices)
        for idx, article_idx in enumerate(selected_indices):
            article = self.articles[article_idx]
            self.status_label.config(text=f"正在下载: {article['title'][:30]}...")
            self.progress.config(text=f"{int((idx+1)/total*100)}%")
            self.root.update()

            try:
                self.download_single_article(article, output_dir)
                article["downloaded"] = True
                article["status"] = "已完成"
                self.update_tree_display()
            except Exception as e:
                article["status"] = f"失败"
                self.update_tree_display()

            time.sleep(0.5)

        self.status_label.config(text=f"下载完成！共 {total} 篇文章")
        self.progress.config(text="100%")
        messagebox.showinfo("完成", f"文章已保存到: {os.path.abspath(output_dir)}")

    def download_single_article(self, article, output_dir):
        logger.info(f"开始下载文章: {article['title']}")
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(article["link"], headers=headers, timeout=10)
        response.encoding = 'utf-8'
        logger.info(f"文章 {article['title']} 响应状态码: {response.status_code}")

        soup = BeautifulSoup(response.text, 'html.parser')

        title = article["title"]

        date_match = re.search(r'(\d{4}-\d{2}-\d{2})', article["date"])
        if date_match:
            date_str = date_match.group(1)
            logger.info(f"解析日期: {date_str}")
        else:
            date_str = datetime.now().strftime("%Y-%m-%d")
            logger.warning(f"未找到日期，使用当前日期: {date_str}")

        categories = []
        tags = []

        content_div = soup.select_one("#cnblogs_post_body")
        if not content_div:
            content_div = soup.select_one(".blogpost-body")
            logger.info("使用 .blogpost-body 选择器")

        if content_div:
            content_html = str(content_div)
            logger.info(f"文章HTML内容长度: {len(content_html)} 字符")

            h = html2text.HTML2Text()
            h.ignore_links = False
            h.body_width = 0
            content_md = h.handle(content_html)

            content_md = re.sub(r'!\[([^\]]*)\]\(\/\/', r'![\1](https://', content_md)
            content_md = re.sub(r'\]\(\/\/', r'](https://', content_md)

            logger.info(f"转换后Markdown内容长度: {len(content_md)} 字符")
        else:
            content_md = "无法获取文章内容"
            logger.warning("未找到文章内容div")

        filename = re.sub(r'[<>:"/\\|?*]', '', title)
        filename = re.sub(r'\s+', '-', filename)[:50]
        logger.info(f"生成文件名: {filename}.md")

        hugo_content = f'''---
title: "{title}"
date: {date_str}
description: ""
categories: ["博客园迁移"]
tags: [{', '.join(f'"{tag}"' for tag in tags)}]
draft: false
---

# {title}

> 原文链接: {article["link"]} | 迁移自博客园

---

{content_md}
'''

        filepath = os.path.join(output_dir, f"{filename}.md")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(hugo_content)
        logger.info(f"文章保存成功: {filepath}")

def main():
    root = tk.Tk()
    app = CnblogsToHugo(root)
    root.mainloop()

if __name__ == "__main__":
    main()
