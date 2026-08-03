# 🗺️ Build Your Own X — 零基础学习路线

> 来源：[codecrafters-io/build-your-own-x](https://github.com/codecrafters-io/build-your-own-x)（535k ⭐）
>
> 核心理念：**"What I cannot create, I do not understand."** —— 你造不出来的东西，说明你没真懂。

---

## 📖 使用说明

每个项目都有一篇完整的教程文章，跟着敲代码就能跑。我按难度排了序，从幼儿园到研究生，挑你能看懂的动手。

**难度标记：**
| 标记 | 意思 |
|:--:|------|
| 🟢 | 入门：会写 Python 就能做，1-3 小时 |
| 🟡 | 进阶：需要一点计算机基础，一天能搞定 |
| 🔴 | 硬核：要啃，可能一周 |

**语言偏好：** 优先推荐 Python 版本（你熟），找不到 Python 版才用别的语言。

---

## 🟢 第一阶段：建立信心（先做这些）

这些项目很小，代码量在 50-500 行，做完你会觉得"我也能造东西"。

### 1. [用 Python 写一个 Redis](http://charlesleifer.com/blog/building-a-simple-redis-server-with-python/)
> 🟢 | Python | 约 200 行

**你要造什么：** 一个能存数据、查数据的迷你 Redis。客户端发 `SET name mustafa`，服务器存起来，发 `GET name`，返回 `mustafa`。

**学到什么：** socket 编程、TCP 协议、键值存储原理。

---

### 2. [用 Python 写一个 Web 服务器](https://ruslanspivak.com/lsbaws-part1/)
> 🟢 | Python | 3 篇系列

**你要造什么：** 一个能响应浏览器请求的 HTTP 服务器。浏览器访问 `http://localhost:8888`，你的程序返回一个 HTML 页面。

**学到什么：** HTTP 协议到底长什么样（`GET /index.html HTTP/1.1`）、socket、多进程。

---

### 3. [用 Python 写一个模板引擎](http://aosabook.org/en/500L/a-template-engine.html)
> 🟢 | Python | 约 250 行

**你要造什么：** 类似 Jinja2 的东西——把 `Hello {{name}}` 变成 `Hello mustafa`。

**学到什么：** 字符串解析、正则表达式、编译原理的雏形。

---

### 4. [用 Python 写一个 Git 客户端](https://benhoyt.com/writings/pygit/)
> 🟢 | Python | 约 500 行

**你要造什么：** 一个极简 Git——能 `init`、`add`、`commit`、`push`。

**学到什么：** Git 的 `.git` 目录里到底存了什么，commit 和 blob 对象是什么。

---

### 5. [用 Python 写一个 Lisp 解释器](http://norvig.com/lispy.html)
> 🟢 | Python | 约 90 行

**你要造什么：** 一个能执行 `(+ 1 2)` 这种 Lisp 代码的小解释器。**只有 90 行。**

**学到什么：** 编程语言是怎么"理解"代码的——词法分析 → 语法分析 → 执行。

---

## 🟡 第二阶段：深入理解（这些会让你变强）

### 6. [用 Python 写一个数据库](http://aosabook.org/en/500L/dbdb-dog-bed-database.html)
> 🟡 | Python | 约 400 行

**你要造什么：** 一个能持久化存储的键值数据库，断电重启数据还在。

**学到什么：** 数据怎么存到磁盘、索引、事务的雏形。

---

### 7. [用 Python 写一个神经网络](https://victorzhou.com/blog/intro-to-neural-networks/)
> 🟡 | Python | 2 篇系列

**你要造什么：** 从零写一个能识别手写数字的神经网络——不用 TensorFlow，不用 PyTorch，纯 Python + NumPy。

**学到什么：** 前向传播、反向传播、梯度下降——AI 的底层原理。

---

### 8. [用 Python 从零训练一个 LLM](https://github.com/rasbt/LLMs-from-scratch)
> 🟡 | Python | 一本书的篇幅

**你要造什么：** 一个能生成文本的小型 GPT。从数据准备到训练到推理，全流程。

**学到什么：** Transformer 架构、自注意力机制、Tokenizer——ChatGPT 怎么工作的。

---

### 9. [用 Python 写 Docker](https://github.com/Fewbytes/rubber-docker)
> 🟡 | Python | 教程+代码

**你要造什么：** 一个迷你 Docker——隔离进程、限制资源、管理镜像。

**学到什么：** Linux namespace、cgroup、chroot——容器技术的底层。

---

### 10. [用 Python 写一个 Shell](https://brennan.io/2015/01/16/write-a-shell-in-c/)（C 版，但原理通用）
> 🟡 | Python 概念可迁移

**你要造什么：** 一个能执行命令的命令行 Shell（就是你现在用的 bash 的迷你版）。

**学到什么：** 进程创建（fork/exec）、管道、重定向、信号处理。

---

## 🔴 第三阶段：挑战硬核（做完可以吹一辈子）

### 11. [用 C 写一个操作系统——从 0 到 1](https://github.com/cfenollosa/os-tutorial)
> 🔴 | C + 汇编

**你要造什么：** 一个能从裸机启动的微型操作系统——bootloader → kernel → shell。

**学到什么：** CPU 怎么启动、内存管理、中断、系统调用。

---

### 12. [用 C 写一个文本编辑器](https://viewsourcecode.org/snaptoken/kilo/)
> 🔴 | C | 约 1000 行

**你要造什么：** 一个终端里的文本编辑器，类似 vim 的极简版。

**学到什么：** 终端控制序列、光标操作、语法高亮原理。

---

### 13. [用 C 写一个编译器](https://github.com/DoctorWkt/acwj)
> 🔴 | C | 多篇系列

**你要造什么：** 一个能把源代码编译成汇编的编译器。

**学到什么：** 词法分析 → 语法分析 → 语义分析 → 代码生成。编译原理全流程。

---

### 14. [用任何语言——从与非门到俄罗斯方块](https://www.nand2tetris.org/)
> 🔴 | 语言不限 | 12 周完整课程

**你要造什么：** 从一个 NAND 逻辑门开始，一路造出 CPU、汇编器、虚拟机、编译器、操作系统，最后在上面跑俄罗斯方块。

**学到什么：** 计算机的完整技术栈——从晶体管到应用层。Coursera 上有配套视频。

---

## 🎯 推荐路线（零基础，Python 路线）

```
第1周:  Web 服务器 (#2)   →  "原来 HTTP 这么简单"
第2周:  Lisp 解释器 (#5)  →  "原来编程语言也没那么神秘"
第3周:  Git 客户端 (#4)   →  "原来 git add 背后就这点事"
第4周:  Redis (#1)        →  "原来 Redis 就是个 socket + 哈希表"
第5周:  神经网络 (#7)      →  "原来 AI 就是矩阵乘法 + 求导"
第6周:  数据库 (#6)        →  "原来存盘就是写到文件里"
第7周:  LLM (#8)          →  "原来 ChatGPT 就这么训出来的"
第8周:  Docker (#9)       →  "原来容器就是隔离进程"
```

每周一个项目，两个月后你会脱胎换骨。

---

## 📊 全部 30 个类别速查表

| 类别 | 推荐语言 | 难度 | 对你有什么用 |
|------|:--:|:--:|------|
| Web 服务器 | Python | 🟢 | 你每天都在写 rp_server |
| Redis | Python | 🟢 | 缓存/消息队列 |
| Git | Python | 🟢 | 日常开发 |
| Lisp 解释器 | Python | 🟢 | 理解编程语言本质 |
| 模板引擎 | Python | 🟢 | Web 开发 |
| Shell | C | 🟢 | 嵌入式开发天天用 |
| 命令行工具 | Rust/Go | 🟢 | 写自己的工具 |
| 正则引擎 | Python | 🟡 | 文本处理 |
| 数据库 | Python/Go | 🟡 | 后端基础 |
| 搜索引擎 | Python | 🟡 | RAG 底层 |
| 神经网络 | Python | 🟡 | AI 原理 |
| LLM | Python | 🟡 | AI Agent 底层 |
| Docker | Python/Go | 🟡 | 容器部署 |
| 区块链 | Python | 🟡 | 分布式原理 |
| 游戏 (2D) | Python | 🟡 | 有趣 |
| 前端框架 (React) | JavaScript | 🟡 | 理解 Web |
| 文本编辑器 | C | 🔴 | 底层 |
| 操作系统 | C | 🔴 | RK3588 跑的就是 Linux |
| 编译器 | C/Python | 🔴 | 硬核 |
| 编程语言 | 各种 | 🔴 | 终极挑战 |
| 3D 渲染 | C++ | 🔴 | 游戏/仿真 |
| 物理引擎 | C++ | 🔴 | 机器人仿真 |
| 模拟器/虚拟机 | C/C++ | 🔴 | 底层 |
| 处理器 | Verilog | 🔴 | FPGA |
| NAND to Tetris | 不限 | 🔴 | 终极课程 |
| 浏览器引擎 | Rust/Python | 🔴 | 理解渲染 |
| 网络协议栈 | C | 🔴 | TCP/IP 底层 |
| 体素引擎 | C++ | 🔴 | 3D 游戏 |

---

## 🔗 原仓库

https://github.com/codecrafters-io/build-your-own-x

535,000+ star，GitHub 历史 Top 10。教程持续更新中。

---

*— mustaf-osman · 学习笔记*
