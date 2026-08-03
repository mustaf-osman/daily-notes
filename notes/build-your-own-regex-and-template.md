# 🔍 从零写一个正则引擎 — 逐行详解

> 原文：[Build Your Own Regex Engine](https://deniskyashif.com/2019/02/17/implementing-a-regular-expression-engine/) + [A Regular Expression Matcher](https://www.cs.princeton.edu/courses/archive/spr09/cos333/beautiful.html)
>
> 正则表达式你天天用——`grep`、`sed`、Python `re`。但 `.*` 怎么匹配任意字符？`a|b` 怎么实现"或"？写完你就明白。

---

## 0. 正则引擎最简模型：NFA（非确定性有限自动机）

```
正则: a(b|c)*

      b
    ↗   ↘
start → a → (状态2) → end
        ↘   ↗
      c
```

**核心思想：** 把正则表达式转成一个状态机。输入字符串挨个字符走过去，走到"接受状态"就是匹配成功。

---

## 1. 极简正则引擎（40 行）

只支持：普通字符、`.`（匹配任意）、`*`（重复 0 次或多次）

```python
def match(pattern, text):
    """
    匹配正则表达式（只支持 . 和 *）
    match("a.c", "abc") → True
    match("a*b", "aaab") → True
    """
    if not pattern:
        return not text  # 模式空了，文本也该空
    
    # 是否有 * 量词？
    has_star = len(pattern) > 1 and pattern[1] == '*'
    
    if has_star:
        # a* 匹配：跳过 a*（匹配 0 次）或 消耗一个 a（匹配 1+ 次）
        return match(pattern[2:], text) or \
               (text and (pattern[0] == '.' or pattern[0] == text[0]) 
                and match(pattern, text[1:]))
    else:
        # 普通字符或 .
        if not text:
            return False
        if pattern[0] != '.' and pattern[0] != text[0]:
            return False
        return match(pattern[1:], text[1:])


# 测试
print(match("a.c", "abc"))      # True
print(match("a.c", "axc"))      # True
print(match("a.c", "ac"))       # False (缺一个字符)
print(match("ab*c", "ac"))      # True  (b 出现 0 次)
print(match("ab*c", "abc"))     # True  (b 出现 1 次)
print(match("ab*c", "abbbbc"))  # True  (b 出现 4 次)
print(match("a.*b", "axyzb"))   # True  (.* 匹配 xyz)
print(match("a.*b", "ab"))      # True  (.* 匹配空)
```

### 🏃 跑一下

```
a.c   vs abc   → True ✅
a.c   vs axc   → True ✅
a.c   vs ac    → False ✅ (少了一个字符)
ab*c  vs ac    → True ✅ (b 出现0次)
ab*c  vs abbbbc→ True ✅ (b 出现4次)
a.*b  vs axyzb → True ✅
```

---

## 2. 逐行拆解

### 2.1 `*` 的核心逻辑

```python
if has_star:
    return match(pattern[2:], text) or \       # 跳过 a*（匹配0次）
           (text and ... and match(pattern, text[1:]))  # 消耗一个字符，继续用 a*
```

**这是整个正则引擎的精髓——"回溯"。**

```
pattern = "ab*c"
text    = "abbbc"

match("ab*c", "abbbc")
  → 尝试: 跳过 b* → match("c", "abbbc") → 失败！
  → 尝试: 消耗一个 b → match("b*c", "bbc")
    → 尝试: 跳过 b* → match("c", "bbc") → 失败！
    → 尝试: 消耗一个 b → match("b*c", "bc")
      → 尝试: 跳过 b* → match("c", "bc") → 失败！
      → 尝试: 消耗一个 b → match("b*c", "c")
        → 尝试: 跳过 b* → match("c", "c") → 成功！✅
```

**回溯 = 试一条路，走不通就退回，换一条路再试。**

### 2.2 `.` 的实现

```python
if pattern[0] != '.' and pattern[0] != text[0]:
    return False
```

`.` 不比较内容——它匹配**任何字符**。

---

## 3. 加入 `+`、`?`、字符类 `[abc]`

```python
def match_full(pattern, text):
    """支持: . * + ? [abc]"""
    if not pattern:
        return not text
    
    # 字符类 [abc]
    if pattern[0] == '[':
        end = pattern.index(']')
        chars = pattern[1:end]
        rest = pattern[end+1:]
        if not text or text[0] not in chars:
            return False
        return match_full(rest, text[1:])
    
    # 量词
    if len(pattern) > 1:
        quantifier = pattern[1]
        
        if quantifier == '*':     # 0 次或多次
            return (match_full(pattern[2:], text) or
                    (text and match_char(pattern[0], text[0]) 
                     and match_full(pattern, text[1:])))
        
        elif quantifier == '+':   # 1 次或多次
            return (text and match_char(pattern[0], text[0]) 
                    and match_full(pattern[0] + '*' + pattern[2:], text[1:]))
        
        elif quantifier == '?':   # 0 次或 1 次
            return (match_full(pattern[2:], text) or
                    (text and match_char(pattern[0], text[0]) 
                     and match_full(pattern[2:], text[1:])))
    
    # 普通字符
    if not text:
        return False
    if not match_char(pattern[0], text[0]):
        return False
    return match_full(pattern[1:], text[1:])


def match_char(p, c):
    return p == '.' or p == c
```

---

## 4. 优化：NFA → DFA

上面的回溯算法最坏情况是**指数时间**（试了所有可能）。

真正的正则引擎（grep、Python re）用两种优化：

| 引擎类型 | 算法 | 速度 | 支持 |
|----------|------|:--:|------|
| **NFA** | 回溯（我们的） | 最坏 O(2^n) | 支持捕获组、反向引用 |
| **DFA** | 状态机编译 | O(n) 稳定 | 不支持反向引用 |

**Python 的 `re` 是 NFA，但有大量优化。** Google RE2 是 DFA，保证线性时间。

---

## 5. Ken Thompson 的 1968 年正则引擎

1968 年 Ken Thompson（Unix 之父）在 IBM 7094 上写了第一个正则引擎，只有 **400 行汇编**。核心算法到今天还在用。

他用的就是 NFA 编译成机器码——跟现代 JIT 编译一样的思想。

---

## 🔗 相关链接

- 原文: https://deniskyashif.com/2019/02/17/implementing-a-regular-expression-engine/
- Ken Thompson 1968 年论文: https://www.oilshell.org/archive/Thompson-1968.pdf
- Russ Cox 的正则系列（必读）: https://swtch.com/~rsc/regexp/regexp1.html

---

## 🖨️ 从零写一个模板引擎

> 原文：[A Template Engine](http://aosabook.org/en/500L/a-template-engine.html)

**就是 Jinja2 / Mustache 的极简版——把 `Hello {{name}}` 变成 `Hello mustafa`。**

```python
import re

class SimpleTemplate:
    """极简模板引擎：支持 {{var}} 和 {% if %} {% endif %}"""
    
    def __init__(self, template_str):
        self.template = template_str
    
    def render(self, **context):
        result = self.template
        
        # 1. 处理变量 {{var}}
        def replace_var(match):
            var_name = match.group(1).strip()
            return str(context.get(var_name, ''))
        result = re.sub(r'\{\{(.*?)\}\}', replace_var, result)
        
        # 2. 处理 {% if var %} ... {% endif %}
        def replace_if(match):
            var_name = match.group(1).strip()
            body = match.group(2)
            return body if context.get(var_name) else ''
        result = re.sub(
            r'\{%\s*if\s+(.*?)\s*%\}(.*?)\{%\s*endif\s*%\}',
            replace_if, result, flags=re.DOTALL
        )
        
        return result

# ─── 测试 ───
template = SimpleTemplate("""
Hello {{name}}!
{% if show_age %}
You are {{age}} years old.
{% endif %}
""")

print(template.render(name="mustafa", show_age=True, age=25))
# Hello mustafa!
# You are 25 years old.

print(template.render(name="mustafa", show_age=False, age=25))
# Hello mustafa!
```

**模板引擎本质 = 正则替换 + 条件判断。**

Jinja2 在此基础上加了：循环 `{% for %}`、继承 `{% extends %}`、过滤器 `{{ name|upper }}`、自动转义防 XSS、编译成 Python 代码（性能优化）。

---

## 🔗 相关链接

- 原文: http://aosabook.org/en/500L/a-template-engine.html
- Jinja2 源码: https://github.com/pallets/jinja
- Mustache 规范: https://mustache.github.io/

---

*— mustaf-osman · 学习笔记*
