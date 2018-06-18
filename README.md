# Установка

```
git clone git@git.webid.kz:voxball/voxball.git
git clone git@git.webid.kz:voxball/voxball-frontend.git
mkdir -p voxball/volumes
cd voxball/volumes

mkdir -p web/{logs,media}

wget http://voxball.com/media/samJDnr45/db.tar.bz2
wget http://voxball.com/media/samJDnr45/letsencrypt.tar.bz2
tar xvf db.tar.bz2
tar xvf letsencrypt.tar.bz2
```

# Запуск dev

```
echo "127.0.0.1      test.devz.voxball.io" >> /etc/hosts
./dev/dev-up.sh start
```

Открыть в браузере https://test.devz.voxball.io/

# Доступные команды

**./up.sh**
```
./up.sh 0 - только pre-init.d/*.sh
./up.sh nginx-start - старт nginx
./up.sh nginx-reload - рестарт nginx

./up.sh db-start - запуск базы данных

./up.sh app-start - запуск uwsgi приложения на prod
./up.sh app-reload - рестарт uwsgi приложения на prod

./up.sh test-start - запуск тестовго окружения
./up.sh test-stop - остановка тестовго окружения

./up.sh test-deploy - деплой на приложения на тестовый

./up.sh react-build-test - react.js собрать статику для тест
./up.sh react-deploy-test - react.js собрать и задеплоить на тест
```

**./dev/dev-up.sh**
```
./dev-up.sh 0 - только pre-init.d/*.sh

./dev-up.sh nginx-start

./dev-up.sh nginx-start

./dev-up.sh nginx-start

./dev-up.sh db-start
./dev-up.sh db-start-tiny - запустить только postgres & rabbitmq

./dev-up.sh web-start
./dev-up.sh start - запустить dev окружение

./dev-up.sh react-start - react.js live режим

./dev-up.sh react-build - react.js собрать статику для prod
./dev-up.sh react-deploy - react.js собрать статику для prod
```
