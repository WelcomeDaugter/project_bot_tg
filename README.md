# Телеграм бот "Crypto Price"
Проект нацелен помочь в аналитике и наблюдении за изменением курса криптовалют

Ссылка на бота в телеграмм ```@verysoonbot```

Выбор темы обусловлен личной заинтересованностью автора данной сферой деятельности
# Основной функционал:
Перед началом исполользования бота пользователю необходимо пройти регистрацию, указав свой usernaem и 8-ми значный пароль, включающий 1 цифру. После регистрации разблокирутся весь остальной функционал, а именно: 

+ Вызов необходимой пары криптовалюты при помощи api-ninjas и просмотр актуальной цены (более сотни различной валюты доступны для поиска)

+ Формирования графика по необходимой валюте (matplotlib) за период времени, при помощи запроса api-CoinGecko

+ Бонус - игральный кубик, доступный по команде /dice

# Команды в Telegram

| Команда          |          Описание         |
|------------------|---------------------------|
| `/start`         | Запуск бота               |
| `/reg`           | Регистрация пользователя  |
| `/menu`          | Вызом меню                |
| `/menu`          | Вызов меню команд         |
| `/help`          | Доступный функционал      |
| `/price`         | Запрос нужной пары валют  |                  
|`Цены криптовалют`| Формирование графика      |
| `/dice`          | Бросок игральной кости    |
Пасхалка, скорее являющая символом любой криптовалюты

Для удобства использования, помимо команд, пользователя сопровождают интуитивно-понятные кнопки и копирумый текст

Бот использует базу данных, с хешированием пароля, а также наделён всяческими проверками (на регистрацию, на наличие пользователя в бд, на локализацию функций)

# Использование удалённого сервера (Linux)

Примечание: в репозитории отсутствует файл .env с токеном бота, вам его придется создавать самостоятельно. Используются API: ```Telegram Bot API; API-Ninjas - запрос пары валют; CoinGecko API - вызов истории криптовалюты```

1. Установка ПО

```sudo apt-get install python3.12```

```sudo apt-get install python3-pip```

```python3 --version - проверка установленной версии ```

1. Клонирование репозитория 

```git clone https://github.com/WelcomeDaugter/project_bot_tg [Название папки куда клонируете]```

2. Переход в вашу директорию, если вы не в ней

```cd "/root/Название/папки/"```

3. Создание виртуального окружения

```python3 -m venv venv```

4. Активация виртуального окружения

```source venv/bin/activate```

5. Установка зависимостей

```pip3 install -r requirements.txt```

6. Запуск скрипта

```python main.py```

# Связь со мной

Telegram - ```@web3kazakh```
Email - ```yarosav2004b@yandex.ru```
