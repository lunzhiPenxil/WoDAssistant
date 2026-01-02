# -*- encoding: utf-8 -*-

import OlivOS
import WoDAssistant

class Event(object):
    def init(plugin_event: None, Proc: OlivOS.pluginAPI.shallow):
        pass

    def init_after(plugin_event: None, Proc: OlivOS.pluginAPI.shallow):
        WoDAssistant.msgReply.unity_init_after(plugin_event, Proc)

    def private_message(plugin_event: OlivOS.API.Event, Proc: OlivOS.pluginAPI.shallow):
        WoDAssistant.msgReply.unity_reply(plugin_event, Proc)

    def group_message(plugin_event: OlivOS.API.Event, Proc: OlivOS.pluginAPI.shallow):
        WoDAssistant.msgReply.unity_reply(plugin_event, Proc)
