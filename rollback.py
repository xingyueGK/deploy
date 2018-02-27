#/usr/bin/env python
#-*- coding:utf-8 -*-

#lastversion 1.0
#2018/2/27

'''
回滚测试，使用软连接方式，快速部署回滚
可以回滚到制定版本，或是快速回滚到之前某一个版本，
项目名称的设计，能够标识每次发版，标识发版时间，什么版本；
例如：
pro_beefly_v1.0.1_20180124_101030   生产环境-项目名称-版本-发版时间
dev_beefly_v1.0.1_20180124_101030   开发环境-项目名称-版本-发版时间


输出项目访问url
'''

import os
import sys
import getopt
import time
import re
"""基础信息"""
script_name = __file__
script_pwd = os.path.split(os.path.abspath(__file__))[0]
file_pwd = os.path.split(os.path.realpath(__file__))[0]

lock_name = '/tmp/{}.lock'.format(script_name)

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
Date = time.strftime('%Y%m%d_%H%M%S')
sdir = '/home/mmuu/webapps'

def rollback_list(APPname):
    #获取制定目录的code目录
    cmd = 'tree  -L 1 %s  -d'%APPname
    os.system(cmd)
def curr_version(APPname):
    #列出制定目录的软连接的版本号
    if os.path.islink(APPname):
        print '项目版本号为：',blue(os.readlink(APPname))
    else:
        print '项目未部署'
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
def version(APPname):
    if isinstance(dict_dir[APPname],list):
        for tomcat in dict_dir[APPname]:
            try:
                dlink = "/opt/{}/webapps/{}".format(tomcat, APPname)
                if os.path.islink(dlink):
                    print '项目版本号为：', blue(os.readlink(dlink))
                else:
                    print '项目未部署'
            except KeyError as e:
                print '项目不存在', red(e)
                exit(8)
    else:
        if os.path.islink(dict_dir[APPname]):
            print '项目版本号为：', blue(os.readlink(dict_dir[APPname]))
        else:
            print '项目未部署'
def rollback(APPname,version):
    versions = re.search('_(.+?)_', version).group(1)
    if isinstance(dict_dir[APPname],list):
        for tomcat in dict_dir[APPname]:
            slink = "{}/{}/{}_{}".format(sdir,APPname, versions,tomcat)
            dlink = "/opt/{}/webapps/{}".format(tomcat, APPname)
            pro_link(slink, dlink)
    else:
        slink = "{}/{}/{}".format(sdir,dict_dir[APPname], version)
        dlink = "/opt/{}/webapps/{}".format(dict_dir[APPname], APPname)
        pro_link(slink, dlink)
def usage():
    usages='''usage:
    -h ,--help        帮助信息
    -d appname action //项目名 动作
    action 包含可选参数：
        --list        停止tomcat
        --version     当前版本使用code版本
        --restart     回滚到制定版本，版本号可选，默认上一个版本
        --rollback version     紧急回滚到上一个版本
    python deploy.py  -d appserver --status //查看appserver项目的运行状态
    '''
    print usages

if __name__ == '__main__':
    if len(sys.argv) < 4:
        usage()
        exit(1)
    try:
        options, args = getopt.getopt(sys.argv[1:], "hd:", ["help","list", "version", "rollback="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    for name, value in options:
        if name in ("-d"):
            APPname = value
        if name in ("-h", "--help"):
            usage()
        if name in ("--list"):
            project = sdir + '/' + APPname
            rollback_list(project)
        if name in ("--version"):
           version(APPname)
        if name in ("--rollback"):
            args = value
            rollback(APPname,args)
        if name in ("--restart"):
            action = 'restart'