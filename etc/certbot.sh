#!/bin/bash

cd `realpath $(dirname $0)/..`

CERTBOT_CMD_DOCKER="docker run --rm --tty \
    -v $(pwd)/volumes/letsencrypt/data:/etc/letsencrypt \
    -v $(pwd)/volumes/letsencrypt/www:/var/www \
    -v $(pwd)/volumes/letsencrypt/logs:/var/log/letsencrypt \
    certbot"
CERTBOT_OPTS="--webroot --webroot-path /var/www/ --agree-tos --email rinat.izmailov@gmail.com"

if [[ $1 == "renew" ]] ; then
    certbot_command="${CERTBOT_CMD_DOCKER} renew ${CERTBOT_OPTS}"
else
    DOMAINS=`echo " $@" | sed "s/ / -d /g"`
    certbot_command="${CERTBOT_CMD_DOCKER} certbot certonly ${DOMAINS} --force-renewal ${CERTBOT_OPTS}"
fi

$certbot_command
