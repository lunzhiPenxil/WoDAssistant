# -*- encoding: utf-8 -*-

import OlivOS
import WoDAssistant

pluginName = 'WoD小助手'

gProc = None

class Event(object):
    def init(plugin_event, Proc):
        pass

    def init_after(plugin_event, Proc):
        WoDAssistant.msgReply.unity_init_after(plugin_event, Proc)

    def private_message(plugin_event, Proc):
        WoDAssistant.msgReply.unity_reply(plugin_event, Proc)

    def group_message(plugin_event, Proc):
        WoDAssistant.msgReply.unity_reply(plugin_event, Proc)
