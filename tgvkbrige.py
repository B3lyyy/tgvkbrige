import logging
import vk_api
import requests
from io import BytesIO
from threading import Thread
from vk_api.longpoll import VkLongPoll, VkEventType
from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext
from config import VK_LOGIN, VK_PASSWORD, VK_CHAT_ID, TELEGRAM_CHAT_ID, BOT_TOKEN, APP_ID

def telegram_message_handler(update: Update, context: CallbackContext, vk):
    message = update.message
    if message:
        try:
            if message.photo:
                largest_photo = max(message.photo, key=lambda x: x.file_size)
                photo_file = largest_photo.get_file()
                photo_response = requests.get(photo_file.file_path)

                if photo_response.status_code == 200:
                    upload_url = vk.photos.getMessagesUploadServer(peer_id=VK_CHAT_ID)['upload_url']
                    photo_stream = BytesIO(photo_response.content)
                    files = {'photo': ('photo.jpg', photo_stream, 'image/jpeg')}
                    photo_upload_response = requests.post(upload_url, files=files).json()

                    if 'photo' not in photo_upload_response:
                        raise Exception("Ошибка загрузки фотографии")

                    save_photo_response = vk.photos.saveMessagesPhoto(server=photo_upload_response['server'],
                                                                      photo=photo_upload_response['photo'],
                                                                      hash=photo_upload_response['hash'])[0]
                    if message.caption:
                        vk.messages.send(chat_id=VK_CHAT_ID,
                                         random_id=0,
                                         user_ids=None,
                                         message=message.caption,
                                         attachment=f'photo{save_photo_response["owner_id"]}_{save_photo_response["id"]}')
                    else:
                        vk.messages.send(chat_id=VK_CHAT_ID,
                                         random_id=0,
                                         user_ids=None,
                                         message='',
                                         attachment=f'photo{save_photo_response["owner_id"]}_{save_photo_response["id"]}')
                else:
                    logging.warning("Неудалось загрузить фотографию")
            else:
                if message.text:
                    vk.messages.send(chat_id=VK_CHAT_ID, message=message.text, random_id=0)
                else:
                    logging.warning("Неподдерживаемый формат сообщения.")
        except Exception as e:
            logging.exception(f"Ошибка при отправке сообщения в ВК: {e}")
    else:
        logging.warning("Получено пустое или неподдерживаемое сообщение.")


def telegram_to_vk(updater, vk):
    message_handler = MessageHandler((Filters.text | Filters.photo) & ~Filters.command, lambda update, context: telegram_message_handler(update, context, vk))
    updater.dispatcher.add_handler(message_handler)

def vk_streaming(vk_session, updater):
    longpoll = VkLongPoll(vk_session)
    vk = vk_session.get_api()
    current_user_id = vk.users.get()[0]['id']

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and \
           event.from_chat and \
           event.chat_id == VK_CHAT_ID and \
           event.user_id != current_user_id:

            # Получение информации о сообщении
            message_info = vk.messages.getById(message_ids=event.message_id)['items'][0]

            # Получение имени отправителя
            user = vk.users.get(user_ids=event.user_id)[0]
            full_name = f"{user['first_name']} {user['last_name']}"

            # Добавление подписи и отправка сообщения
            text_message = f"{full_name}:\n\n{message_info['text']}"

            # Проверка наличия изображения в сообщении
            if ('attachments' in message_info and len(message_info['attachments']) > 0 and
                 message_info['attachments'][0]['type'] == 'photo'):
                largest_photo = max(message_info['attachments'][0]['photo']['sizes'], key=lambda x: x['height'])
                photo_url = largest_photo['url']
                updater.bot.send_photo(chat_id=TELEGRAM_CHAT_ID, photo=photo_url, caption=text_message)
            else:
                # Отправка обычного текстового сообщения
                updater.bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=text_message)

def captcha_handler(captcha):
    key = input("Введите капчу {}: ".format(captcha.get_url())).strip()
    return captcha.try_again(key)

def two_factor():
    code = input("Введите код 2ФА: ").strip()
    return code, False

def auth_handler():
    key = input("Введите код из приложения: ")
    remember_device = True
    return key, remember_device

def main():
    if not all([VK_LOGIN, VK_PASSWORD, BOT_TOKEN]):
        logging.error("Отсутствуют указанные данные: VK_LOGIN, VK_PASSWORD, или BOT_TOKEN")
        return

    print(
        r"""
             .--,-``-.                                            
    ,---,.  /   /     '.    ,--,                                  
  ,'  .'  \/ ../        ; ,--.'|                                  
,---.' .' |\ ``\  .`-    '|  | :                                  
|   |  |: | \___\/   \   ::  : '                                  
:   :  :  /      \   :   ||  ' |        .--,      .--,      .--,  
:   |    ;       /  /   / '  | |      /_ ./|    /_ ./|    /_ ./|  
|   :     \      \  \   \ |  | :   , ' , ' : , ' , ' : , ' , ' :  
|   |   . |  ___ /   :   |'  : |__/___/ \: |/___/ \: |/___/ \: |  
'   :  '; | /   /\   /   :|  | '.'|.  \  ' | .  \  ' | .  \  ' |  
|   |  | ; / ,,/  ',-    .;  :    ; \  ;   :  \  ;   :  \  ;   :  
|   :   /  \ ''\        ; |  ,   /   \  \  ;   \  \  ;   \  \  ;  
|   | ,'    \   \     .'   ---`-'     :  \  \   :  \  \   :  \  \ 
`----'       `--`-,,-'                 \  ' ;    \  ' ;    \  ' ; 
                                        `--`      `--`      `--`  
        """
    )
         
    vk_session = vk_api.VkApi(login=VK_LOGIN, password=VK_PASSWORD, auth_handler=two_factor, app_id=APP_ID, scope='wall,offline', captcha_handler=captcha_handler, api_version='5.131')

    try:
        vk_session.auth()
    except vk_api.AuthError as e:
        logging.error(f"Не удалось пройти аутентификацию с ВКонтакте: {e}")
        return

    vk = vk_session.get_api()
    updater = Updater(token=BOT_TOKEN, use_context=True)

    vk_thread = Thread(target=vk_streaming, args=(vk_session, updater))
    vk_thread.start()

    telegram_to_vk(updater, vk)
    updater.start_polling()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    main()
