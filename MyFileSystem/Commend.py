from Struction import Inode, Group, Process, User, SuperBlock, GTD
import os


def get_commend():
    user = login()
    #user = Process('root')
    while True:
        try:
            commend = input("%s@%s:%s$" % (user.P_user, SuperBlock.filesystem_name, user.P_path))
            commend_split = commend.split()

            if commend_split[0] == 'ls':
                ls(user)

            elif commend_split[0] == 'touch':
                touch(user, commend_split[1])

            elif commend_split[0] == 'cd':
                cd(user, commend_split[1])

            elif commend_split[0] == 'mkdir':
                mkdir(user, commend_split[1])

            elif commend_split[0] == 'rm':
                rm(user, commend_split[1])

            elif commend_split[0] == 'exit':
                break

            elif commend_split[0] == 'cat':
                cat(user, commend_split[1])

            elif commend_split[0] == 'edit':
                edit(user, commend_split[1])

            elif commend_split[0] == 'chmod':
                chmod(user, commend_split[1], commend_split[2])

            elif commend_split[0] == 'su':
                su(user, commend_split[1])

            elif commend_split[0] == 'useradd':
                useradd(user, commend_split[1])

            elif commend_split[0] == 'userdel':
                userdel(user, commend_split[1])

            elif commend_split[0] == 'help':
                help()

            elif commend_split[0] == 'disk':
                diskcheck()

            elif commend_split[0] == 'debug':
                show()

            else:
                print("not commend named %s !" % commend_split[0])

        except Exception as e:
            print('cause error:\n', e)


def load():
    """将SuperBlock、InodeTable等信息加载到内存"""

    """将SuperBlock加载到内存"""
    file = open('Disk/block0', 'r')
    line = file.readline()
    SuperBlock.filesystem_name = line.strip('\n')
    line = file.readline()
    SuperBlock.filesystem_version = line.strip('\n')
    line = file.readline()
    SuperBlock.block_size = int(line.strip('\n'))
    line = file.readline()
    SuperBlock.disk_size = int(line.strip('\n'))
    line = file.readline()
    SuperBlock.group_size = int(line.strip('\n'))
    line = file.readline()
    SuperBlock.group_num = int(line.strip('\n'))
    line = file.readline()
    SuperBlock.disk_used_size = int(line.strip('\n'))
    file.close()

    """将GTD加载到内存"""
    file = open('Disk/block1')
    line = file.readline()
    GTD.SuperBlock_size = int(line.strip('\n'))
    line = file.readline()
    GTD.GTD_size = int(line.strip('\n'))
    line = file.readline()
    GTD.BlockBitMap_size = int(line.strip('\n'))
    line = file.readline()
    GTD.InodeTable_size = int(line.strip('\n'))
    line = file.readline()
    GTD.RootDir_size = int(line.strip('\n'))
    line = file.readline()
    GTD.UserDir_size = int(line.strip('\n'))
    line = file.readline()
    GTD.UserMap_size = int(line.strip('\n'))
    line = file.readline()
    GTD.GTD_num = int(line.strip('\n'))
    line = file.readline()
    GTD.DataBlock_size = int(line.strip('\n'))
    file.close()


    """将BlockBitMap读到内存"""
    print("System loading...")
    file = open('Disk/block2', 'r')
    line = file.readline()
    while line:
        info = line.split()
        if info[1] == 'true':
            Group.BlockBitMap[info[0]] = True
        else:
            Group.BlockBitMap[info[0]] = False
        line = file.readline()
    file.close()

    """将InodeTable读到内存"""
    file = open('Disk/block3', 'r')
    line = file.readline()
    while line:
        info = line.split()
        line = file.readline()
        info2 = line.split()

        Group.InodeTable[info[1]] = Inode(info[1], info[2])
        """加载文件名，属主"""
        mode = []
        for i in info[3]:
            mode.append(i)
        Group.InodeTable[info[1]].f_mode = mode
        """加载保护码"""
        Group.InodeTable[info[1]].f_size = int(info[4])
        """加载文件大小"""
        block = []
        for b in info2:
            block.append(b)
        Group.InodeTable[info[1]].f_block = block
        """加载分配块"""
        Group.InodeTable[info[1]].f_dir_father = info[5]
        """加载父目录"""
        if info[0] == 'true':
            Group.InodeTable[info[1]].f_is_dir = True
        else:
            Group.InodeTable[info[1]].f_is_dir = False
        """加载文件类型"""
        Group.InodeTable[info[1]].f_address = hex(int(Group.InodeTable[info[1]].f_block[0][5::]) \
                                              * SuperBlock.block_size * 1024)
        """加载文件长度"""
        line = file.readline()
    file.close()

    """将目录文件读到内存"""
    for inode in Group.InodeTable:
        if Group.InodeTable[inode].f_is_dir:
            info = read_dir(inode).split()

            f = []
            for line in info:
                f.append(line.strip('\n'))
            Group.InodeTable[inode].f_dir = f

    """加载用户表"""
    file = open('Disk/block6', 'r')
    line = file.readline()
    while line:
        info = line.split()
        Group.UserMap[info[0]] = User(info[0], info[1], info[2])
        line = file.readline()

    # """系统初始化目录"""
    # Group.InodeTable['/'] = Inode('/', 'root', ['block4', ], True)
    # Group.InodeTable['/user_info'] = Inode('/user_info', 'root', ['block6', ], False)
    # Group.InodeTable['/'].f_dir.append('/user_info')
    # Group.InodeTable['/'].f_dir.append('/user')
    # Group.InodeTable['/user'] = Inode('/user', 'user', ['block5', ], True, '/')
    # Group.UserMap = {'root': User('root', 'root'),
    #                  'user': User('user', 'user', '/user')}

    print("System load finished.")


def write():
    """将SuperBlock、InodeTable等信息写回磁盘"""

    """将目录文件写回磁盘"""
    for inode in Group.InodeTable:
        if Group.InodeTable[inode].f_is_dir:
            #file = open('Disk/%s' % Group.InodeTable[inode].f_block[0], 'w')
            content = ''
            for i in Group.InodeTable[inode].f_dir:
                content = content + i + '\n'
            #print(content)
            write_dir(content, inode)
                #file.write('%s\n' % i)
            #file.close()


    """将SuperBlock写回磁盘"""
    file = open('Disk/block0', 'w')
    file.write('%s\n' % SuperBlock.filesystem_name)
    file.write('%s\n' % SuperBlock.filesystem_version)
    file.write('%d\n' % SuperBlock.block_size)
    file.write('%d\n' % SuperBlock.disk_size)
    file.write('%d\n' % SuperBlock.group_size)
    file.write('%d\n' % SuperBlock.group_num)
    file.write('%d\n' % SuperBlock.disk_used_size)
    file.close()

    """将GTD写回磁盘"""
    file = open('Disk/block1', 'w')
    file.write('%d\n' % GTD.SuperBlock_size)
    file.write('%d\n' % GTD.GTD_size)
    file.write('%d\n' % GTD.BlockBitMap_size)
    file.write('%d\n' % GTD.InodeTable_size)
    file.write('%d\n' % GTD.RootDir_size)
    file.write('%d\n' % GTD.UserDir_size)
    file.write('%d\n' % GTD.UserMap_size)
    file.write('%d\n' % GTD.GTD_num)
    file.write('%d\n' % GTD.DataBlock_size)
    file.close()


    """将BlockBitMap写回磁盘"""
    print("System exiting...")
    file = open('Disk/block2', 'w')
    for block in Group.BlockBitMap.keys():
        if Group.BlockBitMap[block]:
            file.write('%s true\n' % block)
        else:
            file.write('%s false\n' % block)
    file.close()

    """将InodeTable写回磁盘"""
    file = open('Disk/block3', 'w')
    for inode in Group.InodeTable.keys():
        if Group.InodeTable[inode].f_is_dir:
            file.write('true %s %s %s %d %s\n' % (Group.InodeTable[inode].f_name,
                                                Group.InodeTable[inode].f_owner,
                                                ''.join(Group.InodeTable[inode].f_mode),
                                                Group.InodeTable[inode].f_size,
                                                  Group.InodeTable[inode].f_dir_father))
            fw = ''
            for f in Group.InodeTable[inode].f_block:
                fw = fw + ' ' + f + ' '
            file.write(fw.strip(' ')+'\n')
        else:
            file.write('false %s %s %s %d %s\n' % (Group.InodeTable[inode].f_name,
                                                Group.InodeTable[inode].f_owner,
                                                ''.join(Group.InodeTable[inode].f_mode),
                                                Group.InodeTable[inode].f_size,
                                                  Group.InodeTable[inode].f_dir_father))
            fw = ''
            for f in Group.InodeTable[inode].f_block:
                fw = fw + ' ' + f + ' '
            file.write(fw.strip(' ')+'\n')

    file.close()


    """将用户信息写回磁盘"""
    file = open('Disk/block6', 'w')
    for user in Group.UserMap.values():
        file.write('%s %s %s\n' % (user.u_name, user.u_password, user.u_home))
    file.close()

    """更新各个块组"""
    for i in range(0, 7):
        file = open('Disk/block%d' % i, 'r')
        info = file.read()
        file.close()
        file = open('Disk/block%d' % (i+16), 'w')
        file.write(info)
        file.close()

    print("bye")


def touch(process, file_name):
    """创建普通文件"""
    if process.P_path == '/':
        file = process.P_path + file_name
    else:
        file = process.P_path + '/' + file_name
    f_owner = process.P_user
    father_path = process.P_path
    if file in Group.InodeTable.keys():
        """"存在同名文件"""
        print("%s :already exist!" % file)
        return

    block = find_block()
    if not block:
        return

    #for block in Group.BlockBitMap.keys():
    """不存在同名文件，分配block"""
    if not Group.BlockBitMap[block]:
        Group.InodeTable[file] = Inode(file, f_owner)  # 分配inode
        Group.InodeTable[father_path].f_dir.append(file)  # 父目录中记录该文件
        Group.InodeTable[file].f_dir_father = father_path
        Group.BlockBitMap[block] = True  # 分配block
        temp = []
        temp.append(block)
        Group.InodeTable[file].f_block = temp  # inode 记录block
        Group.InodeTable[file].f_address = hex(int(Group.InodeTable[file].f_block[0][5::])
                                               * SuperBlock.block_size * 1024)
        SuperBlock.disk_used_size += 1  # 磁盘消耗+1
    else:
        print('disk error!')
    #break


def mkdir(process, dir_name):
    """创建目录文件"""
    touch(process, dir_name)
    if process.P_path == '/':
        file = process.P_path + dir_name
    else:
        file = process.P_path + '/' + dir_name
    Group.InodeTable[file].f_is_dir = True

# 可以使用绝对路径
def rm(process, delete_file):
    """删除文件"""
    delete_list = []  # 用于记录需要删除的inode

    def rm_i(delete_file_i):
        file = delete_file_i
        if file in Group.InodeTable.keys():
            if Group.InodeTable[file].f_is_dir:
                """若删除的是目录文件"""
                delete_list.append(file)    # 删除表添加inode
                for i in Group.InodeTable[file].f_dir:
                    """遍历目录的全部文件"""
                    rm_i(i)  # 递归
            else:
                """若删除的是普通文件"""
                delete_list.append(file)  # 删除表添加inode

    if delete_file == '/':
        print("cant not remove root file")
        return 0

    whole_file = delete_file    # 若输入的是绝对路径
    if process.P_path == '/':
        rela_path = process.P_path + delete_file
    else:
        rela_path = process.P_path + '/' + delete_file

    if rela_path in Group.InodeTable[process.P_path].f_dir:
        """若输入的是相对路径"""

        if Group.InodeTable[rela_path].f_owner == process.P_user or process.P_user =='root':
            """属主和root才能删除文件"""
            Group.InodeTable[process.P_path].f_dir.remove(rela_path)
            """父目录中删除该文件记录"""
            rm_i(rela_path)
        else:
            print('permission denied!')

    elif whole_file not in Group.InodeTable.keys():
        print("no such file:%s" % whole_file)
    else:
        if Group.InodeTable[whole_file].f_owner == process.P_user:
            """属主才能删除文件"""
            Group.InodeTable[process.P_path].f_dir.remove(whole_file)
            """父目录中删除该文件记录"""
            rm_i(whole_file)
        else:
            print('permission denied!')


    for i in delete_list:
        for fblock in Group.InodeTable[i].f_block:
            Group.BlockBitMap[fblock] = False  # 释放block
            SuperBlock.disk_used_size -= 1
            file = open('Disk/%s' % fblock, 'w')
            file.close()
        Group.InodeTable.pop(i)  # 释放inode


def ls(process):
    """根据进程当前目录，打印输出目录内容"""
    # whole_path = dir_name   # 若获取的是绝对路径
    # if dir_name == '/':
    #     rela_path = process.P_path + dir_name
    # else:
    #     rela_path = process.P_path + '/' + dir_name
    # if rela_path in Group.InodeTable[process.P_path].f_dir:
    #     path = rela_path
    # elif whole_path not in Group.InodeTable.keys():
    #     print("%s :not such directory" % dir_name)
    # else:
    #     path = whole_path
    path = process.P_path
    if path in Group.InodeTable:
        for i in Group.InodeTable[path].f_dir:
            if Group.InodeTable[i].f_is_dir:
                print('d%s %s\t%sKb\t%s\t%s' % (''.join(Group.InodeTable[i].f_mode),
                                        Group.InodeTable[i].f_owner,
                                        Group.InodeTable[i].f_size,
                                        Group.InodeTable[i].f_address,
                                        # hex(int(Group.InodeTable[i].f_address, 16)*1024),
                                        i.split('/')[-1]))
            else:
                print('-%s %s\t%sKb\t%s\t%s' % (''.join(Group.InodeTable[i].f_mode),
                                        Group.InodeTable[i].f_owner,
                                        Group.InodeTable[i].f_size,
                                        Group.InodeTable[i].f_address,
                                        # hex(int(Group.InodeTable[i].f_address, 16)*1024),
                                        i.split('/')[-1]))

# 可以使用绝对路径
def cd(process, path):
    """切换路径"""
    whole_path = path       # 若输入的是绝对路径
    if process.P_path == '/':
        rela_path = process.P_path + path
    else:
        rela_path = process.P_path + '/' + path


    if path == '..':
        """返回上一层目录"""
        if process.P_path == '/':
            return 0
        process.P_path = Group.InodeTable[process.P_path].f_dir_father

    elif rela_path in Group.InodeTable[process.P_path].f_dir:
        """目标文件存在当前目录"""
        if not Group.InodeTable[rela_path].f_is_dir:
            print('%s : Not such directory!' % whole_path)
            return
        process.P_path = rela_path

    elif whole_path not in Group.InodeTable.keys():
        """不存在该绝对路径"""
        print('%s :cd Not such directory!' % whole_path)
        return 0

    elif Group.InodeTable[path].f_is_dir:
        """存在该绝对路径"""
        if not Group.InodeTable[path].f_is_dir:
            print('%s : Not such directory!' % whole_path)
            return
        process.P_path = whole_path
    else:
        print('%s is not a directory' % path)


def get_ap(process):
    # whole_path = []
    # now_path = process.P_path
    # whole_path.append(now_path)
    # father_path = Group.InodeTable[now_path].f_dir_father
    # while father_path:
    #     whole_path.append(father_path)
    #     father_path = Group.InodeTable[father_path].f_dir_father
    # path = ''
    # for i in whole_path:
    #     path = path + '/' + i
    # path = path.strip('/')
    # return '/' + path[len(path)-1::-1]
    return process.P_path


def login():
    """用户登陆"""
    while True:
        username = input('username:')
        password = input('password:')
        if username in Group.UserMap.keys():
            if Group.UserMap[username].u_password == password:
                process = Process(username, Group.UserMap[username].u_home)
                print("welcome to MyFileSystem...")
                return process
            print('wrong password, please try again')
        else:
            print('permission denied, please try again')


def show():
    """debug功能，用于查看当前BlockBitMap等信息"""
    print(Group.BlockBitMap)
    for i in Group.InodeTable.values():
        print('%s\t%s\t%s\t%s\t%s' % (i.f_name, i.f_block, i.f_dir, i.f_is_dir, i.f_dir_father))
    print(Group.UserMap)


def cat(process, filename):
    path = change_path(process, filename)
    if not r_ver(process, path):
        """验证读权限"""
        return
    info = ''
    for i in Group.InodeTable[path].f_block:
        file = open('Disk/%s' % i, 'r')
        info = info + file.read()
        file.close()
    print(info)


def edit(process, filename):
    """编辑文件"""
    path = change_path(process, filename)

    if path not in Group.InodeTable.keys():
        print('%s :new file.' % filename)
        touch(process, filename)

    if Group.InodeTable[path].f_is_dir:
        """目录文件不可编辑"""
        print('%s :not writable!' % filename)

    if not w_ver(process, path):
        """验证写权限"""
        return

    print('content:')
    cat(process, filename)

    content = input('new content:\n')
    content_cut = cut_text(content)
    if len(content_cut) == 0:
        """第一个block不需释放，故先写入内容"""
        file = open('Disk/' + Group.InodeTable[path].f_block[0], 'w')
        file.close()
    else:
        file = open('Disk/' + Group.InodeTable[path].f_block[0], 'w')
        file.write(content_cut[0])
        file.close()
    for block in Group.InodeTable[path].f_block[1::]:
        """先释放原来的block"""
        phy_path = 'Disk/' + block
        file = open(phy_path, 'w')
        file.close()
        Group.BlockBitMap[block] = False
        Group.SuperBlock.disk_used_size -= 1
        Group.InodeTable[path].f_block.remove(block)

    for i in content_cut[1::]:
        """将切割后的文本内容逐个写到各个block中"""
        block = find_block()
        phy_path = 'Disk/' + block
        file = open(phy_path, 'w')
        file.write(i)
        file.close()
        Group.BlockBitMap[block] = True
        Group.InodeTable[path].f_block.append(block)
        SuperBlock.disk_used_size += 1

    Group.InodeTable[path].f_size = len(Group.InodeTable[path].f_block)
    Group.InodeTable[path].f_address = hex(int(Group.InodeTable[path].f_block[0][5::])
                                           * SuperBlock.block_size * 1024)
    """更新文件大小"""
    print('new content:')
    cat(process, filename)


def change_path(process, filename):
    """对用户输入的文件名，转换称唯一的Inode名"""
    if process.P_path == '/':
        path = process.P_path + filename
    else:
        path = process.P_path + '/' + filename

    return path


def r_ver(process, path):
    """判断是否可读"""
    if process.P_user == 'root':
        """root什么都可以读"""
        return True
    if process.P_user == Group.InodeTable[path].f_owner:
        if Group.InodeTable[path].f_mode[0] == 'r':
            return True
        else:
            print('read permission denied')
            return False
    elif Group.InodeTable[path].f_mode[2] == 'r':
        return True
    else:
        print('read permission denied')
        return False


def w_ver(process, path):
    """判断是否可写"""
    if process.P_user == 'root':
        return True
    if process.P_user == Group.InodeTable[path].f_owner:
        if Group.InodeTable[path].f_mode[1] == 'w':
            return True
        else:
            print('write permission denied')
            return False
    elif Group.InodeTable[path].f_mode[3] == 'w':
        return True
    else:
        print('write permission denied!')
        return False


def chmod(process, filename, mode):
    """更改保护模式码"""
    path = change_path(process, filename)
    if process.P_user == 'root' or Group.InodeTable[path].f_owner == path:
        """root和文件属主才能修改文件权限"""
        Group.InodeTable[path].f_mode = mode
    else:
        print('permission denied!')


def su(process, username):
    """切换用户"""
    if username in Group.UserMap.keys():
        process.P_user = username
        process.P_home = Group.UserMap[username].u_home
    else:
        print('no user named %s' % username)


def useradd(process, username):
    """添加用户"""
    if process.P_user != 'root':
        print('permission denied!')
        return
    password = input('password:')
    path = '/' + username
    Group.UserMap[username] = User(username, password, path)
    if path in Group.InodeTable.keys():
        return
    tem_process = Process('root', '/')
    mkdir(tem_process, username)


def userdel(process, username):
    Group.UserMap.pop(username)
    print('%s :delete successfully' % username)


def find_block():
    """求出应该分配的块"""
    if SuperBlock.disk_used_size == SuperBlock.disk_size:
        print("The disk is full!")
        return False
    # group_num = (SuperBlock.disk_used_size - SuperBlock.group_num * GTD.GTD_num) // GTD.DataBlock_size
    # group_addr = (SuperBlock.disk_used_size - SuperBlock.group_num * GTD.GTD_num) % GTD.DataBlock_size + 7
    # block_allo = group_num * SuperBlock.group_size + group_addr
    # block = 'block%d' % block_allo
    block = ''
    for b in Group.BlockBitMap.keys():
        if not Group.BlockBitMap[b]:
            block = b
            break

    return block


def cut_text(txt):
    """按块大小分隔文件内容"""
    b = []
    a = ''
    count = 0
    C = 0
    for i in txt:
        C += 1
        count += 1
        a = a + i
        if count == (SuperBlock.block_size/8) or C == len(txt):
            b.append(a)
            a = ''
            count = 0
    return b


def write_dir(f_block, path):
    """编写文件内容，并分配合适的数据块"""
    content = f_block
    content_cut = cut_text(content)
    if len(content_cut) == 0:
        """第一个block不需释放，故先写入内容"""
        file = open('Disk/' + Group.InodeTable[path].f_block[0], 'w')
        file.close()
    else:
        file = open('Disk/' + Group.InodeTable[path].f_block[0], 'w')
        file.write(content_cut[0])
        file.close()
    for block in Group.InodeTable[path].f_block[1::]:
        """先释放原来的block"""
        phy_path = 'Disk/' + block
        file = open(phy_path, 'w')
        file.close()
        Group.BlockBitMap[block] = False
        Group.SuperBlock.disk_used_size -= 1
        Group.InodeTable[path].f_block.remove(block)

    for i in content_cut[1::]:
        """将切割后的文本内容逐个写到各个block中"""
        block = find_block()
        phy_path = 'Disk/' + block
        file = open(phy_path, 'w')
        file.write(i)
        file.close()
        Group.BlockBitMap[block] = True
        Group.InodeTable[path].f_block.append(block)
        SuperBlock.disk_used_size += 1

    Group.InodeTable[path].f_size = len(Group.InodeTable[path].f_block)
    Group.InodeTable[path].f_address = hex(int(Group.InodeTable[path].f_block[0][5::])
                                           * SuperBlock.block_size * 1024)


def read_dir(dirname):
    """遍历数据块，返回完整文件内容"""
    info = ''
    for i in Group.InodeTable[dirname].f_block:
        file = open('Disk/%s' % i, 'r')
        info = info + file.read()
        file.close()
    return info


def diskcheck():
    print('*************************磁盘信息***************************')
    print('文件系统：%s' % SuperBlock.filesystem_name)
    print('版本：%s' % SuperBlock.filesystem_version)
    print('块大小：%d' % SuperBlock.block_size)
    print('块组大小：%dKb' % SuperBlock.group_size)
    print('块组数量：%d' % SuperBlock.group_num)
    print('磁盘总量：%dKb' % SuperBlock.disk_size)
    print('已用: %dKb' % SuperBlock.disk_used_size)
    print('系统占用： %sKb' % (SuperBlock.group_num*GTD.GTD_num))
    print('***********************************************************')



def help():
    print('*************************帮助手册***************************')
    print('*名称          参数          描述                           ')
    print('*ls                          列出当前目录                   ')
    print('*cd            *filename     切换路径           ')
    print('*touch         filename      创建文件，不可与当前目录下有同名文件')
    print('*mkdir         filename      在当前目录创建文件夹              ')
    print('*rm            *filename     删除文件')
    print('*cat           filename      输出文件内容')
    print('*edit          filename      编辑指定文件，若当前目录下无该文件，则创建一个新的文件')
    print('*useradd       username      创建新用户')
    print('*userdel       username      删除用户，但不会删除用户目录')
    print('*su            username      切换用户')
    print('*chmod         filename mode 更改文件权限')
    print('*disk                        查看磁盘信息')
    print('*exit                        退出系统，并保存系统上下文')
    print('*debug                       开发人员工具')
    print('***********************************************************')



