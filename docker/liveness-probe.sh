#!/bin/sh

check_process_is_running() { 
	if [ "$(ps $1 | wc -l)" -ne 2 ]; then 
		echo The $2 process \($1\) is  not running. 1>&2; 
	else
		echo "ok"
	fi 
}

ret1=$(check_process_is_running $(cat $(grep 'pidfile=.*' /etc/supervisor/supervisord.conf | awk -F'=' '{print $2}' | awk '{print $1}')) supervisor)
ret2=$(check_process_is_running $(cat $(grep 'pid .*;' /etc/nginx/nginx.conf | awk '{print $2}' | awk -F';' '{print $1}')) nginx)
ret3=$(check_process_is_running $(ls -l /run/tethys_asgi0.sock.lock | awk -F'-> ' '{print $2}') asgi)

if [ "$ret1" != "ok" ] || [ "$ret2" != "ok" ] || [ "$ret3" != "ok" ]; then
	echo "liveness-probe.sh: at least 1 test failed"
	exit 1
else
	echo "liveness-probe.sh: all tests passed"
	exit 0
fi
