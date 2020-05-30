from telegram.ext import Updater
from telegram.ext import CommandHandler

from api_tools import StaticAPIImage, WorldPoint, Marker
from secrets import TOKEN


def main():
    def command_show(update, context):
        print('Showing...')
        image = StaticAPIImage()
        print(image)
        place = ' '.join(context.args)
        p = WorldPoint()
        p.set_toponym(place)
        image.marks.append(Marker(p))
        update.message.reply_photo(photo=image.to_http(0.05, 'map', p),
                                   caption='Пред вами ' + place)

    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("show", command_show,
                                  pass_args=True,
                                  pass_job_queue=True,
                                  pass_chat_data=True,
                                  pass_user_data=True))
    updater.start_polling()
    print('Started!')
    updater.idle()


if __name__ == '__main__':
    main()
