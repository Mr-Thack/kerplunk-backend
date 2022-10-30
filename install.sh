#!/bin/sh
rm -rf /var/www/api/code
mkdir /var/www/api/code
cp ./api/* /var/www/api/code

rm -rf /etc/lighttpd
mkdir /etc/lighttpd
cp ./lighttpd-config/* /etc/lighttpd


