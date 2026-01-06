# -*- encoding: utf-8 -*-

import OlivOS
import WoDAssistant

import threading
import time
import traceback

def unity_init_after(plugin_event: None, Proc: OlivOS.pluginAPI.shallow):
    WoDAssistant.data.gProc = Proc
    WoDAssistant.dataIO.init_data()
    WoDAssistant.dataIO.save_data()
    threading.Thread(target = threadingSend).start()

def unity_group_reply(plugin_event: OlivOS.API.Event, Proc: OlivOS.pluginAPI.shallow):
    WoDAssistant.context.get_input_listener(plugin_event)
    userID = str(plugin_event.data.user_id)
    botHash = str(plugin_event.bot_info.hash)
    groupID = str(plugin_event.data.group_id)
    message_str: str = plugin_event.data.message
    message_str = message_str.strip(' ')
    command_this = '/wod'
    message_str = message_str[:len(command_this)].lower() + message_str[len(command_this):] if len(message_str) > 4 else message_str.lower()
    if message_str.startswith(command_this):
        message_str = message_str.lstrip(command_this)
        message_str = message_str.lstrip(' ')
        if 0 == len(message_str):
            plugin_event.reply(
                f"WoD小助手 WoDAssistant By lunzhiPenxil Ver.{WoDAssistant.data.version}({WoDAssistant.data.svn}) {WoDAssistant.data.OlivOSInfo}\n"
                "欢迎使用本机器人! 请使用[/wod 帮助]查看帮助"
            )
            return
        command_this = '帮助'
        if message_str.startswith(command_this):
            reply_message_str = (
                ' ==== WoD助手 ==== \n'
                '/wod\n'
                '  - 查看机器人信息\n'
                '/wod 帮助\n'
                '  - 查看帮助\n'
                '/wod 查询物品 [物品名称]\n'
                '  - 用名称查询物品\n'
                '/wod 查询技能 [技能名称]\n'
                '  - 用名称查询技能'
            )
            if isAdmin(userID):
                reply_message_str += (
                    '\n'
                    '/wod 订阅团队 [团队ID]\n'
                    '  - 在群聊中发送以订阅播报\n'
                    '/wod 解绑团队 [团队ID]\n'
                    '  - 在群聊中发送以解绑播报\n'
                    '/wod 订阅列表\n'
                    '  - 查看本群的订阅列表\n'
                    '/wod 查询团队 [团队名称]\n'
                    '  - 用名称查询团队ID\n'
                    '/wod 刷新\n'
                    '  - 立即进行一次刷新'
                )
            plugin_event.reply(reply_message_str)
            return
        command_this = '查询物品'
        if message_str.startswith(command_this):
            message_str = message_str.lstrip(command_this)
            message_str = message_str.lstrip(' ')
            if len(message_str) > 0:
                itemName = message_str
                itemData = WoDAssistant.webAPI.get_itemSearchByName(itemName)
                if len(itemData) > 0:
                    if len(itemData) == 1:
                        plugin_event.reply(
                            WoDAssistant.webAPI.get_itemInfo(itemData[0])
                        )
                    else:
                        reply_message_str = '找到如下相近物品:\n'
                        reply_message_str += WoDAssistant.webAPI.get_listByData(itemData)
                        reply_message_str += f"\n请输入[1-{len(itemData)}]的数字"
                        plugin_event.reply(reply_message_str)
                        regex_str = r'^(10|[1-9])$'
                        if len(itemData) < 10:
                            regex_str = f'^([1-{len(itemData)}])$'
                        if result := WoDAssistant.context.get_input(
                            plugin_event = plugin_event,
                            regex = regex_str
                        ):
                            if len(result) >= 1:
                                if result_int := get_int_safe(result[0]):
                                    plugin_event.reply(
                                        WoDAssistant.webAPI.get_itemInfo(itemData[result_int - 1])
                                    )
                        else:
                            reply_message_str = f"请输入[1-{len(itemData)}]的数字"
                else:
                    plugin_event.reply('未找到相近物品')
            else:
                plugin_event.reply('请输入物品名称')
            return
        command_this = '查询技能'
        if message_str.startswith(command_this):
            message_str = message_str.lstrip(command_this)
            message_str = message_str.lstrip(' ')
            if len(message_str) > 0:
                skillName = message_str
                skillData = WoDAssistant.webAPI.get_skillSearchByName(skillName)
                if len(skillData) > 0:
                    if len(skillData) == 1:
                        plugin_event.reply(
                            WoDAssistant.webAPI.get_skillInfo(skillData[0])
                        )
                    else:
                        reply_message_str = '找到如下相近技能:\n'
                        reply_message_str += WoDAssistant.webAPI.get_listByData(skillData)
                        reply_message_str += f"\n请输入[1-{len(skillData)}]的数字"
                        plugin_event.reply(reply_message_str)
                        regex_str = r'^(10|[1-9])$'
                        if len(skillData) < 10:
                            regex_str = f'^([1-{len(skillData)}])$'
                        if result := WoDAssistant.context.get_input(
                            plugin_event = plugin_event,
                            regex = regex_str
                        ):
                            if len(result) >= 1:
                                if result_int := get_int_safe(result[0]):
                                    plugin_event.reply(
                                        WoDAssistant.webAPI.get_skillInfo(skillData[result_int - 1])
                                    )
                        else:
                            reply_message_str = f"请输入[1-{len(skillData)}]的数字"
                else:
                    plugin_event.reply('未找到相近技能')
            else:
                plugin_event.reply('请输入技能名称')
            return
        if not isAdmin(userID):
            return
        command_this = '订阅团队'
        if message_str.startswith(command_this):
            message_str = message_str.lstrip(command_this)
            message_str = message_str.lstrip(' ')
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
                if groupID not in WoDAssistant.data.listBroadcastGroup[botHash][str(partyID)]:
                    WoDAssistant.data.listBroadcastGroup[botHash][str(partyID)].append(groupID)
                WoDAssistant.dataIO.save_data()
                plugin_event.reply('已将该团队订阅至本群')
            return
        command_this = '解绑团队'
        if message_str.startswith(command_this):
            message_str = message_str.lstrip(command_this)
            message_str = message_str.lstrip(' ')
            partyID = get_int_safe(message_str)
            if partyID is None:
                plugin_event.reply('非法的团队ID')
            else:
                if botHash in WoDAssistant.data.listBroadcastGroup \
                and type(WoDAssistant.data.listBroadcastGroup[botHash]) is dict \
                and str(partyID) in WoDAssistant.data.listBroadcastGroup[botHash] \
                and type(WoDAssistant.data.listBroadcastGroup[botHash][str(partyID)]) is list:
                    while groupID in WoDAssistant.data.listBroadcastGroup[botHash][str(partyID)]:
                        WoDAssistant.data.listBroadcastGroup[botHash][str(partyID)].remove(groupID)
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
                plugin_event.reply('已将该团队解绑自本群')
            return
        command_this = '订阅列表'
        if message_str.startswith(command_this):
            reply_message_str = ''
            broadcastList = []
            if botHash in WoDAssistant.data.listBroadcastGroup \
            and type(WoDAssistant.data.listBroadcastGroup[botHash]) is dict:
                for i in WoDAssistant.data.listBroadcastGroup[botHash]:
                    if groupID in WoDAssistant.data.listBroadcastGroup[botHash][i]:
                        broadcastList.append(f"  {i} - {WoDAssistant.webAPI.get_groupName(i)}")
            if len(broadcastList) > 0:
                reply_message_str += f"距离下次刷新还有[{WoDAssistant.data.broadcastTimer}]秒\n"
                reply_message_str += '本群订阅列表如下:\n'
                reply_message_str += '\n'.join(broadcastList)
            else:
                reply_message_str += '本群订阅列表为空'
            plugin_event.reply(reply_message_str)
            return
        command_this = '查询团队'
        if message_str.startswith(command_this):
            message_str = message_str.lstrip(command_this)
            message_str = message_str.lstrip(' ')
            partyName = message_str
            reply_message_str = ''
            data = WoDAssistant.webAPI.get_groupSearchByName(partyName = partyName)
            if len(data) > 0:
                reply_message_str += '找到如下相近团队:\n'
                partyList = []
                for i in data:
                    partyIDThis = "未知团队"
                    partyNameThis = "未知团队"
                    if 'id' in i:
                        partyIDThis = i['id']
                        partyNameThis = f"团队[{partyIDThis}]"
                    if 'name' in i:
                        partyNameThis = i['name']
                    partyList.append(f"  {partyIDThis} - {partyNameThis}")
                reply_message_str += '\n'.join(partyList)
            else:
                reply_message_str += '未找到相近团队'
            plugin_event.reply(reply_message_str)
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
                WoDAssistant.webAPI.get_groupName(partyID),
                WoDAssistant.webAPI.diff_fetchDropAnalysis(partyID)
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

def release_reply(groupName:str, dataDict: dict):
    res = []
    dataList: list = dataDict['diff']
    itemDict: dict = dataDict['item']
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
            if str(dataListThis_this['id']) in itemDict:
                diff_count = dataListThis_this['total'] - itemDict[str(dataListThis_this['id'])]
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

# 判断是否为管理
def isAdmin(userID: str):
    return userID in WoDAssistant.data.listAdmin
