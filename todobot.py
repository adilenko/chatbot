import json
import requests
import time
import urllib
import threading
import string
from models import Questions
from config import db, URL, questionsList as qsL, usersDict, dispatcher, updater
import traceback
from functools import wraps
from telegram.ext import CommandHandler, MessageHandler, Filters


def logger(func):
    @wraps(func)
    def wrapped(update, context, *args, **kwargs):
        if id in usersDict:
            return func(update, context, *args, **kwargs)
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text="It is not a correct answer! Try again")
            return

    return wrapped


def error_handle(func):
    @wraps(func)
    def wrapped(update, context, *args, **kwargs):
        try:
            return func(update, context, *args, **kwargs)
        except Exception as ex:
            traceback.print_tb(ex.__traceback__)
            start_chat(context, "Press start to begin test", update.effective_chat.id)
            return

    return wrapped


def error_callback(update, context):
    try:
        raise context.error
    except Exception as ex:
        traceback.print_tb(ex.__traceback__)
        start_chat(context, "Press start to begin test", update.effective_chat.id)
        return


# def send_action(action):
#     """Sends `action` while processing func command."""
#     def decorator(func):
#         @wraps(func)
#         def command_func(text, chat_id,**kwargs):
#             text.bot.send_chat_action(chat_id=chat_id, action=action)
#             return func(text, chat_id, **kwargs)
#         return command_func
#     return decorator
#
# send_typing_action = send_action(ChatAction.TYPING)
# send_upload_video_action = send_action(ChatAction.UPLOAD_VIDEO)
# send_upload_photo_action = send_action(ChatAction.UPLOAD_PHOTO)

def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content


def get_users_with_interval(sec):
    def func_wrapper():
        get_users_with_interval(sec)
        global usersDict
        usersDict = db.get_users()
        # print(usersDict)

    t = threading.Timer(sec, func_wrapper)
    t.start()
    return t


def get_json_from_url(url):
    content = get_url(url)
    js = json.loads(content)
    return js


# def get_updates(offset=None):
#     url = URL + "getUpdates?timeout=100"
#     if offset:
#         url += "&offset={}".format(offset)
#     js = get_json_from_url(url)
#     return js
#
# def get_last_update_id(updates):
#     update_ids = []
#     for update in updates["result"]:
#         update_ids.append(int(update["update_id"]))
#     return max(update_ids)
#
# def get_last_chat_id_and_text(updates):
#     num_updates = len(updates["result"])
#     last_update = num_updates - 1
#     text = updates["result"][last_update]["message"]["text"]
#     chat_id = updates["result"][last_update]["message"]["chat"]["id"]
#     return (text, chat_id)
#
#
# def send_message(text, chat_id, reply_markup=None):
#     text = urllib.parse.quote_plus(text)
#     url = URL + "sendMessage?text={}&chat_id={}&parse_mode=Markdown".format(text, chat_id)
#     if reply_markup:
#         url += "&reply_markup={}".format(reply_markup)
#     get_url(url)

def start_chat(context, text, chat):
    keyboard = build_keyboard(["start"])
    context.bot.send_message(chat_id=chat, text=text, reply_markup=keyboard)


def select_subject(context, chat):
    subjects = db.get_subjects()
    keyboard = build_keyboard(subjects)
    context.bot.send_message(chat_id=chat, text="Select subject", reply_markup=keyboard)


def get_next_question(subject, prev_quest_id=0):
    quest_id = db.get_next_question_num_by_subj(subject, prev_quest_id)
    if quest_id is None:
        return None
    return db.get_question_by_id(quest_id)


# def handle_updates(updates):
#     for update in updates["result"]:
#         text = update["message"]["text"]
#         chat = update["message"]["chat"]["id"]
#         handle_user_message(chat, text)

def test_is_finished(context, question, chat):
    start_chat(context, f"Test is finished! \n"
                        f"Correct aswers: {question.correct_answers_num} \n"
                        f"Wrong answers: {question.wrong_answers_num} \n"
                        f" Press Start to repeat", chat)
    db.update_answers(chat, question_id=None)


def send_question(context, quest, chat, retry_question=False):
    guestion_num = quest.id
    answers_prefix = list(map(lambda x: x + ". ", list(string.ascii_uppercase[0:len(quest.all_answers)])))
    global correct_variant
    correct_variant = ""

    def join_lists(x):
        if x[1] == quest.correct_answer:
            global correct_variant
            correct_variant = x[0].strip()
        return x[0] + x[1]

    answers = [join_lists(x) for x in zip(answers_prefix, quest.all_answers)]

    keyboard = build_keyboard(answers_prefix + ["next"]) if retry_question else build_keyboard(answers_prefix)
    # text_message = quest.question + "\n"
    context.bot.send_message(chat_id=chat, text=quest.question)
    for text in answers:
        # text_message += text + "\n"
        context.bot.send_message(chat_id=chat, text=text)
    context.bot.send_message(chat_id=chat, text="Select your answer", reply_markup=keyboard)
    db.update_answers(chat, question_id=guestion_num)
    db.update_answers(chat, correct_variant=correct_variant)


# @error_handle
def handle_user_message(update, context):
    chat = update.effective_chat.id
    text = update.message.text
    if text in ["/start", "start"]:
        db.delete_answer(chat)
        context.bot.send_message(chat_id=chat, text="Welcome to chatbot. Please select chatbot")
        select_subject(context, chat)
        db.add_answer(chat, None)
        return

    answer = db.get_answer(chat)
    guestion_num = answer.question_id
    if text in db.get_subjects() and guestion_num is None:
        # qsL.reset()
        context.bot.send_message(chat_id=chat, text="Please select your answer ")
        db.update_answers(chat, subject=text)
        quest = get_next_question(text)
        send_question(context, quest, chat)
        return

    if guestion_num is None:
        start_chat("Press start to begin test", chat)
        return
    quest = db.get_question_by_id(guestion_num)

    if text == "next":
        quest = get_next_question(answer.subject, answer.question_id)  # text = guestion.subject
        if quest is None:
            test_is_finished(context, answer, chat)
            return
        else:
            send_question(context, quest, chat)
            return

    if text == answer.correct_variant:
        context.bot.send_message(chat_id=chat, text="You are right!")
        answer.correct_answers_num += 1
        db.update_answers(chat, correct_answers_num=answer.correct_answers_num)

        quest = get_next_question(answer.subject, answer.question_id)
        if quest is None:
            test_is_finished(context, answer, chat)
            return
        else:
            send_question(context, quest, chat)
            return

    if text != answer.correct_variant:
        context.bot.send_message(chat_id=chat, text="It is not a correct answer! Try again")
        answer.wrong_answers_num += 1
        db.update_answers(chat, wrong_answers_num=answer.wrong_answers_num)
        send_question(context, quest, chat, retry_question=True)


def build_keyboard(items):
    keyboard = [[item] for item in items]
    reply_markup = {"keyboard": keyboard, "one_time_keyboard": True, "resize_keyboard": True}
    return json.dumps(reply_markup)


def main():
    # start_handler = CommandHandler('start', handle_user_message)
    # dispatcher.add_handler(start_handler)
    message_handler = MessageHandler(Filters.text | Filters.command, handle_user_message)
    dispatcher.add_handler(message_handler)
    dispatcher.add_error_handler(error_callback)
    updater.start_polling()
    updater.idle()
    # db.setup()
    # last_update_id = None
    # interval =5
    # get_users_with_interval(interval)
    # time.sleep(interval)
    # while True:
    #     updates = get_updates(last_update_id)
    #     if len(updates["result"]) > 0:
    #         last_update_id = get_last_update_id(updates) + 1
    #         handle_updates(updates)
    #     time.sleep(0.5)


if __name__ == '__main__':
    main()
