#!/bin/bash

set -e
cd `realpath $(dirname $0)/..`

[ -f .env ] || cp ./etc/.env-defaults .env
