# Тестовое задание на позицию Junior в компанию ООО Фабрика Решений 📄
Ссылка на вакансию - [link](https://tomsk.hh.ru/vacancy/80082407?hhtmFrom=chat)

# Getting Started ✅
Для разработки использовалась ОС Manjaro. Приведенный ниже cheat sheet сделан для Manjaro. Шаги легко повторяются на любом Linux дистрибутиве.
Если Вы работаете на Window там будет слегка по-другому, но смысл тот же и можно так же повторить шаги работая по аналогии.

### Installing 🔨
Для работы использовал python/pip следующей версии:
* python3.10;
* pip3.10.

Прежде чем начинать работу необходимо убедится:
  * установлен python/pip;
  * установлен Docker/docker-compose;
  * установлен PostgreSQL (если Вы хотите использовать локальную БД, а не в контейнере);
  * установлен kubectl/minikube для работы с k8s.

Здесь не будет инструкции по установки софта в списке выше, поскольку это очень простые действия:
```
sudo pacman -S <something>
```
Далее небольшие правки и все. Легко можно найти в интернете. Если все жё будет проблемы, пишите помогу :)

Следующий шаг будет клонирование репозитория с проектом и установка зависимостей проекта. Делается это следующим образом:

Клонирование репозитория:
```
git clone https://gitlab.com/acolyte-py/test-case-solution_factory.git
```
Устновка зависимостей проекта:
```
pip3.10 install -r requirements.txt
```
Сам проект запускается командой:
```
uvicorn main:app --reload
```

### Run Docker 🔴
В проекте есть готовый файлы для работы с Docker/docker-compose
Есть готовый образ - [image](https://hub.docker.com/repository/docker/acolytelovedev/fabric-api-k8s/general)

Для запуска проекта достаточно запустить команду:
```
docker-compose up
```

### Run Kubernetes 🔴
Запуск проекта на K8s выполняется двумя командами, все файлы так же есть в проекте:
```
kubectl apply -f deployment.yaml
```
```
kubectl apply -f service.yaml
```

### Completed tasks 🐾
* [100%] организовать тестирование написанного кода;
* [100%] обеспечить автоматическую сборку/тестирование с помощью GitLab CI;
* [100%] подготовить docker-compose для запуска всех сервисов проекта одной командой;
* [50%] 
написать конфигурационные файлы (deployment, ingress, …) для запуска проекта в kubernetes и описать как их применить к работающему кластеру;
* [100%] сделать так, чтобы по адресу /docs/ открывалась страница со Swagger UI и в нём отображалось описание разработанного API. Пример: https://petstore.swagger.io;
* [100%] реализовать администраторский Web UI для управления рассылками и получения статистики по отправленным сообщениям;
* [100%] реализовать отдачу метрик в формате prometheus и задокументировать эндпоинты и экспортируемые метрики.


## Built With 🔧
* [FastAPI](https://fastapi.tiangolo.com/) - Для разработки приложения;
* [PostgreSQL](https://www.postgresql.org/docs/) - Для работы с Docker;
* [docker-compose](https://docs.docker.com/compose/) - Для запуска контейнеров;
* [SQLAlchemy](https://docs.sqlalchemy.org/en/20/) - Для работы с базы данными в python;
* [K8s](https://kubernetes.io/docs/home/) - Для работы с K8s.

## Authors 🗿

* **Миронов Миша** - *Изначальная работа* - [vk](https://vk.com/acolyte_py) | tg - @acolytee.

## License ©

Данный проект использует лицензию MIT - [LICENSE](LICENSE) для деталей.
