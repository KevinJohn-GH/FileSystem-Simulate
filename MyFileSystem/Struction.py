class SuperBlock:
    """超级块"""
    filesystem_name = 'KevinJohn\'s FileSystem'     # 系统名称
    filesystem_version = '1.0'      # 系统版本
    block_size = 1024   # 块大小1k
    """单位块"""
    disk_size = 32      # 磁盘大小（单位块）
    group_size = 16     # 块组大小（单位块）
    group_num = disk_size / group_size      # 块组数量
    disk_used_size = 14     # 磁盘已用数量


class GTD:
    """块组描述结构"""
    SuperBlock_size = 1     # 超级块在块组中的大小（单位k）
    GTD_size = 1    # 块组描述结构在块组中占用的大小（单位k）
    BlockBitMap_size = 1    # 块位图在块组中占用的大小（单位k）
    InodeTable_size = 1     # InodeTable在块组中占用的大小（单位k）
    RootDir_size = 1    # 根目录文件在块组中占用的大小（单位k）
    UserDir_size = 1    # 用户use文件在块组用占用大小（单位k）
    UserMap_size = 1    # 用户表在块组中占用的大小（单位k）

    GTD_num = 7     # GTD占用块组的大小（单位k）
    DataBlock_size = SuperBlock.group_size - GTD_num    # 剩余数据块大小

    def __init__(self):
        self.Group_used = 7 * 1024


class Inode:
    """Inode结构"""
    def __init__(self, f_name, f_owner, f_block=[], f_is_dir=False, f_dir_father=None):
        self.f_is_dir = f_is_dir    # 是否文件目录标记
        self.f_name = f_name        # 文件名
        self.f_owner = f_owner      # 文件属主
        self.f_block = f_block      # 文件分配的数据块
        self.f_mode = ['r', 'w', 'r', '-']  # 文件模式保护码
        self.f_size = 1     # 文件大小
        self.f_dir = []     # 目录文件的子文件
        self.f_dir_father = f_dir_father    # 文件的父目录

        self.f_address = 0  # 文件起始物理地址
        # self.f_address = int(self.f_block[0][5::]) * SuperBlock.block_size * 1024


class Group:
    """块组结构"""
    SuperBlock = SuperBlock()   # 每个块组包含超级块
    BlockBitMap = {}    # 包含一个块位图
    InodeTable = {}     # 包含一个Inode表
    # Root = InodeTable['/']
    # User = InodeTable['/user']
    UserMap = {}    # 一个用户列表

    def __init__(self, gtd, Group_num):
        self.GTD = gtd
        self.Group_num = Group_num


class Process:
    """进程结构"""
    def __init__(self, P_user, P_path='/'):
        self.P_user = P_user    # 进程的创建用户
        self.P_home = '/'   # 用户家目录
        self.P_path = P_path    # 进程当前路径


class User:
    """用户结构"""
    def __init__(self, u_name, u_password, u_home='/'):
        self.u_name = u_name    # 用户名
        self.u_password =u_password # 用户密码
        self.u_home = u_home    # 用户家目录

