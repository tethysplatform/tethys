#!/bin/sh


check_process_is_running() { 
	if [ "$(ps $1 | wc -l)" -ne 2 ]; then 
		echo The $2 process \($1\) is  not running. 1>&2
	else
		echo "ok"
	fi 
}


get_pid_from_file() { 
	if [ -f $1 ]; then
		echo $(cat $1)
	else 
		echo pid file for $2 does not exist at $1
		exit 1
	fi
}


check_pid_is_number() { 
	case $1 in
		''|*[!0-9]*) echo pid found for $2 is not a number: $1 ; exit 1;;
		*) ;;
	esac
}


# supervisord
SUPERVISORD_PID_FILE=$(grep 'pidfile=.*' /etc/supervisor/supervisord.conf | awk -F'=' '{print $2}' | awk '{print $1}')
SUPERVISORD_PID=$(get_pid_from_file "${SUPERVISORD_PID_FILE}" supervisor)
check_pid_is_number "${SUPERVISORD_PID}" supervisor
SUPERVISORD_STATUS=$(check_process_is_running "${SUPERVISORD_PID}" supervisor)


# nginx
NGINX_PID_FILE=$(grep 'pid .*;' /etc/nginx/nginx.conf | awk '{print $2}' | awk -F';' '{print $1}')
NGINX_PID=$(get_pid_from_file "${NGINX_PID_FILE}" nginx)
check_pid_is_number "${NGINX_PID}" nginx
NGINX_STATUS=$(check_process_is_running "${NGINX_PID}" nginx)


# tethys asgi server
if [ ! -L /run/tethys_asgi0.sock.lock ]; then
	echo lock file for asgi does not exist at /run/tethys_asgi0.sock.lock
	exit 1
fi
ASGI_PID=$(ls -l /run/tethys_asgi0.sock.lock | awk -F'-> ' '{print $2}' 2>&1)
check_pid_is_number "${ASGI_PID}" asgi
ASGI_STATUS=$(check_process_is_running "${ASGI_PID}" asgi)


# print errors
if [ "$SUPERVISORD_STATUS" != "ok" ] ; then
	echo $SUPERVISORD_STATUS 1>&2
fi

if [ "$NGINX_STATUS" != "ok" ] ; then
	echo $NGINX_STATUS 1>&2
fi

if [ "$ASGI_STATUS" != "ok" ] ; then
	echo $ASGI_STATUS 1>&2
fi

if [ "$SUPERVISORD_STATUS" != "ok" ] || \
	[ "$NGINX_STATUS" != "ok" ] || \
	[ "$ASGI_STATUS" != "ok" ]; then
	exit 1
else
	echo "liveness-probe.sh: all tests passed"
	exit 0
fi
