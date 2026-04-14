# cnblogs-to-hugo

博客园文章批量迁移到 Hugo 静态博客的工具。

## 功能特性

- **GUI 界面** - 简洁易用的图形化界面
- **批量获取** - 自动获取博客园用户的所有文章列表
- **分页支持** - 自动翻页获取完整文章列表
- **选择性下载** - 支持全选、反选文章
- **格式转换** - 将 HTML 内容转换为 Markdown 格式
- **图片链接处理** - 自动修复图片链接
- **Hugo 兼容** - 生成符合 Hugo 规范的 Markdown 文件，包含完整的 Front Matter

## 环境要求

- Python 3.8+
- tkinter (Python 内置)
- requests
- beautifulsoup4
- html2text

## 安装依赖

```bash
pip install requests beautifulsoup4 html2text
```

## 使用方法

1. 运行脚本：

```bash
python cnblogs_to_hugo.py
```

2. 在界面中输入博客园用户名
3. 设置输出目录（默认为 `./hugo_content`）
4. 点击「获取文章列表」按钮
5. 在列表中勾选需要迁移的文章（可使用全选/反选）
6. 点击「下载选中文章」开始转换

## 输出格式

生成的文件为 Hugo Markdown 格式：

```markdown
---
title: "文章标题"
date: 2024-01-01
description: ""
categories: ["博客园迁移"]
tags: [""]
draft: false
---

# 文章标题

> 原文链接: https://www.cnblogs.com/xxx/p/xxx | 迁移自博客园

---

文章内容...
```

## 项目结构

```
cnblogs-to-hugo/
├── cnblogs_to_hugo.py    # 主程序
├── LICENSE               # MIT License
└── README.md             # 项目文档
```

## 技术栈

- **GUI**: tkinter
- **网络请求**: requests
- **HTML 解析**: BeautifulSoup
- **格式转换**: html2text
- **日志**: Python logging

## License

MIT License
