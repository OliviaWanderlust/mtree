#!/bin/bash
#
# chkconfig: - 85 12
# description: Open source system
# processname: workflow
# Date: 2017-03-15
# Version: 0.1
# Site: 
# Author: hhr


base_dir=$(cd $(dirname $0);pwd)
export PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin

if [ -f /etc/init.d/functions ];then
    . /etc/init.d/functions
else
    echo "No functions script found in [./functions, ./install/functions, /etc/init.d/functions]"
    exit 1
fi

PROC_NAME=${base_dir##*/}
lockfile=/var/lock/subsys/${PROC_NAME}

start() {
        yun_start=$"Starting ${PROC_NAME} service:"
        if [ -f $lockfile ];then
             echo -n "${PROC_NAME} is running..."
             success "$yun_start"
             echo
        else
            source $base_dir/env/bin/activate
            daemon python $base_dir/manage.py runserver 0.0.0.0:8000 &> $base_dir/logs/console.log 2>&1 &
            #>$base_dir/logs/celery.log
            daemon python $base_dir/manage.py celery worker --loglevel=info &>> $base_dir/logs/celery.log 2>&1 &
            sleep 1
            echo -n "$yun_start"
            ps axu | grep ${PROC_NAME} | grep -v 'grep' &> /dev/null
            if [ $? == '0' ];then
                success "$yun_start"
                if [ ! -e $lockfile ]; then
                    lockfile_dir=`dirname $lockfile`
                    mkdir -pv $lockfile_dir
                fi
                touch "$lockfile"
                echo
            else
                failure "$yun_start"
                echo
            fi
        fi
}


stop() {
    echo -n $"Stopping ${PROC_NAME} service:"
    daemon python $base_dir/manage.py crontab remove &>> $base_dir/logs/console.log 2>&1
    ps aux | grep -E ${PROC_NAME} | grep -v grep | awk '{print $2}' | xargs kill -9 &> /dev/null
    ret=$?
    if [ $ret -eq 0 ]; then
        echo_success
        echo
        rm -f "$lockfile"
    else
        echo_failure
        echo
        rm -f "$lockfile"
    fi

}

status(){
    ps axu | grep -E ${PROC_NAME} | grep -v 'grep' &> /dev/null
    if [ $? == '0' ];then
        echo -n "${PROC_NAME} is running..."
        success
        touch "$lockfile"
        echo
    else
        echo -n "${PROC_NAME} is not running."
        failure
        echo
    fi
}



restart(){
    stop
    start
}

# See how we were called.
case "$1" in
  start)
        start
        ;;
  stop)
        stop
        ;;

  restart)
        restart
        ;;

  status)
        status
        ;;
  *)
        echo $"Usage: $0 {start|stop|restart|status}"
        exit 2
esac
