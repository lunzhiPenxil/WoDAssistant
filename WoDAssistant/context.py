# -*- encoding: utf-8 -*-

import OlivOS
import WoDAssistant

import uuid
import time
import re

dictContext = {}

def get_input(plugin_event: OlivOS.API.Event, regex: str, max_time: int = 60):
    global dictContext
    uuid_token = str(uuid.uuid4())
    token = get_token(plugin_event)
    dictContext[token] = {
        'token': uuid_token,
        're': regex,
        'res': None
    }
    res = None
    for i in range(max_time):
        time.sleep(1)
        if token in dictContext:
            if dictContext[token]['token'] != uuid_token:
                break
            if dictContext[token]['res'] is not None:
                res = dictContext[token]['res']
                break
        else:
            break
    if token in dictContext:
       if dictContext[token]['token'] in [uuid_token, 'miss']:
           dictContext.pop(token)
    return res

def get_input_listener(plugin_event: OlivOS.API.Event):
    global dictContext
    token = get_token(plugin_event)
    message = plugin_event.data.message
    if token in dictContext:
        if result := re.search(dictContext[token]['re'], message):
            dictContext[token]['res'] = result.groups()
        else:
            dictContext[token]['token'] = 'miss'

def get_token(plugin_event: OlivOS.API.Event):
    user_id = None
    host_id = None
    group_id = None
    if 'user_id' in plugin_event.data.__dict__:            
        user_id = str(plugin_event.data.user_id)
    if 'host_id' in plugin_event.data.__dict__:            
        host_id = str(plugin_event.data.host_id)
    if 'group_id' in plugin_event.data.__dict__ :
        group_id = str(plugin_event.data.group_id)
    return f"{host_id}|{group_id}|{user_id}"
