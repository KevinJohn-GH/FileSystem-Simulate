# 模拟文件系统



## 概述

该文件系统以ext2文件系统为原型。模拟了文件系统分配磁盘空间、创建文件、删除文件、创建目录等功能。

同时模仿linux系统，添加了增加用户、删除用户、用户登陆、用户权限、用户家目录等特点。

总代码量约为800行



## 使用环境

Linux或windows

语言：Python3.7

IDE：pycharm



## 项目文件说明

##### /Disk

block0 superblock # 超级块，存储文件系统信息
block1 GTD # 块组描述块，描述块内信息
block2 BlockBitMap # 块图，记录整个磁盘块的使用
block3 InodeTable # Inode表，记录全部文件inode结点信息
block4 / # 分配给根目录的数据块（同时也是root用户的家目录）
block5 /user # 用户user的家目录
block6 user info # 用户信息表，存储所有用户信息

>Disk目录是模拟的磁盘目录，总共分配了32个数据块，每个数据块大小为1k。
>
>分了两个块组。每个块组为16k。每个块组前7个块（block0~block6）为系统块。

##### /main.py
**执行文件入口**

##### /Strcution.py

**项目使用的数据结构**

##### /Commend.py

**项目模拟的文件系统功能，以及一些逻辑处理。**



## 使用说明

使用``python3 main.py``运行文件系统。

注意：运行前请确保Disk目录下的文件完整，block0~block31，缺少的为空文件，请自行创建



## 命令说明

``help``	输入help查看系统命令



## 磁盘分配说明

一个文件分配一个数据块。

目录文件是一种内容结构固定的文件，本质也是一个文件。

若文件内容大于1k，即多余128个字节，则分配多个块存储该文件内容。

数据块最多存储128个字节。



## 文件系统默认参数

```
文件系统：KevinJohn's FileSystem
版本：1.0
块大小：1024
块组大小：16Kb
块组数量：2
磁盘总量：32Kb
已用: 14Kb
系统占用： 14Kb
```

**登陆账号：**

账户：root 密码：root

账户：user 密码：user



## 心得记录

本项目为操作系统的课程设计题目，总共历时五天完成



day1 查资料理解文件系统关于磁盘分配原理，Superblock、Inode、GTD等概念

day2 编写结构体，Group、inode、InodeBitMap、BlockBitMap等

day3 编写逻辑层代码，包括各种文件的各种命令，``cd``、``touch``、``mkdir``等功能

day4 发现结构体漏洞，无法实现不同文件夹下同名文件共存问题，对结构体进行改善

day5 完善SuperBlock、GTD等数据块的内容，并编写help命令，测试查找bug，完善整个系统



由于本次实验开始毫无头绪，导致整个实验过程比较曲折。自发现结构体出现漏洞之后，完善了结构体后，

又需要对已经写好的逻辑层进行修改，而此时逻辑层已经完成60%左右。



本人认为本课设最难的地方在于设计结构体，若一开始的整体构思比较完整，Inode等结构体写的比较完善的话，逻辑层的编写会变得顺畅许多，代码也会更简洁，冗余程度将会大大降低。比如创建目录等需要分配数据块的操作，可以直接嵌套一个``touch``命令。



## 参考资料

<https://www.ibm.com/developerworks/cn/linux/filesystem/ext2/index.html>

<https://zhuanlan.zhihu.com/p/53027856>

<https://www.cnblogs.com/alantu2018/p/8472105.html>

<https://www.jianshu.com/p/3355a35e7e0a>
