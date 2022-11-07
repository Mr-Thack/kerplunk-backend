#!/bin/sh
rm -rf /var/www/api/*
cp ./api/* /var/www/api/

rm -rf /etc/lighttpd
mkdir /etc/lighttpd
cp ./lighttpd-config/* /etc/lighttpd


