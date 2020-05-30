import json
import random

from telegram import ReplyKeyboardRemove
from telegram.ext import Updater, MessageHandler, Filters, ConversationHandler
from telegram.ext import CommandHandler

from secrets import TOKEN


def main():
    def stop(update, context):
        update.message.reply_text(
            "Ok",
            reply_markup=ReplyKeyboardRemove()
        )

    def enter(update, context):
        with open('test.json', encoding='utf8') as test_file:
            context.user_data['all'] = json.loads(test_file.read())['test']
            random.shuffle(context.user_data['all'])

        context.user_data['correct_ans'] = 0
        context.user_data['all_ans'] = len(context.user_data['all'])
        take_next_question(update, context)
        return 1

    def take_next_question(update, context):
        test = context.user_data['all'].pop()
        context.user_data['correct'] = test['response']
        update.message.reply_text(test['question'])

    def command_room(update, context):
        if update.message.text == '/stop':
            return ConversationHandler.END
        if update.message.text == context.user_data['correct']:
            context.user_data['correct_ans'] += 1
        if context.user_data['all']:
            take_next_question(update, context)
        else:
            update.message.reply_text('Тест окончен')
            update.message.reply_text(f'Вы набрали {context.user_data["correct_ans"]} / '
                                      f'{context.user_data["all_ans"]} баллов')
            return ConversationHandler.END

    updater = Updater(TOKEN, use_context=True)
    # Получаем из него диспетчер сообщений.
    dp = updater.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', enter)],
        states={
            1: [MessageHandler(Filters.text, command_room, pass_user_data=True)],
        },
        fallbacks=[CommandHandler('stop', stop)]
    )
    dp.add_handler(conv_handler)

    print('Started!')
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
