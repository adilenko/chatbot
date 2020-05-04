
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