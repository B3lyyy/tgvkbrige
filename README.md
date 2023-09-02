# tgvkbrige
Это бот – созданный на платформах Telegram и VKontakte, который может пересылать сообщения и фотографии между этими двумя популярными мессенджерами. Бот может быть полезен, если вы используете оба мессенджера и хотите иметь возможность отправлять сообщения из одного чата в другой или просто сохранять копии сообщений в обоих чатах.

Бот использует два API – Telegram Bot API и VK API, чтобы получать и отправлять сообщения и фотографии. Он работает в качестве посредника между двумя чатами, принимая сообщения и фотографии от одного мессенджера и пересылая их в другой. Бот написан на Python с использованием библиотеки python-telegram-bot и vk_api.

Важно отметить, что бот не сохраняет и не обрабатывает никакие данные пользователей. Он просто передает сообщения и фотографии между мессенджерами в режиме реального времени.

Бот будет дорабатываться и улучшаться со временем. На данный момент работают базовые необходимые функции. В планах поддержка видео, документов и стикеров.

Чтобы этот бот заработал, нужно выполнить следующие шаги:
1. Установите Python 3 на свой компьютер, если он еще не установлен.
2. Установите необходимые библиотеки. Для запуска бота вам понадобятся библиотеки python-telegram-bot и vk_api. Откройте командную строку на вашем компьютере и введите следующую команду:

pip install python-telegram-bot vk_api

3. Создайте бота в Telegram, следуя инструкциям @BotFather. Напишите команду /newbot и следуйте инструкциям для создания нового бота Telegram. В конце этого процесса BotFather выдаст вам токен вашего бота. Сохраните этот токен в безопасном месте, так как он будет нужен для подключения к API Telegram.
4. Добавьте его в группу тг. После этого переходим по ссылке:

https://api.telegram.org/botХХХХХХХХХХХХХХХХХХХ/getUpdates?...

Где вместо ХХХХХХ вставляем токен бота. Напишите что-нибудь в чате с ботом. Обновите страницу по ссылке. Должна появится новая строка на странице. В ней ищем: 

"chat":{"id":-ХХХХХХХХХХХХХХ

-ХХХХХХХХХХХХХ и есть нужный ид. Сохраняем себе ид чата.

5. Создайте страничку ВК для бота, ну или используйте уже имеющуюся. В настройках можете подключить двухфакторную авторизацию по телефону. Вам понадобится сохранить логин и пароль. В моем случае в качестве логина выступает номер телефона и выглядит так: 79990000000.
   
6. Узнайте ид чата вконтакте. Покажу на примере группового чата, куда я добавил бота. Открывает чат, смотрим в адресную строку: 

https://vk.com/im?sel=c123

В данном случае 123 является ид чата. Запоминаем.

7. Вставьте нужную информацию в config. В этом файле есть пункт: "APP_ID", если не знаете как получают access_token ВК, оставьте как есть, это ид Кейт мобайл. Если знаете-умеете, меняйте ид на свое приложение.

8. Запустите бота. Чтобы запустить бота кликните по исходнику, чтобы запустить питон. Или откройте командную строку в папке с исходным кодом бота и введите следующую команду:

python tgvkbrige.py


9. После запуска бот начнет процедуру авторизации на сайте ВК. Если вы включили двухфакторную авторизацию, бот попросит ввести код. Если нет, бот пропустит этот шаг.

Поздравляю с успешной активацией!
