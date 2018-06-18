#!/bin/bash
set -e
#source .env

CYAN='\033[0;36m'
NC='\033[0m'

action=$1
cd `realpath "$(dirname $0)"`

case $action in
    "0")
        echo "only-init, exit 0"
        ;;

    "deploy")
        rsync -vazP ./docker-compose* up.sh ./pre-init.d ./etc cerber@voxball:voxball/
        rsync -vazP ./etc/ cerber@voxball:voxball/etc/
        rsync -vazP --exclude "*.pyc" --delete --force --delete-excluded ./src/ cerber@voxball:voxball/src/
        ;;
    "test-deploy")
        rsync -vazP ./docker-compose* up.sh ./pre-init.d cerber@test.devz.voxball.io:test-voxball/
        rsync -vazP ./etc/ cerber@test.devz.voxball.io:test-voxball/etc/
        rsync -vazP --exclude "settings.py" --exclude "*.pyc" --delete --force ./src/ cerber@test.devz.voxball.io:test-voxball/src/
        ;;

    "test-start")
        docker-compose -f docker-compose.test.yml up
        ;;
    "test-stop")
        docker-compose -f docker-compose.test.yml up
        ;;

    "app-start")
        docker-compose up -d
        ;;
    "app-reload")
        docker-compose exec web touch /tmp/uwsgi-reload
        ;;

    "db-start")
        docker-compose -f docker-compose.db.yml up -d
        ;;
    "nginx-start")
        docker-compose -f docker-compose.nginx-${WORKNET}.yml up -d
        ;;
    "nginx-reload")
        docker-compose -f docker-compose.nginx-${WORKNET}.yml exec proxy nginx -t
        docker-compose -f docker-compose.nginx-${WORKNET}.yml kill -s HUP proxy
        ;;

    "react-build")
        docker-compose -f docker-compose-react.yml run react-install
        docker-compose -f docker-compose-react.yml run react-build
        ;;
    "react-deploy")
        docker-compose -f docker-compose-react.yml run react-install
        docker-compose -f docker-compose-react.yml run react-build
        rsync -vazP --delete ./volumes/frontend/ cerber@voxball:/home/cerber/voxball/volumes/frontend/
        ;;
    "react-build-test")
        docker-compose -f docker-compose-react.yml run react-install
        docker-compose -f docker-compose-react.yml run react-build-test
        ;;
    "react-deploy-test")
        docker-compose -f docker-compose-react.yml run react-install
        docker-compose -f docker-compose-react.yml run react-build-test
        rsync -vazP --delete ./volumes/frontend/ cerber@test.devz.voxball.io:/home/cerber/test-voxball/volumes/frontend/
        ;;
        
    * | "-h" | "--help")
        echo -e "
${CYAN}./up.sh${NC}
${CYAN}./up.sh 0${NC} - только pre-init.d/*.sh
${CYAN}./up.sh nginx-start${NC} - старт nginx
${CYAN}./up.sh nginx-reload${NC} - рестарт nginx

${CYAN}./up.sh db-start${NC} - запуск базы данных

${CYAN}./up.sh app-start${NC} - запуск uwsgi приложения на prod
${CYAN}./up.sh app-reload${NC} - рестарт uwsgi приложения на prod

${CYAN}./up.sh react-build${NC} - react.js собрать статику для prod
${CYAN}./up.sh react-deploy${NC} - react.js собрать статику и залить на prod

${CYAN}./up.sh test-start${NC} - запуск тестовго окружения
${CYAN}./up.sh test-stop${NC} - остановка тестовго окружения

${CYAN}./up.sh test-deploy${NC} - деплой на приложения на тестовый

${CYAN}./up.sh react-build-test${NC} - react.js собрать статику для dev
${CYAN}./up.sh react-deploy-test${NC} - react.js собрать и задеплоить на тест
"
esac
