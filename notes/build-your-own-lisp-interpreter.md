# 🧠 从零写一个 Lisp 解释器 — 逐行详解

> 原文：[Peter Norvig - (How to Write a (Lisp) Interpreter (in Python))](http://norvig.com/lispy.html)
>
> 作者是 Peter Norvig（Google 研究总监，AI 泰斗级人物）。这篇教程写于 2010 年，被誉为"最优雅的 Python 代码之一"。
>
> **只有 90 行代码**，造出一个能跑 Scheme（Lisp 方言）的完整解释器。

---

## 0. 先搞懂：解释器到底是什么？

你现在写的 Python 代码，是怎么变成电脑能执行的指令的？

```
你写的代码                  解释器/编译器              电脑执行
──────────                ────────────              ────────
print("hello")     →     Python 解释器         →     屏幕上出现 hello
x = 1 + 2          →     计算 1+2=3            →     x 变成 3
```

**解释器的工作就三步，反复循环：**

```
  ┌──────────┐     ┌──────────┐     ┌──────────┐
  │  读取     │ →  │  计算     │ →  │  打印     │
  │  READ    │     │  EVAL    │     │  PRINT   │
  └──────────┘     └──────────┘     └──────────┘
        ↑                                  │
        └────────────  循环  ──────────────┘
```

这叫 **REPL**（Read-Eval-Print Loop）。你在终端里输入 `python` 然后一行行敲代码，就是 REPL。

**我们要造的就是这个东西。** 只不过它读的不是 Python，是 Lisp。

Lisp 长这样：

```lisp
(+ 1 2)           ; 返回 3
(* 3 (+ 4 5))     ; 返回 27（3 * 9）
(define x 10)     ; 定义变量 x = 10
(lambda (x) (* x x))  ; 定义一个"平方"函数
```

**Lisp 的核心特点：操作符在最前面。** `1 + 2` 写成 `(+ 1 2)`。为什么？因为这样所有东西都是统一格式——`(函数 参数1 参数2 ...)`，解释器处理起来极其简单。

---

## 1. 最小可行版本（7 行）

先把骨架搭起来。以下代码能处理 `(+ 1 2)` 这种东西：

```python
def eval(exp):
    """计算一个 Lisp 表达式"""
    if isinstance(exp, (int, float)):   # 如果是数字
        return exp                       # 直接返回
    elif exp[0] == '+':                  # 如果是 (+ 1 2)
        return eval(exp[1]) + eval(exp[2])
    elif exp[0] == '-':
        return eval(exp[1]) - eval(exp[2])

# 测试
print(eval(['+', 1, 2]))       # 3
print(eval(['+', 1, ['*', 3, 4]]))  # 13 (1 + 3*4)
```

**拆解：**

- `['+', 1, 2]` 是 Python 列表，代表 Lisp 的 `(+ 1 2)`
- `eval` 看到 `+` → 把后面的参数都算出来 → 加起来
- 嵌套的 `['*', 3, 4]` 会递归调用 `eval`——先算出 `3*4=12`，再 `1+12=13`

**这就是解释器的核心。** 剩下的全是"加功能"。

---

## 2. 加入变量（15 行）

`(define x 10)` 怎么处理？

```python
# 环境 = 变量名 → 值的映射
env = {}

def eval(exp):
    if isinstance(exp, str):            # 如果是变量名，去环境里找
        return env[exp]
    elif isinstance(exp, (int, float)): # 数字直接返回
        return exp
    elif exp[0] == '+':
        return eval(exp[1]) + eval(exp[2])
    elif exp[0] == 'define':            # (define 变量名 值)
        name, val = exp[1], eval(exp[2])
        env[name] = val
        return val
```

**环境（Environment）** 就是一个 Python 字典：`{'x': 10, 'y': 20}`。定义变量就是往字典里加一条。

---

## 3. 加入函数（30 行）

```lisp
(lambda (x) (* x x))    ; 定义一个"平方"函数
```

```python
def eval(exp, env=None):
    if env is None: env = global_env
    
    if isinstance(exp, str):
        return env[exp]
    elif isinstance(exp, (int, float)):
        return exp
    elif exp[0] == '+':
        return eval(exp[1], env) + eval(exp[2], env)
    elif exp[0] == 'define':
        name, val = exp[1], eval(exp[2], env)
        env[name] = val
        return val
    elif exp[0] == 'lambda':            # (lambda (参数) 函数体)
        params, body = exp[1], exp[2]
        return ['procedure', params, body, env]  # 返回一个"闭包"
    elif exp[0] == 'if':                # (if 条件 真分支 假分支)
        test = eval(exp[1], env)
        return eval(exp[2] if test else exp[3], env)
    else:                               # 函数调用: (函数 参数...)
        proc = eval(exp[0], env)        # 先算出函数是啥
        args = [eval(a, env) for a in exp[1:]]  # 算出所有参数
        if proc[0] == 'procedure':      # 如果是自定义函数
            # 创建新环境: 参数名 → 实际参数值
            local_env = dict(proc[3])   # 继承外层环境
            local_env.update(zip(proc[1], args))
            return eval(proc[2], local_env)
```

**三个关键概念：**

| 概念 | 人话 |
|------|------|
| **闭包 (Closure)** | `['procedure', params, body, env]`——函数记得它"出生"在哪 |
| **环境链** | `local_env` 里找不到变量→去外层 `env` 找→再找不到就去 `global_env` |
| **函数调用** | 算出函数是什么→算出参数是什么→创建新环境→在新区环境里执行函数体 |

---

## 4. 完整版本（90 行）

上面是教学版。下面是 Peter Norvig 的真实版本（我转成了 Python 3）：

```python
import math
import operator as op

# ──── 环境 = 变量字典 ────
def standard_env():
    """创建全局环境：内置函数 + 数学函数"""
    env = {}
    env.update(vars(math))  # sin, cos, pi 等
    env.update({
        '+': op.add, '-': op.sub, '*': op.mul, '/': op.truediv,
        '>': op.gt, '<': op.lt, '>=': op.ge, '<=': op.le, '=': op.eq,
        'abs': abs, 'max': max, 'min': min,
        'round': round, 'len': len,
        'car': lambda x: x[0],       # 取列表第一个
        'cdr': lambda x: x[1:],      # 取列表剩余部分
        'cons': lambda x, y: [x] + y,# 构造列表
        'list': lambda *x: list(x),
        'list?': lambda x: isinstance(x, list),
        'null?': lambda x: x == [],
        'equal?': op.eq,
        'not': op.not_,
        'append': op.add,
        'number?': lambda x: isinstance(x, (int, float)),
        'symbol?': lambda x: isinstance(x, str),
        'begin': lambda *x: x[-1],
    })
    return env

global_env = standard_env()

# ──── 解析器：把字符串变成列表 ────
def tokenize(chars):
    """把字符串拆成 token 列表"""
    return chars.replace('(', ' ( ').replace(')', ' ) ').split()

def parse(program):
    """把 token 列表变成嵌套列表（AST）"""
    return read_from_tokens(tokenize(program))

def read_from_tokens(tokens):
    if len(tokens) == 0:
        raise SyntaxError('unexpected EOF')
    token = tokens.pop(0)
    if token == '(':
        L = []
        while tokens[0] != ')':
            L.append(read_from_tokens(tokens))
        tokens.pop(0)  # 弹出 ')'
        return L
    elif token == ')':
        raise SyntaxError('unexpected )')
    else:
        return atom(token)

def atom(token):
    """把 token 转成 Python 对象：数字→int/float，其他→字符串"""
    try: return int(token)
    except ValueError:
        try: return float(token)
        except ValueError:
            return str(token)

# ──── 解释器核心 ────
def eval(x, env=global_env):
    """计算表达式"""
    if isinstance(x, str):             # 变量引用
        return env[x]
    elif not isinstance(x, list):      # 字面量（数字）
        return x
    elif x[0] == 'if':                 # (if test conseq alt)
        (_, test, conseq, alt) = x
        return eval(conseq if eval(test, env) else alt, env)
    elif x[0] == 'define':             # (define var exp)
        (_, var, exp) = x
        env[var] = eval(exp, env)
    elif x[0] == 'lambda':             # (lambda (vars) body)
        (_, params, body) = x
        return lambda *args: eval(body, dict(env, **dict(zip(params, args))))
    else:                              # 函数调用
        proc = eval(x[0], env)
        args = [eval(arg, env) for arg in x[1:]]
        return proc(*args)

# ──── REPL ────
def repl():
    """Read-Eval-Print Loop"""
    print("Lispy — Ctrl+D 退出")
    while True:
        try:
            val = eval(parse(input('lispy> ')))
            if val is not None:
                print(val)
        except EOFError:
            break
        except Exception as e:
            print(f'错误: {e}')

if __name__ == '__main__':
    repl()
```

### 🏃 跑起来试试

```bash
$ python lispy.py

lispy> (+ 1 2)
3

lispy> (* 3 (+ 4 5))
27

lispy> (define x 10)
lispy> (* x x)
100

lispy> (define square (lambda (n) (* n n)))
lispy> (square 5)
25

lispy> (if (> 3 2) "yes" "no")
yes

lispy> (car (list 10 20 30))
10

lispy> (cdr (list 10 20 30))
[20, 30]

lispy> (max 3 7 2 9)
9
```

---

## 5. 核心原理拆解

### 5.1 词法分析 + 语法分析（2 行）

```python
def tokenize(chars):
    return chars.replace('(', ' ( ').replace(')', ' ) ').split()
```

输入 `(+ 1 2)` → 输出 `['(', '+', '1', '2', ')']`

**就这么简单**——Lisp 的括号天生就是语法分隔符，不需要复杂的解析器。

### 5.2 抽象语法树（递归下降）

```
token 流:  ['(', '+', '1', '(', '*', '3', '4', ')', ')']
                         ↓
AST（嵌套列表）:  ['+', 1, ['*', 3, 4]]
```

`read_from_tokens` 看到 `(` 就递归调用自己，直到看到 `)` 为止。

### 5.3 eval — 整个解释器的灵魂

```python
def eval(x, env):
    if isinstance(x, str):           # x → 去环境里找
        return env[x]
    elif not isinstance(x, list):    # 42 → 直接返回
        return x
    elif x[0] == 'if':               # (if ...) → 判断条件
        ...
    elif x[0] == 'define':           # (define ...) → 存变量
        ...
    elif x[0] == 'lambda':           # (lambda ...) → 造函数
        ...
    else:                            # (func args...) → 调用
        ...
```

**eval 的本质是一个巨大的"if-else"分派表**——看到什么关键字，就做什么事。

### 5.4 lambda — 闭包

```python
elif x[0] == 'lambda':
    (_, params, body) = x
    return lambda *args: eval(body, dict(env, **dict(zip(params, args))))
```

| 组件 | 说明 |
|------|------|
| `params` | 参数名列表，如 `['n']` |
| `body` | 函数体，如 `['*', 'n', 'n']` |
| `env` | 当前环境（闭包捕获） |
| `dict(env, **dict(zip(params, args)))` | 新环境 = 旧环境 + 参数绑定 |

**闭包的精髓：** 函数记住它被定义时的环境。`(define square (lambda (n) (* n n)))`——`square` 被调用时，`n` 被绑到实际参数，其它变量去外层环境找。

---

## 6. 你能做什么（能力边界）

**能跑：**
- 算术：`(+ 1 (* 2 3))`
- 条件：`(if (> x 0) "正" "负")`
- 变量：`(define x 10)`
- 函数：`(lambda (x) (* x x))`
- 递归：能写阶乘、斐波那契

**不能跑：**
- 宏（macro）、尾递归优化、错误处理、类型检查

但这 90 行已经包含了所有解释器的核心概念。JavaScript 的 V8 引擎、Python 的 CPython，原理都是这个。

---

## 🔗 相关链接

- 原文: http://norvig.com/lispy.html
- 原代码: http://norvig.com/lispy.py
- Build Your Own X: https://github.com/codecrafters-io/build-your-own-x
- 作者 Peter Norvig: https://norvig.com

---

*— mustaf-osman · 学习笔记*
