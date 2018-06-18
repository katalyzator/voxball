#!/bin/bash

set -e
cd `realpath $(dirname $0)/..`

for DNAME in ./volumes/letsencrypt/{data,www/.well-known,logs} ./volumes/{frontend,web/{media,logs}} ; do
    mkdir -p "$DNAME"
    USER_ID=$(stat -c '%u' "$DNAME")
    GROUP_ID=$(stat -c '%g' "$DNAME")
    if [[ $USER_ID != 1000 || $GROUP_ID != 1000 ]] ; then
        echo -e "${RED}${DNAME}: Error dir's owner - not \"1000:1000\"${NC}"
        exit 1
    fi
done

mkdir -p ./volumes/{postgres,elasticsearch}
