if [ ! -f "/usr/lib/tethys/setup_complete" ] ;
then
    
    echo Starting TethysCore Setup
    apt-get update && apt-get install -y gcc
    bash setup_tethys.sh \
         --allowed-host ${TETHYSBUILD_ALLOWED_HOST:-127.0.0.1} \
         --python-version ${TETHYSBUILD_PY_VERSION:-2} \
         --db-username ${TETHYSBUILD_DB_USERNAME:-tethys_default} \
         --db-password ${TETHYSBUILD_DB_PASSWORD:-pass} \
         --db-host ${TETHYSBUILD_DB_HOST:-127.0.0.1} \
         --db-port ${TETHYSBUILD_DB_PORT:-5432} \
         --superuser ${TETHYSBUILD_SUPERUSER:-tethys_super} \
         --superuser-pass ${TETHYSBUILD_SUPERUSER_PASS:-admin} \
         --tethys-home ${TETHYSBUILD_TETHYS_HOME:-/usr/lib/tethys} \
    echo TethysCore Setup Complete
    cd /var/www/tethys/apps
    echo Setting Up CityWater
    
    echo "----------------------------------------------------------------------------------"
    echo "Setting Up NGINX"
    echo "----------------------------------------------------------------------------------"
    NGINX_USER=$(grep 'user .*;' /etc/nginx/nginx.conf | awk '{print $2}' | awk -F';' '{print $1}')
    NGINX_GROUP=${NGINX_USER}
    NGINX_HOME=$(grep ${NGINX_USER} /etc/passwd | awk -F':' '{print $6}')
    
    chown -R ${NGINX_USER}:${NGINX_GROUP} ${TETHYS_HOME}/src
    chown -R ${NGINX_USER}:${NGINX_GROUP} ${TETHYS_HOME}/static
    
    /bin/bash -c 'mkdir -p /run/uwsgi; chown www-data:www-data /run/uwsgi'
    
    touch /usr/lib/tethys/setup_complete

fi


echo "----------------------------------------------------------------------------------"
echo Starting Server
echo "----------------------------------------------------------------------------------"
nohup /usr/lib/tethys/miniconda/envs/tethys/bin/uwsgi --yaml /usr/lib/tethys/src/tethys_portal/tethys_uwsgi.yml --uid www-data --gid www-data&
nginx -g 'daemon off;'

. deactivate
