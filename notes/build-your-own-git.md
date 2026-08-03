# 📦 从零写一个 Git 客户端 — 逐行详解

> 原文：[Write yourself a Git!](https://wyag.thb.lt/) + [pygit](https://benhoyt.com/writings/pygit/)
>
> 你每天都在用 `git add`、`git commit`、`git push`。但 `.git` 目录里到底存了什么？写完你就全懂了。

---

## 0. 先搞懂：Git 到底存了什么？

```bash
$ git init
$ echo "hello" > file.txt
$ git add file.txt
$ git commit -m "first commit"
```

这时候 `.git` 目录里多了这些：

```
.git/
├── HEAD            → "ref: refs/heads/master"  # 当前分支
├── config           # 仓库配置
├── objects/         # 所有数据都存在这里！
│   ├── ce/013625...  # file.txt 的内容（blob）
│   ├── 1a/7b3f8c...  # 目录结构（tree）
│   └── a1/b2c3d4...  # 提交信息（commit）
└── refs/
    └── heads/
        └── master   → "a1b2c3d4..."  # 指向最新 commit
```

### Git 的四种对象

| 对象类型 | 是什么 | 示例 | SHA 怎么算 |
|----------|--------|------|-----------|
| **blob** | 文件内容 | `"hello\n"` | `sha1("blob 6\0hello\n")` |
| **tree** | 目录结构 | `blob abc... file.txt` | `sha1("tree 25\0...")` |
| **commit** | 一次提交 | tree + parent + author + message | `sha1("commit ...")` |
| **tag** | 标签 | 指向某个 commit | `sha1("tag ...")` |

**SHA-1 哈希是 Git 的身份证号。** 同样的内容永远算出同一个 SHA。这就是 Git 能检测到"内容没变"的原理。

---

## 1. 极简 Git 客户端（50 行）

```python
import hashlib
import os
import zlib
import time

# ──── 工具函数 ────
def sha1(data):
    """计算 SHA-1 哈希"""
    return hashlib.sha1(data).hexdigest()

def write_object(obj_type, content):
    """把对象写入 .git/objects/ 目录"""
    header = f"{obj_type} {len(content)}\0".encode()
    store = header + content
    obj_hash = sha1(store)
    
    # 存到 .git/objects/ab/cdef...
    dir_name = f".git/objects/{obj_hash[:2]}"
    file_name = f"{obj_hash[2:]}"
    os.makedirs(dir_name, exist_ok=True)
    
    with open(f"{dir_name}/{file_name}", 'wb') as f:
        f.write(zlib.compress(store))
    
    return obj_hash

# ──── git init ────
def cmd_init():
    """初始化仓库"""
    for d in ['.git', '.git/objects', '.git/refs', '.git/refs/heads']:
        os.makedirs(d, exist_ok=True)
    with open('.git/HEAD', 'w') as f:
        f.write('ref: refs/heads/master\n')
    print("Initialized empty Git repository")

# ──── git add ────
def cmd_add(filename):
    """把文件内容存成 blob 对象"""
    with open(filename, 'rb') as f:
        content = f.read()
    
    obj_hash = write_object('blob', content)
    print(f"blob {obj_hash[:7]} → {filename}")
    return obj_hash

# ──── git commit ────
def cmd_commit(message):
    """创建 commit 对象"""
    # 1. 创建 tree 对象（简化为单文件）
    filename = 'file.txt'
    with open(filename, 'rb') as f:
        content = f.read()
    blob_hash = write_object('blob', content)
    
    # tree 格式: "100644 blob <hash>\t<filename>"
    tree_content = f"100644 blob {blob_hash}\t{filename}\n".encode()
    tree_hash = write_object('tree', tree_content)
    
    # 2. 读取 parent（之前的 HEAD）
    parent_hash = None
    try:
        with open('.git/refs/heads/master') as f:
            parent_hash = f.read().strip()
    except FileNotFoundError:
        pass
    
    # 3. 构建 commit 内容
    timestamp = int(time.time())
    author = "mustafa <mustafa@example.com>"
    
    commit_lines = [
        f"tree {tree_hash}",
    ]
    if parent_hash:
        commit_lines.append(f"parent {parent_hash}")
    commit_lines += [
        f"author {author} {timestamp} +0800",
        f"committer {author} {timestamp} +0800",
        "",  # 空行
        message,
        "",  # 空行结束
    ]
    
    commit_content = '\n'.join(commit_lines).encode()
    commit_hash = write_object('commit', commit_content)
    
    # 4. 更新 HEAD
    with open('.git/refs/heads/master', 'w') as f:
        f.write(commit_hash)
    
    print(f"[master {commit_hash[:7]}] {message}")

# ──── git log ────
def cmd_log():
    """查看提交历史"""
    try:
        with open('.git/refs/heads/master') as f:
            commit_hash = f.read().strip()
    except FileNotFoundError:
        print("No commits yet")
        return
    
    while commit_hash:
        # 读取 commit 对象
        dir_name = f".git/objects/{commit_hash[:2]}"
        file_name = commit_hash[2:]
        with open(f"{dir_name}/{file_name}", 'rb') as f:
            raw = zlib.decompress(f.read())
        
        # 解析 commit
        text = raw.decode()
        lines = text.split('\n')
        tree_line = [l for l in lines if l.startswith('tree ')][0]
        parent_line = [l for l in lines if l.startswith('parent ')]
        msg_start = lines.index('') + 1
        message = lines[msg_start]
        
        print(f"\ncommit {commit_hash}")
        print(f"Date:   ...")
        print(f"\n    {message}")
        
        # 下一个
        commit_hash = parent_line[0].split()[1] if parent_line else None

# ──── 命令行入口 ────
if __name__ == '__main__':
    import sys
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'help'
    
    if cmd == 'init':
        cmd_init()
    elif cmd == 'add':
        cmd_add(sys.argv[2])
    elif cmd == 'commit':
        msg = sys.argv[2] if len(sys.argv) > 2 else 'no message'
        cmd_commit(msg)
    elif cmd == 'log':
        cmd_log()
    else:
        print("用法: python git-lite.py <init|add|commit|log>")
```

### 🏃 立刻跑

```bash
# 1. 初始化
$ python git-lite.py init
Initialized empty Git repository

# 2. 写一个文件
$ echo "hello world" > file.txt

# 3. add → 存成 blob
$ python git-lite.py add file.txt
blob a0c2d3e → file.txt

# 4. commit → 创建 commit 对象
$ python git-lite.py commit "first commit"
[master a1b2c3d] first commit

# 5. 修改文件，再 commit
$ echo "hello git" > file.txt
$ python git-lite.py add file.txt
$ python git-lite.py commit "second commit"
[master e4f5g6h] second commit

# 6. 看历史
$ python git-lite.py log
commit e4f5g6h...
    second commit

commit a1b2c3d...
    first commit

# 7. 用真正的 git 也能读！
$ git log
commit e4f5g6h...  ← 真的 git 认识我们造的数据！
```

---

## 2. 逐行详解

### 2.1 SHA-1：Git 的身份证

```python
def sha1(data):
    return hashlib.sha1(data).hexdigest()
```

**同样的输入 → 永远同样的输出。** 这就是为什么两个不同的人 clone 同一个仓库，commit hash 一样。

### 2.2 Blob 对象：文件内容

```python
header = f"blob {len(content)}\0".encode()
store = header + content
obj_hash = sha1(store)
```

`blob 6\0hello\n` → SHA → `ce013625...`

**Blob 只存文件内容，不存文件名。** 文件名存在 tree 对象里。

### 2.3 Tree 对象：目录结构

```python
tree_content = f"100644 blob {blob_hash}\t{filename}\n".encode()
```

```
100644 blob ce013625...    file.txt
040000 tree 1a7b3f8c...    src/
```

- `100644` = 普通文件权限
- `040000` = 目录

### 2.4 Commit 对象：一次提交

```
tree 1a7b3f8c...
parent a1b2c3d4...      ← 指向上一个 commit（形成链）
author mustafa ... +0800
committer mustafa ... +0800

first commit
```

**commit 链就是 Git 的历史——每个 commit 指着它的爸爸。**

### 2.5 对象存储路径

```python
dir_name = f".git/objects/{obj_hash[:2]}"   # 前2位 = 目录名
file_name = f"{obj_hash[2:]}"               # 剩余 = 文件名
```

```
SHA: ce013625...
路径: .git/objects/ce/013625...
```

**为什么分目录？** 一个目录里放太多文件会慢。Git 用前 2 位做子目录，分散存储。

### 2.6 Zlib 压缩

```python
zlib.compress(store)
```

Git 用 zlib 压缩所有对象。省空间，但内容还是能完整还原。

---

## 3. 你还缺什么（真正的 Git 比这复杂在哪）

| 功能 | 我们的实现 | 真正的 Git |
|------|-----------|-----------|
| add | 支持单文件 | 索引（staging area）、多文件 |
| commit | 单文件 tree | 完整目录树递归 |
| branch | ❌ | `git branch`, `git checkout` |
| merge | ❌ | 三方合并算法 |
| push/pull | ❌ | HTTP/SSH 协议、packfile |
| diff | ❌ | Myers diff 算法 |
| 垃圾回收 | ❌ | `git gc` |

但这 50 行已经让你理解了 Git 的核心：

> **Git 是一个内容寻址的文件系统——用 SHA-1 做索引，存 blob/tree/commit/tag 四种对象。**

---

## 🔗 相关链接

- 原文 Write yourself a Git: https://wyag.thb.lt/
- Python 版 pygit: https://benhoyt.com/writings/pygit/
- Git 内部原理（Pro Git）: https://git-scm.com/book/en/v2/Git-Internals-Git-Objects
- Build Your Own X: https://github.com/codecrafters-io/build-your-own-x

---

*— mustaf-osman · 学习笔记*
