#!/bin/bash  
#  
# chkconfig: - 95 15   
# description: Tomcat start/stop/status script  
#last 20180130
#修改64行处判为空后  
#Location of JAVA_HOME (bin files)  
export JAVA_HOME="/usr/lib/jvm/java-1.8.0-openjdk-1.8.0.102-4.b14.el7.x86_64"  
export JRE_HOME=$JAVA_HOME/jre
  
#Add Java binary files to PATH  
export PATH=$JAVA_HOME/jre/bin:$PATH  
  
#CATALINA_HOME is the location of the configuration files of this instance of Tomcat  
CATALINA_HOME=$1
  
#TOMCAT_USER is the default user of tomcat  
TOMCAT_USER=mmuu
  
#TOMCAT_USAGE is the message if this script is called without any options  
TOMCAT_USAGE="Usage: $0 {\e[00;32mstart\e[00m|\e[00;31mstop\e[00m|\e[00;32mstatus\e[00m|\e[00;31mrestart\e[00m}"  
  
#SHUTDOWN_WAIT is wait time in seconds for java proccess to stop  
SHUTDOWN_WAIT=3
#SCRIPT_NAME 获取脚本的名字，排除以参数传入的关键字，grep查询使用
SCRIPT_NAME=$0 
tomcat_pid() {  
	pid=`ps -ef | grep $CATALINA_HOME  | egrep -v "grep|${SCRIPT_NAME}" | awk '{print $2}'`
        echo $pid
}  
start() {  
  pid=$(tomcat_pid)  
  if [ -n "$pid" ];then  
    echo -e "\e[00;31mTomcat is already running (pid: $pid)\e[00m"  
  else  
    echo -e "\e[00;32mStarting tomcat\e[00m"  
    if [ "x`user_exists $TOMCAT_USER`" = "x0" ];then  
      #以root运行执行
      su $TOMCAT_USER -c $CATALINA_HOME/bin/startup.sh  
    else  
      #以普通用户运行的，直接执行
      $CATALINA_HOME/bin/startup.sh  
    fi  
    status  
  fi  
  return 0  
}  
  
status(){  
  pid=$(tomcat_pid)  
  if [ -n "$pid" ];then  
    echo -e "\e[00;32mTomcat is running with pid: $pid\e[00m"  
  else  
    echo -e "\e[00;31mTomcat is not running\e[00m"  
  fi  
}  
  
stop() {  
  pid=$(tomcat_pid)  
  if [ -n "$pid" ];then  
    echo -e "\e[00;31mStoping Tomcat\e[00m"  
        $CATALINA_HOME/bin/shutdown.sh  
  
    let kwait=$SHUTDOWN_WAIT  
    count=0;  
    until [ "x`ps -p $pid | grep -c $pid`" = 'x0' ] || [ $count -gt $kwait ]  
    do  
      echo -n -e "\e[00;31mwaiting for processes to exit\e[00m\n";  
      sleep 1  
      let count=$count+1;  
    done  
  
    if [ $count -gt $kwait ];then  
      echo -n -e "\n\e[00;31mkilling processes which didn't stop after $SHUTDOWN_WAIT seconds\e[00m\n"  
      sudo kill -9 $pid  
    fi  
  else  
    echo -e "\e[00;31mTomcat is not running\e[00m"  
  fi  
  
  return 0  
}  
  
user_exists(){  
   if [ `whoami` = "root" ];then  
    return 0  
   else  
    echo "非root用户！"
    return 1  
   fi
   #if id -u $1 >/dev/null 2>&1; then  
   #   echo "1"  
   #else  
   #   echo "0"  
   #fi  
}  
  
case $2 in  
        start)  
          start  
        ;;  
  
        stop)    
          stop  
        ;;  
  
        restart)  
          stop  
          start  
        ;;  
  
        status)  
      status  
        ;;  
  
        *)  
      echo -e $TOMCAT_USAGE  
        ;;  
esac      
