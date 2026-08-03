# 🐳 从零写一个 Docker — 逐行详解

> 原文：[Linux containers in 500 lines](https://blog.lizzie.io/linux-containers-in-500-loc.html) + [Build Your Own Container in Go](https://www.infoq.com/articles/build-a-container-golang)
>
> Docker 看起来像魔法——一条命令就隔离出一个完整的 Linux 环境。但底层原理就几样东西。写完你会明白容器不是什么黑科技。

---

## 0. 先搞懂：Docker 到底是什么？

```bash
$ docker run -it ubuntu bash
root@abc123:/# ls
bin  boot  dev  etc  home  lib  ...
root@abc123:/# exit
```

这个 `ubuntu` 容器跟你宿主机用**同一个 Linux 内核**，但它的进程以为自己独占一台机器。

**Docker 靠三个 Linux 内核特性实现隔离：**

| 特性 | 作用 | 类比 |
|------|------|------|
| **Namespace（命名空间）** | 隔离"能看到什么" | 给每个进程一间独立房间 |
| **Cgroup（控制组）** | 限制"能用多少" | 给每个房间限制用水用电量 |
| **chroot / pivot_root** | 隔离文件系统 | 每个房间有自己的家具 |

**Namespace 有六种：**

| Namespace | 隔离什么 |
|-----------|---------|
| PID | 进程 ID——容器里的 PID 1 不是宿主机的 PID 1 |
| NET | 网络——容器有自己独立的网卡、IP |
| MNT | 挂载点——容器看不到宿主机的 `/proc` |
| UTS | 主机名——容器可以叫 `abc123`，宿主机叫 `server01` |
| IPC | 进程间通信 |
| USER | 用户——容器里 root ≠ 宿主机 root |

---

## 1. 最小容器（Python 版，30 行）

下面的代码创建一个隔离的进程——它以为自己是整台机器上唯一的进程。

```python
import os
import subprocess
import sys

def run_container(cmd, rootfs='./rootfs'):
    """
    用 Linux namespace 隔离运行一个命令
    需要 root 权限！用 sudo 跑
    """
    # 1. 创建新的 namespace（PID + UTS + MNT）
    # CLONE_NEWPID  = 0x20000000  → 隔离进程ID
    # CLONE_NEWUTS  = 0x04000000  → 隔离主机名
    # CLONE_NEWNS   = 0x00020000  → 隔离挂载点
    flags = 0x20000000 | 0x04000000 | 0x00020000
    
    # 2. 克隆进程，传入新的 namespace
    pid = os.fork()
    
    if pid == 0:  # 子进程 = 容器
        # 3. 进入新的 namespace
        import ctypes
        LIBC = ctypes.CDLL('libc.so.6')
        LIBC.unshare(flags)
        
        # 4. 挂载 /proc（容器自己的）
        os.system('mount -t proc proc /proc')
        
        # 5. 设置主机名
        os.sethostname('container')
        
        # 6. 运行命令
        os.execvp(cmd[0], cmd)
    else:
        # 父进程等待子进程结束
        os.waitpid(pid, 0)

if __name__ == '__main__':
    if os.geteuid() != 0:
        print("需要 root 权限！用 sudo python container.py bash")
        sys.exit(1)
    run_container(sys.argv[1:])
```

### 🏃 在 Linux 上跑

```bash
# 需要 Linux 环境（RK3588 板子就行）
$ sudo python container.py bash

root@container:/# ps aux       # 只能看到容器内部的进程！
USER       PID  CPU  MEM
root         1   0.0   0.0   bash        ← 我是 PID 1！
root         2   0.0   0.0   ps aux

root@container:/# hostname     # 容器的主机名
container

root@container:/# exit
```

**看到了吗？** 容器里 `bash` 的 PID 是 1，但在宿主机上它可能是 PID 28471。

---

## 2. 加上文件系统隔离（chroot + overlayfs）

真正的 Docker 容器不是共享宿主机文件的——它有自己完整的文件系统。

```bash
# 1. 下载一个最小 rootfs（Alpine Linux）
mkdir rootfs
cd rootfs
wget https://dl-cdn.alpinelinux.org/alpine/v3.19/releases/x86_64/alpine-minirootfs-3.19.0-x86_64.tar.gz
tar xzf alpine-minirootfs-*.tar.gz

# 2. chroot 进入隔离的文件系统
sudo chroot rootfs /bin/sh

/ # ls
bin  dev  etc  home  lib  media  mnt  opt  proc  root  run  sbin  srv  sys  tmp  usr  var

/ # cat /etc/os-release
NAME="Alpine Linux"
VERSION_ID=3.19.0

/ # exit
```

**chroot** 把 `/` 目录"改"成了 `./rootfs`。进程看不到 rootfs 外面的任何文件。

---

## 3. 加上资源限制（cgroup）

```python
def setup_cgroup(pid, memory_limit_mb=128, cpu_shares=512):
    """给容器限制内存和 CPU"""
    # 创建 cgroup
    cgroup_path = f'/sys/fs/cgroup/container-{pid}'
    os.makedirs(cgroup_path, exist_ok=True)
    
    # 内存限制: 128MB
    with open(f'{cgroup_path}/memory.max', 'w') as f:
        f.write(f'{memory_limit_mb * 1024 * 1024}')
    
    # CPU 权重（默认 1024，512 = 一半）
    with open(f'{cgroup_path}/cpu.weight', 'w') as f:
        f.write(str(cpu_shares))
    
    # 把进程加入 cgroup
    with open(f'{cgroup_path}/cgroup.procs', 'w') as f:
        f.write(str(pid))
```

---

## 4. 完整的容器脚本（100 行）

```python
#!/usr/bin/env python3
"""
mini-docker: 一个 100 行的容器运行时
用法: sudo python mini-docker.py run <image_dir> <command>
示例: sudo python mini-docker.py run ./alpine-rootfs /bin/sh
"""
import os
import sys
import ctypes
import stat

LIBC = ctypes.CDLL('libc.so.6', use_errno=True)

# Linux namespace 常量
CLONE_NEWNS   = 0x00020000  # Mount namespace
CLONE_NEWUTS  = 0x04000000  # UTS namespace
CLONE_NEWPID  = 0x20000000  # PID namespace
CLONE_NEWNET  = 0x40000000  # Network namespace

MS_REC = 0x4000
MS_PRIVATE = 1 << 18

def unshare(flags):
    """调用 Linux unshare 系统调用"""
    result = LIBC.unshare(flags)
    if result != 0:
        err = ctypes.get_errno()
        raise OSError(err, os.strerror(err))

def mount(source, target, fstype, flags=0, data=''):
    """调用 Linux mount 系统调用"""
    result = LIBC.mount(source.encode(), target.encode(),
                        fstype.encode(), flags, data.encode())
    if result != 0:
        err = ctypes.get_errno()
        raise OSError(err, os.strerror(err))

def pivot_root(new_root, old_root):
    """调用 Linux pivot_root 系统调用"""
    result = LIBC.pivot_root(new_root.encode(), old_root.encode())
    if result != 0:
        err = ctypes.get_errno()
        raise OSError(err, os.strerror(err))

def run_container(image_path, cmd):
    # 1. 创建新的 namespace
    unshare(CLONE_NEWNS | CLONE_NEWUTS | CLONE_NEWPID | CLONE_NEWNET)
    
    # 2. 设置主机名
    os.sethostname('container')
    
    # 3. 让挂载点私有化（不影响宿主机）
    mount(None, '/', None, MS_REC | MS_PRIVATE)
    
    # 4. 挂载镜像文件系统
    image_path = os.path.abspath(image_path)
    mount(image_path, image_path, None, 0x4000 | 0x8000)  # MS_BIND | MS_REC
    
    # 5. 创建 old_root 目录
    old_root = os.path.join(image_path, '.old_root')
    os.makedirs(old_root, exist_ok=True)
    
    # 6. 切换根文件系统
    os.chdir(image_path)
    pivot_root('.', '.old_root')
    
    # 7. 卸载旧的根文件系统
    os.chdir('/')
    LIBC.umount2('/.old_root', 2)  # MNT_DETACH
    os.rmdir('/.old_root')
    
    # 8. 挂载 /proc（容器自己的）
    os.makedirs('/proc', exist_ok=True)
    mount('proc', '/proc', 'proc')
    
    # 9. 挂载 /sys
    os.makedirs('/sys', exist_ok=True)
    mount('sysfs', '/sys', 'sysfs')
    
    # 10. 执行命令
    os.execvp(cmd[0], cmd)

if __name__ == '__main__':
    if os.geteuid() != 0:
        print("需要 root 权限！")
        sys.exit(1)
    if len(sys.argv) < 4 or sys.argv[1] != 'run':
        print("用法: sudo python mini-docker.py run <image_dir> <command>")
        sys.exit(1)
    run_container(sys.argv[2], sys.argv[3:])
```

---

## 5. Docker 架构 vs 我们的实现

```
真正的 Docker               我们的 mini-docker
─────────────────          ──────────────────
docker daemon   (后台服务)   直接跑 Python 脚本
containerd      (容器管理)   无
runc            (OCI 运行时)  我们的 python 脚本 ≈ runc
镜像 registry   (Docker Hub) 手动下载 tar.gz
分层镜像        (overlayfs)   单层目录
网络            (bridge/NAT)  CLONE_NEWNET（隔离但没配网络）
```

**runc 是真正的"创建容器"的部分——它只做一件事：** 调用 Linux namespace + cgroup + chroot 创建隔离进程。Docker daemon 负责镜像管理、网络配置、日志收集等外围功能。

---

## 6. 跟你的 RK3588 的关系

你在板子上部署 rp_server 时需要：
- **环境隔离**：测试服和正式服不互相污染
- **依赖管理**：Python 版本、系统库版本不冲突
- **快速恢复**：出问题能一键回滚

容器化部署是标准做法。理解底层原理后，你 debug 容器问题（"为什么 /proc 读不到？""为什么网络不通？"）就知道从哪下手了。

---

## 🔗 相关链接

- Linux containers in 500 LOC: https://blog.lizzie.io/linux-containers-in-500-loc.html
- Build Your Own Container in Go: https://www.infoq.com/articles/build-a-container-golang
- Docker 源码阅读: https://github.com/opencontainers/runc
- 中文 Docker 底层原理: https://draveness.me/docker/

---

*— mustaf-osman · 学习笔记*
