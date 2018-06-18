#!/bin/bash
set -e

CYAN='\033[0;36m'
NC='\033[0m'

action=$1
cd `realpath "$(dirname $0)"`

for file in ./pre-init.d/*.sh; do
    echo "$file ..."
    [ -f "$file" ] && [ -x "$file" ] && "$file"
done

case $action in
    "0")
        echo "only-init, exit 0"
        ;;

    "nginx-start")
        docker-compose -f docker-compose-nginx-dev.yml up -d
        ;;
    "db-start")
        cd ..
        docker-compose -f docker-compose.db.yml up -d
        ;;
    "db-start-tiny")
        cd ..
        docker-compose -f docker-compose.db.yml up -d postgres rabbit
        ;;
    "web-start")
        cd ..
        docker-compose up web celery
        ;;
    "start")
        ./dev-up.sh react-start
        ./dev-up.sh nginx-start
        ./dev-up.sh db-start-tiny
        ./dev-up.sh web-start
        ;;

    "react-build")
        docker-compose -f docker-compose-react.yml run react-build
        ;;
    "react-deploy")
        rsync -vazP --delete ../volumes/frontend/ cerber@voxball:/home/cerber/voxball/volumes/frontend/
        ;;

    "react-start")
        docker-compose -f docker-compose-react.yml up -d react-dev
        ;;
    "react-build-test")
        docker-compose -f docker-compose-react.yml run react-build-test
        ;;
    "react-deploy-test")
        rsync -vazP --delete ../volumes/frontend/ cerber@voxball:/home/cerber/test-voxball/volumes/frontend/
        ;;

    * | "-h" | "--help")
        echo -e "
./dev-up.sh

${CYAN}./dev-up.sh 0${NC} - только pre-init.d/*.sh

${CYAN}./dev-up.sh nginx-start${NC}

${CYAN}./dev-up.sh db-start${NC}
${CYAN}./dev-up.sh db-start-tiny${NC} - запустить только postgres & rabbitmq

${CYAN}./dev-up.sh web-start${NC}
${CYAN}./dev-up.sh start${NC} - запустить dev окружение

${CYAN}./dev-up.sh react-start${NC} - react.js live режим

${CYAN}./dev-up.sh react-build${NC} - react.js собрать статику для prod
${CYAN}./dev-up.sh react-deploy${NC} - react.js собрать статику для prod

${CYAN}./dev-up.sh react-build-test${NC} - react.js собрать статику для dev
${CYAN}./dev-up.sh react-deploy-test${NC} - react.js deploy статики для dev"
        ;;
esac
