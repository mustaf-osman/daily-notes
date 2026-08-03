# 🔧 从零写一个 Web 服务器 — 逐行详解

> 原文：[Let's Build A Web Server](https://ruslanspivak.com/lsbaws-part1/) by Ruslan Spivak
> 
> 本文用人话逐行解释每一个概念。零基础能看懂，看完能自己写。

---

## 0. 先搞懂：浏览器打开一个网页，背后发生了什么？

你在浏览器地址栏输入 `http://localhost:8888/hello`，敲回车。

```
你的浏览器                        Web 服务器
    │                                  │
    │──── 1. 建立 TCP 连接 ──────────→│
    │                                  │
    │──── 2. 发送 HTTP 请求 ─────────→│
    │     GET /hello HTTP/1.1          │
    │                                  │
    │←─── 3. 返回 HTTP 响应 ──────────│
    │     HTTP/1.1 200 OK              │
    │     Hello, World!                │
    │                                  │
    └─ 4. 浏览器显示 "Hello, World!"
```

**四个关键概念：**

| 概念 | 人话 |
|------|------|
| **TCP 连接** | 打电话——先拨号接通，然后才能说话 |
| **Socket（套接字）** | 电话机——用来收发数据的工具 |
| **HTTP 请求** | 你说的话——"给我 /hello 这个页面" |
| **HTTP 响应** | 对方回的——"200 OK，这是你要的内容" |

---

## 1. 完整代码（Part 1 最终版）

先看完整代码，你马上就能跑。然后把下面代码保存为 `webserver.py`：

```python
import socket

HOST, PORT = '', 8888

# 1. 创建一个"电话机"
listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 2. 允许重复使用端口（防止"Address already in use"报错）
listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# 3. 把电话机绑定到一个"电话号码"（IP + 端口）
listen_socket.bind((HOST, PORT))

# 4. 开始接听——最多1个人排队
listen_socket.listen(1)

print(f'Serving HTTP on port {PORT} ...')

while True:
    # 5. 等待有人"打电话"进来——会一直卡在这里直到有人连接
    client_connection, client_address = listen_socket.accept()

    # 6. 接听——读取对方说的话（最多1024字节）
    request_data = client_connection.recv(1024)
    print(request_data.decode('utf-8'))

    # 7. 回复——这就是 HTTP 响应！
    http_response = b"""\
HTTP/1.1 200 OK

Hello, World!
"""
    client_connection.sendall(http_response)
    
    # 8. 挂电话
    client_connection.close()
```

### 🏃 立刻跑一下

```bash
# 终端1：启动服务器
python webserver.py
# 输出: Serving HTTP on port 8888 ...

# 终端2：模拟浏览器
curl http://localhost:8888/hello
# 输出: Hello, World!
```

**跑通了再往下看。** 下面我一行一行给你讲。

---

## 2. 逐行详解

### 第1行：`import socket`

`socket` 是 Python 自带的库。**socket = 电话机。** 你不需要装任何东西，Python 自带。

---

### 第2行：`HOST, PORT = '', 8888`

| 变量 | 值 | 意思 |
|------|-----|------|
| `HOST` | `''`（空字符串） | 监听本机所有网络接口。填 `'127.0.0.1'` 就只能本机访问，填 `'0.0.0.0'` 就是任何人都能连 |
| `PORT` | `8888` | 端口号。可以理解成"分机号"。一个 IP 地址上可以跑很多服务，端口号用来区分 |

**类比：** IP 地址是大楼地址，端口号是房间号。

---

### 第3行：`listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)`

创建了一个"电话机"。

| 参数 | 值 | 意思 |
|------|-----|------|
| `socket.AF_INET` | IPv4 | 用 IPv4 地址（比如 192.168.1.1） |
| `socket.SOCK_STREAM` | TCP | 用 TCP 协议（可靠的、有序的传输） |

**为什么是 TCP？** HTTP 协议是建立在 TCP 之上的。TCP 保证数据不丢、不乱序。就像打电话：你说话的顺序，对方听到的顺序是一样的。

> 另类选择：`socket.SOCK_DGRAM` 是 UDP——像写信，发出去不管对方收没收到。视频通话用 UDP（丢几帧无所谓），网页必须用 TCP。

---

### 第4行：`listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)`

**这是一个"防坑"设置。** 如果你按 Ctrl+C 停了服务器，立刻重新启动，会报错 `Address already in use`。因为操作系统还没释放那个端口。

这行代码告诉操作系统："端口还在占用？没事，让我用。"

---

### 第5行：`listen_socket.bind((HOST, PORT))`

**把电话机插到墙上。** 把 socket 绑定到一个具体的地址和端口。

`(HOST, PORT)` 是一个元组。注意是两个括号——外面是 `bind()` 的括号，里面是元组的括号。

---

### 第6行：`listen_socket.listen(1)`

**开始接电话。** 参数 `1` 是"等待队列"的长度——最多允许 1 个人排队等待接听。

---

### 第7行：`while True:`

**死循环。** 服务器永远运行，处理完一个请求就等下一个。你不关它，它永远不休息。

---

### 第8行：`client_connection, client_address = listen_socket.accept()`

**这是最关键的一行——接电话。**

`accept()` 会一直等，直到有人连接进来。有人连进来后，它返回两个东西：

| 返回值 | 是什么 | 类比 |
|--------|--------|------|
| `client_connection` | 一个新的 socket 对象 | 你跟这个客户之间的"专线电话" |
| `client_address` | 客户的 IP 和端口 | 来电显示——知道是谁打来的 |

**注意：** 原来的 `listen_socket` 还在，继续等下一个电话。`client_connection` 是专门跟这一个客户通信的。

---

### 第9行：`request_data = client_connection.recv(1024)`

**听对方说话。** `recv(1024)` 表示"最多接收 1024 字节"。

浏览器发过来的原始数据长这样：

```
GET /hello HTTP/1.1
Host: localhost:8888
User-Agent: Mozilla/5.0 ...
Accept: text/html,...
```

| 行 | 含义 |
|----|------|
| `GET /hello HTTP/1.1` | 请求行——方法 + 路径 + 协议版本 |
| `Host: localhost:8888` | 请求头——告诉服务器"我要访问这个主机" |
| `User-Agent: ...` | 请求头——告诉服务器"我是什么浏览器" |
| 空行 | 请求头结束标记 |

**我们的简单服务器完全不管这些内容**——不管浏览器要什么，我们都返回 "Hello, World!"。

---

### 第10行：`http_response = b"""\..."""`

**准备回复。**

```python
http_response = b"""\
HTTP/1.1 200 OK

Hello, World!
"""
```

| 部分 | 内容 | 含义 |
|------|------|------|
| 第1行 | `HTTP/1.1 200 OK` | **状态行**——协议版本 + 状态码 + 原因短语 |
| 第2行 | （空行） | **必须要有！** 分隔头部和正文 |
| 第3行 | `Hello, World!` | **响应体**——真正的内容 |

`b"""..."""` 是 Python 的字节字符串（bytes）。网络传输必须用字节，不能用普通的 str。

**200 是什么意思？** HTTP 状态码：

| 状态码 | 含义 |
|:--:|------|
| 200 | OK——成功了 |
| 404 | Not Found——找不到 |
| 500 | Internal Server Error——服务器崩了 |

---

### 第11行：`client_connection.sendall(http_response)`

**把回复发出去。** `sendall()` 会确保所有数据都发送完毕。

---

### 第12行：`client_connection.close()`

**挂电话。** HTTP 是无状态协议——处理完一个请求就断开连接。

---

## 3. 你能手动测试

不用浏览器，用命令行也能测：

```bash
# 方法1：curl
curl http://localhost:8888/anything

# 方法2：nc
echo -e "GET / HTTP/1.1\r\n\r\n" | nc localhost 8888

# 方法3：Python 一行
python -c "import urllib.request; print(urllib.request.urlopen('http://localhost:8888').read().decode())"
```

---

## 4. 这个服务器的问题

| 问题 | 说明 |
|------|------|
| **一次只能处理一个人** | `while True` 里没有多线程，前一个请求没处理完，后面的人等着 |
| **不管请求的是什么** | 你访问 `/hello` 还是 `/goodbye`，都返回 "Hello, World!" |
| **没有请求头解析** | 不管浏览器发了什么头部信息 |
| **不能跑 Flask/Django** | 没有 WSGI 接口（Part 2 解决这个问题） |

---

## 5. 跟你写的 rp_server 对比

你在 `roboparty_rp_server` 里用的 FastAPI + uvicorn，底层原理跟这个一模一样：

| 你写的 | 本文的 | 本质 |
|--------|--------|------|
| `uvicorn.run(app, host=host, port=port)` | `socket.bind + listen + accept` | 创建 socket 监听 |
| `@app.get("/health")` | 解析 `GET /health HTTP/1.1` | 路由匹配 |
| `return {"status": "ok"}` | `HTTP/1.1 200 OK\r\n\r\n{...}` | 返回响应 |

**FastAPI 只是帮你做了 socket 创建、HTTP 解析、路由匹配这些脏活。** 底层全是本文讲的这些东西。

---

## 6. 下一步（Part 2 & 3 预告）

| 部分 | 学什么 |
|------|--------|
| Part 2 | **WSGI 协议**——让你的服务器能跑 Flask/Django。理解 `application(environ, start_response)` |
| Part 3 | **并发处理**——用 `fork` 同时处理多个请求 |

---

## 🔗 相关链接

- 原文 Part 1: https://ruslanspivak.com/lsbaws-part1/
- 原文 Part 2: https://ruslanspivak.com/lsbaws-part2/
- 原文 Part 3: https://ruslanspivak.com/lsbaws-part3/
- 原仓库代码: https://github.com/rspivak/lsbaws
- Build Your Own X 总览: https://github.com/codecrafters-io/build-your-own-x

---

*— mustaf-osman · 学习笔记*

> 下一篇预告：[从零写 Lisp 解释器](http://norvig.com/lispy.html) — 90 行 Python 代码造一个编程语言，逐行拆给你看。
