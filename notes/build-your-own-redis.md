# 💾 从零写一个 Redis — 逐行详解

> 原文：[Build Your Own Redis](https://build-your-own.org/redis/) + [Simple Redis Server in Python](http://charlesleifer.com/blog/building-a-simple-redis-server-with-python/)
>
> Redis 是后端开发最常用的缓存/消息队列。写完你会理解：socket 怎么收命令、数据怎么存、过期怎么处理。

---

## 0. 先搞懂：Redis 到底是什么？

```bash
$ redis-cli
127.0.0.1:6379> SET name mustafa
OK
127.0.0.1:6379> GET name
"mustafa"
127.0.0.1:6379> DEL name
(integer) 1
```

**本质：一个 TCP 服务器，客户端发文本命令，服务器执行后返回结果。**

```
你的程序                    Redis 服务器
   │                           │
   │── "SET name mustafa\r\n" →│
   │                           │  存到内存哈希表: {"name": "mustafa"}
   │←── "+OK\r\n" ────────────│
   │                           │
   │── "GET name\r\n" ────────→│
   │                           │  从哈希表取出 "mustafa"
   │←── "$7\r\nmustafa\r\n" ──│
```

**RESP 协议：** Redis 客户端和服务器之间的通信格式，纯文本。

| 类型 | 格式 | 示例 |
|------|------|------|
| 简单字符串 | `+内容\r\n` | `+OK\r\n` |
| 错误 | `-错误信息\r\n` | `-ERR unknown command\r\n` |
| 整数 | `:数字\r\n` | `:1\r\n` |
| 批量字符串 | `$长度\r\n内容\r\n` | `$7\r\nmustafa\r\n` |
| 数组 | `*个数\r\n元素...` | `*3\r\n$3\r\nSET\r\n$4\r\nname\r\n$7\r\nmustafa\r\n` |

---

## 1. 完整代码（80 行）

```python
import socket
import threading
import time

# ──── 数据存储 ────
data = {}           # 键 → 值
expires = {}        # 键 → 过期时间戳

# ──── RESP 协议解析 ────
def parse_resp(sock):
    """读取一个 RESP 命令，返回命令列表"""
    line = sock.recv(1024).decode()
    if not line:
        return None
    
    parts = line.strip().split('\r\n')
    if not parts[0].startswith('*'):
        return None
    
    count = int(parts[0][1:])   # *3 → 3 个元素
    cmd = []
    idx = 1
    for _ in range(count):
        if parts[idx].startswith('$'):
            length = int(parts[idx][1:])
            idx += 1
            cmd.append(parts[idx])
            idx += 1
    return cmd

# ──── 命令处理 ────
def handle_command(cmd):
    """执行单个命令，返回 RESP 格式的结果"""
    if not cmd:
        return "-ERR empty command\r\n"
    
    op = cmd[0].upper()
    
    if op == 'PING':
        return "+PONG\r\n"
    
    elif op == 'SET':
        key, val = cmd[1], cmd[2]
        data[key] = val
        # 如果有 EX 参数（过期时间）
        if len(cmd) > 3 and cmd[3].upper() == 'EX':
            ttl = int(cmd[4])
            expires[key] = time.time() + ttl
        return "+OK\r\n"
    
    elif op == 'GET':
        key = cmd[1]
        # 检查过期
        if key in expires and time.time() > expires[key]:
            del data[key]
            del expires[key]
        if key in data:
            val = data[key]
            return f"${len(val)}\r\n{val}\r\n"
        return "$-1\r\n"  # nil
    
    elif op == 'DEL':
        key = cmd[1]
        if key in data:
            del data[key]
            expires.pop(key, None)
            return ":1\r\n"
        return ":0\r\n"
    
    elif op == 'EXISTS':
        key = cmd[1]
        return ":1\r\n" if key in data else ":0\r\n"
    
    elif op == 'KEYS':
        pattern = cmd[1] if len(cmd) > 1 else '*'
        keys = [k for k in data if pattern == '*' or pattern in k]
        resp = f"*{len(keys)}\r\n"
        for k in keys:
            resp += f"${len(k)}\r\n{k}\r\n"
        return resp
    
    elif op == 'FLUSHALL':
        data.clear()
        expires.clear()
        return "+OK\r\n"
    
    else:
        return f"-ERR unknown command '{op}'\r\n"

# ──── 客户端处理 ────
def handle_client(sock, addr):
    print(f"[连接] {addr}")
    while True:
        try:
            cmd = parse_resp(sock)
            if cmd is None:
                break
            print(f"[命令] {cmd}")
            resp = handle_command(cmd)
            sock.sendall(resp.encode())
        except Exception as e:
            print(f"[错误] {e}")
            break
    sock.close()

# ──── 服务器主循环 ────
def main(host='127.0.0.1', port=6379):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.listen(5)
    print(f"Redis-lite 运行在 {host}:{port}")
    
    while True:
        client, addr = server.accept()
        t = threading.Thread(target=handle_client, args=(client, addr))
        t.daemon = True
        t.start()

if __name__ == '__main__':
    main()
```

### 🏃 立刻跑

```bash
# 终端1：启动服务器
python redis-lite.py

# 终端2：用 redis-cli 连接（如果你装了）
redis-cli -p 6379
127.0.0.1:6379> SET name mustafa
OK
127.0.0.1:6379> GET name
"mustafa"
127.0.0.1:6379> PING
PONG

# 或者用 nc 手动测试
echo -e "*3\r\n\$3\r\nSET\r\n\$4\r\nname\r\n\$7\r\nmustafa\r\n" | nc localhost 6379
# +OK

echo -e "*2\r\n\$3\r\nGET\r\n\$4\r\nname\r\n" | nc localhost 6379
# $7
# mustafa
```

---

## 2. 逐行详解

### 2.1 数据存储

```python
data = {}       # 键值对
expires = {}    # 过期时间
```

Redis 本质就是一个**内存哈希表** + **过期管理**。就这么简单。

### 2.2 RESP 协议解析

```
客户端发来的原始数据:
*3\r\n$3\r\nSET\r\n$4\r\nname\r\n$7\r\nmustafa\r\n

拆开看:
*3          → 这个命令有 3 个部分
$3          → 第一部分长度 3
SET         → 第一部分内容
$4          → 第二部分长度 4
name        → 第二部分内容
$7          → 第三部分长度 7
mustafa     → 第三部分内容

解析结果: ['SET', 'name', 'mustafa']
```

### 2.3 SET 命令（带过期）

```python
elif op == 'SET':
    key, val = cmd[1], cmd[2]
    data[key] = val
    if len(cmd) > 3 and cmd[3].upper() == 'EX':
        ttl = int(cmd[4])
        expires[key] = time.time() + ttl  # 过期时间 = 现在 + TTL秒
    return "+OK\r\n"
```

```bash
SET session_token abc123 EX 3600   # 1小时后过期
SET counter 0                       # 永不过期
```

### 2.4 GET 命令（检查过期）

```python
elif op == 'GET':
    key = cmd[1]
    # 先检查过期
    if key in expires and time.time() > expires[key]:
        del data[key]
        del expires[key]
    # 再取值
    if key in data:
        val = data[key]
        return f"${len(val)}\r\n{val}\r\n"
    return "$-1\r\n"  # nil
```

**懒删除策略：** 不主动扫描过期键，只在 GET 的时候检查。真正的 Redis 也是这样做的。

### 2.5 多线程

```python
t = threading.Thread(target=handle_client, args=(client, addr))
t.daemon = True
t.start()
```

每来一个客户端，开一个线程处理。生产环境的 Redis 是单线程事件循环（更快），但对我们来说多线程够用了。

---

## 3. 你还能加什么功能

| 功能 | 命令 | 难度 |
|------|------|:--:|
| 列表 | `LPUSH`, `RPUSH`, `LPOP`, `LRANGE` | 🟢 |
| 哈希 | `HSET`, `HGET`, `HGETALL` | 🟢 |
| 集合 | `SADD`, `SMEMBERS`, `SINTER` | 🟡 |
| 发布/订阅 | `PUBLISH`, `SUBSCRIBE` | 🟡 |
| 持久化 | 定期把 `data` 字典存到文件 | 🟡 |
| 事务 | `MULTI`, `EXEC` | 🔴 |
| 主从复制 | 把命令同步到另一个实例 | 🔴 |

---

## 4. 跟你 rp_server 的关系

你的 `roboparty_rp_server` 里有 WebSocket + 电机驱动。如果加一层 Redis：

```
传感器 → rp_server → Redis（缓存实时数据）
                         ↓
                    前端/App ← 从 Redis 读最新 IMU/BMS 数据
```

**为什么要加 Redis？** 多个客户端同时读数据时，不用每次都调 pybind 读硬件——从 Redis 缓存读，快 100 倍。

---

## 🔗 相关链接

- 原文 Build Your Own Redis (C语言版): https://build-your-own.org/redis/
- Python 版原文: http://charlesleifer.com/blog/building-a-simple-redis-server-with-python/
- RESP 协议规范: https://redis.io/docs/latest/develop/reference/protocol-spec/

---

*— mustaf-osman · 学习笔记*
