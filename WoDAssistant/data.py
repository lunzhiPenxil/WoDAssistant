# -*- encoding: utf-8 -*-

import OlivOS

import platform

pluginName = 'WoD小助手'

version = '0.4.9'
svn = 49

OlivOSInfo = f"[Python {platform.python_version()} OlivOS {OlivOS.infoAPI.OlivOS_Version}]"

dataPath = './plugin/data/WoDAssistant'

gProc: 'OlivOS.pluginAPI.shallow|None' = None

listAdmin = []
listBroadcastGroup = {}
listPartyID = []

broadcastTimer = 300
