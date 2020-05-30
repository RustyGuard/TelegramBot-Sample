import requests
from telegram import ReplyKeyboardRemove
from telegram.ext import CommandHandler
from telegram.ext import Updater

from secrets import TOKEN, YANDEX_API_KEY


def main():

    def set_lang(update, context):
        context.user_data['lang'] = context.args[0]

    def command_translate(update, context):
        print('Translate')
        params = {
            'key': YANDEX_API_KEY,
            'text': ' '.join(context.args),
        }
        print(params)
        if 'lang' in context.user_data:
            params['lang'] = context.user_data['lang']
        else:
            params['lang'] = 'ru'
        print(params)
        json_response = requests.get('https://translate.yandex.net/api/v1.5/tr.json/translate', params=params).json()
        print(json_response.get('text'))
        update.message.reply_text(json_response.get('text', [f'Something goes wrong {json_response}']).pop())

    updater = Updater(TOKEN, use_context=True)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("translate", command_translate,
                                  pass_args=True,
                                  pass_job_queue=True,
                                  pass_chat_data=True,
                                  pass_user_data=True))
    dp.add_handler(CommandHandler("set_lang", set_lang,
                                  pass_args=True,
                                  pass_job_queue=True,
                                  pass_chat_data=True,
                                  pass_user_data=True))

    print('Started!')
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
