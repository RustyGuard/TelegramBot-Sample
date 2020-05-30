from telegram import ReplyKeyboardRemove
from telegram.ext import CommandHandler
from telegram.ext import Updater, MessageHandler, Filters, ConversationHandler

from secrets import TOKEN


def main():

    def stop(update, context):
        update.message.reply_text(
            "Ok",
            reply_markup=ReplyKeyboardRemove()
        )

    def enter(update, context):
        update.message.reply_text(
            'Добро пожаловать! Пожалуйста, сдайте верхнюю одежду в гардероб!'
        )

        context.user_data['room'] = 1
        room = rooms_desc[1]

        update.message.reply_text(
            f'В данном зале представлено {room[0]}'
        )
        for i in room[1]:
            next_room = rooms_desc[i]
            update.message.reply_text(
                f'Далее вы можете пройти в комнату {next_room[0]} ({i})'
            )

        return 1

    def command_room(update, context):
        chosen = int(update.message.text)
        if chosen in rooms_desc[context.user_data['room']][1]:
            context.user_data['room'] = int(update.message.text)
        else:
            update.message.reply_text(
                'Нельзя сквозь стены ходить, чувак'
            )
            return 1
        if context.user_data['room'] == 0:
            update.message.reply_text(
                'Всего доброго, не забудьте забрать верхнюю одежду в гардеробе!'
            )

            return ConversationHandler.END

        room = rooms_desc[context.user_data['room']]
        print(context.user_data['room'])
        update.message.reply_text(
            f'В находитесь в зале {room[0]}'
        )
        for i in room[1]:
            next_room = rooms_desc[i]
            update.message.reply_text(
                f'Далее вы можете пройти в комнату {next_room[0]} ({i})'
            )

    rooms_desc = {
        0: ('С ВЫХОДОМ', ()),
        1: ('ЗЕВСА', (0, 2)),
        2: ('ВЕНЕРЫ', (3, )),
        3: ('ГЕРМЕСА', (1, 4)),
        4: ('уборщика', (1, )),
    }

    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('enter', enter)],

        states={
            1: [MessageHandler(Filters.text, command_room, pass_user_data=True)],
        },
        fallbacks=[CommandHandler('stop', stop)]
    )
    dp.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
