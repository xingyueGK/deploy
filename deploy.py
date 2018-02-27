#!/usr/bin/env python
#-*- coding:utf-8 -*-
#lastversion 2.0
#20180227

'''
多个项目部署
回滚测试，使用软连接方式，快速部署回滚
可以回滚到制定版本，或是快速回滚到置顶
某一个版本，
项目名称的设计，能够标识每次发版，标识发版时间，什么版本；
例如：
pro_beefly_v1.0.1_20180124_101030   生产环境-项目名称-版本-发版时间
dev_beefly_v1.0.1_20180124_101030   生产环境-项目名称-版本-发版时间


输出项目访问url
'''

import os
import sys
import getopt
import time
import shutil


def make_color(code):
    def color_func(s):
        tpl = '\x1b[{}m{}\x1b[0m'
        return tpl.format(code, s)
    return color_func
red = make_color(31)
green = make_color(32)
yellow = make_color(33)
blue = make_color(34)
magenta = make_color(35)
cyan = make_color(36)

'''只需要修改dict对应目录即可'''
dict_dir = {
    "appserver":["tomcat-appserver-8080","tomcat-appserver-8081"],
    "trade":"tomcat-trade-8085",
    "upms":"tomcat-upms-8082",
    "yunying":"tomcat-yunying-8086",
    "fk-server":"tomcat-fk-server-8084",
    "yyserver":"tomcat-yyserver-8083",
    "diqin-admin":"tomcat-diqin-admin-8088",
    "account": "tomcat-account-8090",
    "activity": "tomcat-activity-8092",
    "activityserver": "tomcat-activityserver-8093",
    "battery": "tomcat-battery-8091",
    "diqin": "tomcat-diqin-8094",
    "diqinserver": "tomcat-diqinserver-8095",
    "order": "tomcat-order-8096",
    "user": "tomcat-user-8097",
    "fkadmin":"tomcat-fkadmin-server-8081"
}
Date = time.strftime('%Y%m%d_%H%M')
sdir = '/home/mmuu/webapps'
if not os.path.exists(sdir):
    try:
        os.makedirs(sdir)
        print '创建目录 %s 成功' % blue(sdir)
    except OSError as e:
        print red(e)
"""获取文件绝对路径"""
file_pwd = os.path.split(os.path.realpath(__file__))[0]
class BaseENV():
    def __init__(self,APPname,version=''):
        """
        :param APPname: 项目名称
        :param tomcat: tomcat名称
        :param version: 发版版本号
        :path  /home/mmuu/webapps/appserver/appserver_20180207_145634
        :paht  self.s_war_dir/self.pro_code_version_name
        """
        self.s_war_dir = os.path.join(sdir,APPname)#以每一个app名字存储代码
        """代码存放目录，每个版本目录不同beefly_3.1.2_20180129_181323"""
        self.pro_code_version_name = '{}_{}_{}'.format(APPname,version,Date)#发版名字
        #version = self.pro_code_version_name
        # if os.listdir(version):
        #     info = '当前版本{}已存在是否要删除Y/N：'.format(version)
        #     print info
        #     arg = raw_input(info)
        #     if arg in ('Nn'):
        #         exit(2)
        #     else:
        #         print '删除当前版本{}'.format(version)
        #         cmd = 'rm -rf {}'.format(version)
        #         os.system(cmd)
        # 源代码存放绝对目录
        self.pro_code_dir = os.path.join(self.s_war_dir, self.pro_code_version_name)
        if not os.path.exists(self.s_war_dir):
            os.makedirs(self.s_war_dir)
        if not os.path.exists(self.pro_code_dir):
            print '文件不存在创建目录 {}'.format(blue(self.pro_code_dir))
            os.makedirs(self.pro_code_dir)
def unzip_package(codeDir,codeVersionName):
    '''更新部署项目,拷贝最新包并创建新目录并解压包'''
    try:
        os.chdir(codeDir)
        s_list_dir = os.listdir(codeDir)
        for file in s_list_dir:
            if file.endswith('war'):
                # tomcat 项目存放地址地址
                packname = file
                cmd = 'unzip  {} -d {} >/dev/null'.format(codeDir + "/" + packname,codeVersionName)
                print '解压文件 {} 到目录 {} \n'.format(red(packname), blue(codeVersionName))
                print cmd
                os.system(cmd)
            else:
                print '项目war包不存在，请检查'
                sys.exit(3)
    except OSError as e:
        print  red(e)
        sys.exit(3)
    except IOError as io:
        print red(io)
        sys.exit(4)
def pro_link(slink,dlink):
    """创建新的链接到生产环境，并删除旧的链接"""
    if os.path.islink(dlink):
        print '%s 链接已经存在,删除旧的重新建立'%cyan(dlink)
        cmd = 'rm -rf  %s' %(dlink)
        print '执行命令: {}'.format(green(cmd))
        os.system(cmd)
    cmd='ln -sv %s %s'%(slink,dlink)
    print green(cmd)
    os.system(cmd)
    print '创建新的链接 %s'%cyan(dlink)
def Tomcat(APPname,action,file_pwd=file_pwd):
    if isinstance(dict_dir[APPname], list):
        for tomcat in dict_dir[APPname]:
            web = '/opt/' + tomcat
            cmd = '/usr/bin/sh {}/tomcat.sh {} {}'.format(file_pwd, web, action)
            print 'tomcat shellcmd:{}'.format(green(cmd))
            os.system(cmd)
    else:
        web = '/opt/' + dict_dir[APPname]
        cmd = '/usr/bin/sh {}/tomcat.sh {} {}'.format(file_pwd, web, action)
        print 'tomcat shellcmd:{}'.format(green(cmd))
        os.system(cmd)

def usage():
    usages='''usage:
    -h ,--help        帮助信息
    -d appname action //项目名 动作
    -v version        版本号
    action 包含可选参数：
        --stop        停止tomcat
        --start       启动tomcat
        --status      查看状态信息
        --restart     重启tomcat
        --deploy     重新部署，并重启tomcat
    python deploy.py  -d appserver -v v1.2.3 --status//查看appserver项目的运行状态
    '''
    print usages
def main():
    if len(sys.argv) < 3:
        usage()
        exit(1)
    try:
        options, args = getopt.getopt(sys.argv[1:], "hd:v:", ["help","deploy", "stop", "start", "status","restart","version="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    for name, value in options:
        if name in ("-h", "--help"):
            usage()
        if name in ("-d"):
            APPname = value
        if name in ("-v","version"):
            version = value
        if name in ("--stop"):
            action = 'stop'
            Tomcat(APPname, action)
        if name in ("--start"):
            action = 'start'
            Tomcat(APPname, action)
        if name in ("--status"):
            action = 'status'
            Tomcat(APPname,action)
        if name in ("--restart"):
            action = 'restart'
            Tomcat(APPname, action)
        if name == "--deploy":
            action = 'restart'
            # 执行shell脚本tomcat.sh
            if isinstance(dict_dir[APPname],list):
                base = BaseENV(APPname, version)
                unzip_package(base.s_war_dir, base.pro_code_dir)
                for tomcat in dict_dir[APPname]:
                    #复制code，直接修改配置文件配置文件
                    cp_code = '{version}_{code}'.format(version=version,code=tomcat)
                    if os.path.exists(cp_code):
                        shutil.rmtree(cp_code)
                    cmd = 'cp -r {} {}'.format(base.pro_code_dir,cp_code)
                    print '拷贝源代码 {} 到 {}'.format(blue(base.pro_code_dir),blue(cp_code))
                    print green(cmd)
                    os.system(cmd)
                    #修改dubbo.protoco.port端口号
                    port = tomcat[-4:]
                    conf='WEB-INF/classes/config.properties'
                    abspath_cp_code = '{}/{}'.format(base.s_war_dir,cp_code)
                    cmd = "sed -ir '/dubbo.protoco.port=/cdubbo.protoco.port={}' {}/{}".format(port,abspath_cp_code,conf)
                    pro_dir_name = '/opt/{}/webapps/{}'.format(tomcat,APPname)# tomcat项目名字
                    print green(cmd)
                    os.system(cmd)
                    pro_link(abspath_cp_code,pro_dir_name)
                #重启tomcat
                Tomcat(APPname,action)
            else:
                base = BaseENV(APPname,version)
                unzip_package(base.s_war_dir, base.pro_code_dir)
                pro_dir_name = '/opt/{}/webapps/{}'.format(dict_dir[APPname],APPname) # tomcat项目名字
                pro_link(base.pro_code_dir,pro_dir_name)
                # 执行脚本
                Tomcat(APPname, action)
if __name__ == '__main__':
    main()