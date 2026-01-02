# -*- encoding: utf-8 -*-

import OlivOS
import WoDAssistant

import threading
import time
import traceback
import re

def unity_init_after(plugin_event: None, Proc: OlivOS.pluginAPI.shallow):
    WoDAssistant.data.gProc = Proc
    WoDAssistant.dataIO.init_data()
    threading.Thread(target = threadingSend).start()

def unity_group_reply(plugin_event: OlivOS.API.Event, Proc: OlivOS.pluginAPI.shallow):
    userID = plugin_event.data.user_id
    if str(userID) not in WoDAssistant.data.listAdmin:
        return
    botHash = plugin_event.bot_info.hash
    groupID = plugin_event.data.group_id
    message_str: str = plugin_event.data.message
    message_str = message_str.lower()
    message_str = message_str.strip(' ')
    command_this = '/wod'
    if message_str.startswith(command_this):
        message_str = message_str.lstrip(command_this)
        message_str = message_str.lstrip(' ')
        command_this = '帮助'
        if message_str.startswith(command_this):
            plugin_event.reply(
                ' ==== WoD助手 ==== \n'
                '/wod 帮助\n'
                '  - 查看帮助\n'
                '/wod 绑定团队 [团队ID]\n'
                '  - 在群聊中发送以绑定播报\n'
                '/wod 解绑团队 [团队ID]\n'
                '  - 在群聊中发送以解绑播报\n'
                '/wod 刷新\n'
                '  - 立即进行一次刷新'
            )
            return
        command_this = '绑定团队'
        if message_str.startswith(command_this):
            message_str = message_str.lstrip(command_this)
            message_str = message_str = message_str.lstrip(' ')
            partyID = get_int_safe(message_str)
            if partyID is None:
                plugin_event.reply('非法的团队ID')
            else:
                if partyID not in WoDAssistant.data.listPartyID:
                    WoDAssistant.data.listPartyID.append(partyID)
                if botHash not in WoDAssistant.data.listBroadcastGroup \
                or type(WoDAssistant.data.listBroadcastGroup[botHash]) is not dict:
                    WoDAssistant.data.listBroadcastGroup[botHash] = {}
                if str(partyID) not in WoDAssistant.data.listBroadcastGroup[botHash] \
                or type(WoDAssistant.data.listBroadcastGroup[botHash][str(partyID)]) is not list:
                    WoDAssistant.data.listBroadcastGroup[botHash][str(partyID)] = []
                if str(groupID) not in WoDAssistant.data.listBroadcastGroup[botHash][str(partyID)]:
                    WoDAssistant.data.listBroadcastGroup[botHash][str(partyID)].append(str(groupID))
                WoDAssistant.dataIO.save_data()
                plugin_event.reply('已将该团队绑定至本群')
            return
        command_this = '解绑团队'
        if message_str.startswith(command_this):
            message_str = message_str.lstrip(command_this)
            message_str = message_str = message_str.lstrip(' ')
            partyID = get_int_safe(message_str)
            if partyID is None:
                plugin_event.reply('非法的团队ID')
            else:
                if botHash in WoDAssistant.data.listBroadcastGroup \
                and type(WoDAssistant.data.listBroadcastGroup[botHash]) is dict \
                and str(partyID) in WoDAssistant.data.listBroadcastGroup[botHash] \
                and type(WoDAssistant.data.listBroadcastGroup[botHash][str(partyID)]) is list:
                    while str(groupID) in WoDAssistant.data.listBroadcastGroup[botHash][str(partyID)]:
                        WoDAssistant.data.listBroadcastGroup[botHash][str(partyID)].remove(str(groupID))
                    if len(WoDAssistant.data.listBroadcastGroup[botHash][str(partyID)]) <= 0:
                        WoDAssistant.data.listBroadcastGroup[botHash].pop(str(partyID))
                flag_hit = False
                for i in WoDAssistant.data.listBroadcastGroup:
                    if str(partyID) in WoDAssistant.data.listBroadcastGroup[i]:
                        flag_hit = True
                        break
                if not flag_hit:
                    if type(WoDAssistant.data.listPartyID) is list:
                        while partyID in WoDAssistant.data.listPartyID:
                            WoDAssistant.data.listPartyID.remove(partyID)
                WoDAssistant.dataIO.save_data()
                plugin_event.reply('已将该团队解绑至本群')
            return
        command_this = '刷新'
        if message_str.startswith(command_this):
            WoDAssistant.data.broadcastTimer = 0
            plugin_event.reply('即将刷新')
            return

def get_int_safe(string: str):
    res = None
    try:
        res = int(string)
    except:
        pass
    return res

def sendMessageForce(botHash: str, send_type: str, target_id: str, message: str):
    Proc = WoDAssistant.data.gProc
    if Proc is not None \
    and botHash in Proc.Proc_data['bot_info_dict']:
        pluginName = WoDAssistant.data.pluginName
        plugin_event = OlivOS.API.Event(
            OlivOS.contentAPI.fake_sdk_event(
                bot_info = Proc.Proc_data['bot_info_dict'][botHash],
                fakename = pluginName
            ),
            Proc.log
        )
        plugin_event.send(send_type, target_id, message)

def threadingSend():
    while True:
        threadingSendUnit()
        WoDAssistant.data.broadcastTimer = 300
        while WoDAssistant.data.broadcastTimer > 0:
            WoDAssistant.data.broadcastTimer -= 1
            time.sleep(1)

def threadingSendUnit():
    for partyID in WoDAssistant.data.listPartyID:
        try:
            WoDAssistant.logger.logProc(2, f"开始更新团队[ID:{partyID}]的数据")
            messageList = release_reply(
                WoDAssistant.webAPI.get_groupName(
                    WoDAssistant.webAPI.get_fetchList(partyID),
                    partyID
                ),
                WoDAssistant.webAPI.diff_fetchDropAnalysis(
                    WoDAssistant.webAPI.get_fetchDropAnalysis(partyID),
                    partyID
                )
            )
            WoDAssistant.logger.logProc(2, f'已经完成团队[ID:{partyID}]数据更新')
            for message in messageList:
                time.sleep(1)
                broadcastSend(message, partyID)
        except Exception as e:
            traceback.print_exc()
            WoDAssistant.logger.logProc(4, f'团队[ID:{partyID}]数据更新出现问题')

def broadcastSend(message: str, partyID: int):
    for botHashThis in WoDAssistant.data.listBroadcastGroup:
        if str(partyID) in WoDAssistant.data.listBroadcastGroup[botHashThis]:
            for groupIDThis in WoDAssistant.data.listBroadcastGroup[botHashThis][str(partyID)]:
                sendMessageForce(
                    botHash = botHashThis,
                    send_type = 'group',
                    target_id = groupIDThis,
                    message = message
                )

def release_reply(groupName:str, dataList: list):
    res = []
    for dataListThisObj in dataList:
        dataListThis = dataListThisObj['new']
        old_dataListThis = dataListThisObj['old']
        lastDungeonTime = dataListThis['lastDungeonTime']
        intervalTime = '' if dataListThis['intervalTime'] is None else f"[{dataListThis['intervalTime']}]"
        name = dataListThis['name']
        times = dataListThis['times']
        level = f"Lv. {dataListThis['minLv']} ~ {dataListThis['maxLv']}"
        lvDiff = dataListThis['lvDiff']
        dropListData = []
        for dataListThis_this in dataListThis['dropList']:
            diff_count = 0
            diff_str = ''
            newDrop_str = ''
            uniqType_str = ''
            newDrop = dataListThis_this['newDrop']
            if old_dataListThis is not None:
                for old_dataListThis_this in old_dataListThis['dropList']:
                    if old_dataListThis_this['id'] == dataListThis_this['id']:
                        diff_count = dataListThis_this['total'] - old_dataListThis_this['total']
                        break
            else:
                diff_count = dataListThis_this['total']
            flagNotFirst = times > 1
            if (flagNotFirst or newDrop) and diff_count > 0:
                diff_str = f" (+{diff_count})"
            if flagNotFirst and diff_count > 0:
                newDrop_str = '☆'
            if newDrop is True:
                newDrop_str = '★'
            if dataListThis_this['uniq'] != 'N':
                uniqType_str = f"[{dataListThis_this['uniq']}]"
            dropListData.append(f"{newDrop_str}{dataListThis_this['name']}{uniqType_str}: {dataListThis_this['total']}{diff_str} / {(dataListThis_this['maxDrop']) if dataListThis_this['maxDrop'] != 0 else '∞'}")
        dropTotalList = '\n'.join(dropListData)
        resThis = f" {'='*2} 「{groupName}」 {'='*2}\n{intervalTime}{name} - 第{times}次\n{level} 难度{lvDiff}\n{lastDungeonTime}\n {'='*4} 【全部产出】 {'='*4}\n{dropTotalList}"
        res.append(resThis)
    res.reverse()
    return res
