# 🗄️ 从零写一个数据库 — 逐行详解

> 原文：[Let's Build a Simple Database](https://cstack.github.io/db_tutorial/) + [DBDB: Dog Bed Database](http://aosabook.org/en/500L/dbdb-dog-bed-database.html)
>
> 每次你存一个文件、查一条记录，数据库在底层到底做了什么？写完你就明白 B+树、持久化、事务是怎么回事。

---

## 0. 先搞懂：数据库最核心的问题是什么？

```
用户说: "把 name='mustafa', age=25 存起来"
数据库要:
1. 写到磁盘（断电不丢）           ← 持久化
2. 能快速找到（不要扫全表）         ← 索引
3. 同时有 100 个人在读写，不能乱    ← 并发控制
```

**最简数据库 = 文件 + 索引。**

---

## 1. 极简键值存储（20 行）

```python
import json
import os

class SimpleDB:
    def __init__(self, filename='database.json'):
        self.filename = filename
        self.data = {}
        self._load()
    
    def _load(self):
        """从磁盘加载数据"""
        if os.path.exists(self.filename):
            with open(self.filename) as f:
                self.data = json.load(f)
    
    def _save(self):
        """写到磁盘"""
        with open(self.filename, 'w') as f:
            json.dump(self.data, f)
    
    def set(self, key, value):
        self.data[key] = value
        self._save()
    
    def get(self, key):
        return self.data.get(key)
    
    def delete(self, key):
        if key in self.data:
            del self.data[key]
            self._save()
```

**问题：** 每次 `set` 都写整个文件。100 万条记录时，改一条就要写几百 MB。而且断电时写一半文件就坏了。

---

## 2. 追加日志（Append-Only Log）— 解决持久化

不覆盖原文件，只追加新操作：

```python
import os
import struct

class LogDB:
    """基于追加日志的数据库"""
    
    def __init__(self, filename='database.log'):
        self.filename = filename
        self.data = {}  # 内存索引
        self._replay()  # 启动时重放日志
    
    def _replay(self):
        """启动时读取日志重建内存状态"""
        if not os.path.exists(self.filename):
            return
        with open(self.filename, 'rb') as f:
            while True:
                # 读取操作类型（1字节）
                type_byte = f.read(1)
                if not type_byte:
                    break
                
                op_type = type_byte[0]  # 0=SET, 1=DEL
                
                # 读取 key 长度 + key
                key_len = struct.unpack('>I', f.read(4))[0]
                key = f.read(key_len).decode()
                
                if op_type == 1:  # DEL
                    self.data.pop(key, None)
                else:  # SET
                    val_len = struct.unpack('>I', f.read(4))[0]
                    value = f.read(val_len).decode()
                    self.data[key] = value
    
    def set(self, key, value):
        """追加 SET 记录"""
        with open(self.filename, 'ab') as f:
            f.write(b'\x00')  # 操作类型: SET
            f.write(struct.pack('>I', len(key)))
            f.write(key.encode())
            f.write(struct.pack('>I', len(value)))
            f.write(value.encode())
        self.data[key] = value
    
    def get(self, key):
        return self.data.get(key)
    
    def delete(self, key):
        """追加 DEL 记录"""
        with open(self.filename, 'ab') as f:
            f.write(b'\x01')  # 操作类型: DEL
            f.write(struct.pack('>I', len(key)))
            f.write(key.encode())
        self.data.pop(key, None)
```

**好处：** 写入极快（只追加）、断电不丢数据（启动时 replay）。

**问题：** 日志会无限增长。需要 compaction——定期把最新的状态写到一个新文件，删掉旧日志。

---

## 3. B+树索引 — 解决"快速查找"

100 万条记录，扫全表要多久？B+树把查找从 O(n) 降到 O(log n)。

```
              [50]
             /    \
        [20,30]    [70,80]
        /  |  \    /  |  \
      [10][25][35][60][75][90]
```

```python
class BPlusTree:
    """简化版 B+树（内存中）"""
    
    def __init__(self, order=4):
        self.order = order      # 每个节点最多 order 个 key
        self.root = LeafNode()  # 根节点是叶子
    
    def insert(self, key, value):
        """插入键值对"""
        leaf = self._find_leaf(key)
        leaf.insert(key, value)
        
        # 如果叶子节点满了，分裂
        if len(leaf.keys) > self.order:
            self._split_leaf(leaf)
    
    def search(self, key):
        """查找"""
        leaf = self._find_leaf(key)
        for i, k in enumerate(leaf.keys):
            if k == key:
                return leaf.values[i]
        return None
    
    def _find_leaf(self, key):
        """从根节点走到叶子节点"""
        node = self.root
        while not isinstance(node, LeafNode):
            # 找到第一个大于 key 的索引
            i = 0
            while i < len(node.keys) and key >= node.keys[i]:
                i += 1
            node = node.children[i]
        return node
    
    def _split_leaf(self, leaf):
        """分裂满的叶子节点"""
        mid = len(leaf.keys) // 2
        new_leaf = LeafNode()
        new_leaf.keys = leaf.keys[mid:]
        new_leaf.values = leaf.values[mid:]
        leaf.keys = leaf.keys[:mid]
        leaf.values = leaf.values[:mid]
        # ... 更新父节点（简化略过）

class LeafNode:
    def __init__(self):
        self.keys = []
        self.values = []
        self.next = None  # 指向下一片叶子（范围查询用）
    
    def insert(self, key, value):
        # 保持有序插入
        i = 0
        while i < len(self.keys) and self.keys[i] < key:
            i += 1
        if i < len(self.keys) and self.keys[i] == key:
            self.values[i] = value  # 覆盖
        else:
            self.keys.insert(i, key)
            self.values.insert(i, value)

class InternalNode:
    def __init__(self):
        self.keys = []     # 分隔 key
        self.children = [] # 子节点
```

**真正的数据库（MySQL、PostgreSQL）用的都是 B+树。** 为什么不是二叉树？因为 B+树更"矮胖"——磁盘每次读一个 4KB 页，B+树一个节点恰好放满一页，减少磁盘 IO。

---

## 4. 事务（ACID）— 解决"改一半崩了怎么办"

```python
class TransactionalDB:
    def __init__(self):
        self.data = {}
        self.transaction = None
    
    def begin(self):
        """开始事务"""
        self.transaction = {'changes': {}, 'deletes': set()}
    
    def set(self, key, value):
        if self.transaction is not None:
            self.transaction['changes'][key] = value
        else:
            self.data[key] = value
    
    def delete(self, key):
        if self.transaction is not None:
            self.transaction['deletes'].add(key)
        else:
            self.data.pop(key, None)
    
    def commit(self):
        """提交：所有修改一次性生效"""
        if self.transaction is None:
            return
        for key, val in self.transaction['changes'].items():
            self.data[key] = val
        for key in self.transaction['deletes']:
            self.data.pop(key, None)
        self.transaction = None
    
    def rollback(self):
        """回滚：所有修改丢弃"""
        self.transaction = None
```

**事务的本质：要么全做，要么全不做。**

---

## 5. 数据库的核心概念总结

| 概念 | 解决什么问题 | 怎么做的 |
|------|------------|---------|
| 持久化 | 断电不丢 | 写日志 / WAL |
| 索引 | 查得快 | B+树 |
| 事务 | 改不坏 | 原子性 + 回滚 |
| 并发 | 多人同时读写 | 锁 / MVCC |
| 缓存 | 不每次都读磁盘 | Buffer Pool |

---

## 🔗 相关链接

- 原文 C 语言版: https://cstack.github.io/db_tutorial/
- DBDB (Python): http://aosabook.org/en/500L/dbdb-dog-bed-database.html
- Build Your Own Database (Go): https://build-your-own.org/database/

---

*— mustaf-osman · 学习笔记*
