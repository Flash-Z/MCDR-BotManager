#!/usr/bin/python3
# -*-coding:utf-8-*-
"""
Created on 2021/3/2

@author: Jerry_FaGe

updated by FangGiGi
"""
import os
import json
import time
from mcdreforged.api.rtext import *
from mcdreforged.api.decorator import new_thread

PLUGIN_METADATA = {
    'id': 'bot_Kikai_FangGiGi\'s_version',
    'version': '1.0',
    'name': 'bot_manager',  # RText component is allowed
    'description': '储存假人位置朝向信息并提供昵称映射和简化指令',  # RText component is allowed
    'author': 'Jerry-FaGe, FangGiGi二改',
    'link': 'https://github.com/Flash-Z/MCDR-BotManager',
    'dependencies': {
        'mcdreforged': '>=1.0.0',
        'minecraft_data_api': '*',
    }
}

config_path = './config/BotKikai.json'
prefix_short = '!!bk'
prefix = '!!botkikai'
permission_bot = 1  # 操作假人(spawn,use,kill)的最低权限  guest: 0, user: 1, helper: 2, admin: 3, owner: 4
permission_list = 3  # 操作假人列表(add,remove)的最低权限  guest: 0, user: 1, helper: 2, admin: 3, owner: 4
dimension_convert = {
    '0': 'minecraft:overworld',
    '-1': 'minecraft:the_nether',
    '1': 'minecraft:the_end',
    'overworld': 'minecraft:overworld',
    'the_nether': 'minecraft:the_nether',
    'the_end': 'minecraft:the_end',
    'nether': 'minecraft:the_nether',
    'end': 'minecraft:the_end',
    'minecraft:overworld': 'minecraft:overworld',
    'minecraft:the_nether': 'minecraft:the_nether',
    'minecraft:the_end': 'minecraft:the_end',
    'zhushijie': 'minecraft:overworld',
    'diyu': 'minecraft:the_nether',
    'xiajie': 'minecraft:the_nether',
    'modi': 'minecraft:the_end'
}
bot_dic = {}
bot_list = []
help_head = """
================== §bBotKikai §r==================
§6欢迎使用由@Jerry-FaGe开发、FangGiGi二改的假人器械映射插件！
§6你可以在Github搜索MCDR-BotManager找到本项目！
本插件中§d{prefix_short}§r与§d{prefix}§r效果相同，两者可以互相替换
""".format(prefix=prefix, prefix_short=prefix_short)
help_body = {
    f"§b{prefix_short}": "§r显示本帮助信息",
    f"§b{prefix_short} list": "§r显示假人列表",
    f"§b{prefix_short} reload": "§r重载插件配置",
    f"§b{prefix_short} add <name> <kikai>": "§r使用当前玩家参数添加名为<name>用于<kikai>的假人",
    f"§b{prefix_short} add <name> <kikai> <dim> <pos> <facing>": "§r自定义添加名为<name>用于<kikai>的假人",
    f"§b{prefix_short} del <kikai>": "§r从假人列表移除用于<kikai>的假人",
    f"§b{prefix_short} <kikai>": "§r查找单个假人",
    f'§b{prefix_short} <kikai> spawn': "§r召唤一个用于<kikai>的假人",
    f"§b{prefix_short} <kikai> kill": "§r干掉用于<kikai>的假人",
    f"§b{prefix_short} <kikai> use": "§r假人右键一次",
    f"§b{prefix_short} <kikai> huse": "§r假人持续右键",
    f"§b{prefix_short} <kikai> iatk": "§r假人间隔14gt攻击",
    f"§b{prefix_short} <kikai> glowing": "§r假人发光两分钟",
    f"§b{prefix_short} <kikai> stop": "§r假人停止一切动作",
}


def read():
    global bot_dic
    with open(config_path, encoding='utf8') as f:
        bot_dic = json.load(f)


def save():
    with open(config_path, 'w', encoding='utf8') as f:
        json.dump(bot_dic, f, indent=4, ensure_ascii=False)


def search(kikai):
    for k, v in bot_dic.items():
        if kikai in v['nick']:
            return k


def auth_player(player):
    """验证玩家是否为bk假人"""
    lower_dic = {i.lower(): i for i in bot_dic}
    bot_name = lower_dic.get(player.lower(), None)
    return bot_name if bot_name else None


def get_pos(server, info):
    api = server.get_plugin_instance('minecraft_data_api')
    pos = api.get_player_info(info.player, 'Pos')
    dim = api.get_player_info(info.player, 'Dimension')
    facing = api.get_player_info(info.player, 'Rotation')
    return pos, dim, facing


def spawn_cmd(server, info, name):
    dim = bot_dic[name]['dim']
    pos = ' '.join([str(i) for i in bot_dic[name]['pos']])
    facing = bot_dic[name]['facing']
    if info.is_player:
        return f'/execute as {info.player} run player {name} spawn at {pos} facing {facing} in {dim}'
    else:
        return f'/player {name} spawn at {pos} facing {facing} in {dim}'


def spawn(server, info, name):
    return spawn_cmd(server, info, name)


def kill(name):
    return f'/player {name} kill'


def use(name):
    return f'/player {name} use'


def attack_14gt(name):
    return f'/player {name} attack interval 14'


def hold_use(name):
    return f'/player {name} use continuous'

def glowing(name):
    return f'/effect give {name} glowing 120'

def stop(name):
    return f'/player {name} stop'


@new_thread(PLUGIN_METADATA["name"])
def operate_bot(server, info, args):
    global bot_dic, bot_list
    permission = server.get_permission_level(info)
    if len(args) == 1:
        head = [help_head]
        body = [RText(f'{k} {v}\n').c(
            RAction.suggest_command, k.replace('§b', '')).h(v)
                for k, v in help_body.items()]
        server.reply(info, RTextList(*(head + body)))

    elif len(args) == 2:
        if args[1] == "list":
            c = ['']
            
            for name, bot_info in bot_dic.items():
                bot_msg = RTextList(
                    '\n',
                    RText('§b[spawn]  ').c(
                        RAction.run_command, spawn(server, info, name)).h(f'§6{name}§7上线'),
                    RText('§b[kill]  ').c(
                        RAction.run_command, kill(name)).h(f'下线§6{name}'),
                    RText('§b[use_once]  ').c(
                        RAction.run_command, use(name)).h(f'§6{name}§7右键一次'),
                    RText('§b[use-hold]  ').c(
                        RAction.run_command, hold_use(name)).h(f'§6{name}§7持续使用'),
                    RText('§b[attack-14gt]  ').c(
                    RAction.run_command, attack_14gt(name)).h(f'§6{name}§7间隔14gt攻击'),
                    RText('§b[stop]  ').c(
                        RAction.run_command, stop(name)).h(f'§6{name}§7停止动作'),
                    RText('§b[glowing]  ').c(
                        RAction.run_command, glowing(name)).h(f'§6{name}§7发光两分钟'),
                    RText(f'§7{name}' if name not in bot_list else f'§a{name}').h(
                        f'§7描述:§6 {bot_dic.get(name)["nick"][1]}\n',
                        f'§7维度:§6 {bot_dic.get(name)["dim"]}\n',
                        f'§7坐标:§6 {bot_dic.get(name)["pos"]}\n',
                        f'§7朝向:§6 {bot_dic.get(name)["facing"]}'
                    )
                )
                
                c.append(bot_msg)
            server.reply(info, RTextList(*c))

        elif args[1] == "reload":
            try:
                read()
                server.say('§b[BotKikai]§a由玩家§d{}§a发起的BotKikai重载成功'.format(info.player))
            except Exception as e:
                server.say('§b[BotKikai]§4由玩家§d{}§4发起的BotKikai重载失败：{}'.format(info.player, e))

        elif search(args[1]):
            name = search(args[1])
            msg = RTextList(
                RText('§b[spawn]  ').c(
                    RAction.run_command, spawn(server, info, name)).h(f'§6{name}§7上线'),
                RText('§b[kill]  ').c(
                    RAction.run_command, kill(name)).h(f'下线§6{name}'),
                RText('§b[use_once]  ').c(
                    RAction.run_command, use(name)).h(f'§6{name}§7右键一次'),
                RText('§b[use-hold]  ').c(
                    RAction.run_command, hold_use(name)).h(f'§6{name}§7持续使用'),
                RText('§b[attack-14gt]  ').c(
                RAction.run_command, attack_14gt(name)).h(f'§6{name}§7间隔14gt攻击'),
                RText('§b[stop]  ').c(
                    RAction.run_command, stop(name)).h(f'§6{name}§7停止动作'),
                RText('§b[glowing]  ').c(
                    RAction.run_command, glowing(name)).h(f'§6{name}§7发光两分钟'),
                RText(f'§7{name}' if name not in bot_list else f'§a{name}').h(
                    f'§7描述:§6 {bot_dic.get(name)["nick"][1]}\n',
                    f'§7维度:§6 {bot_dic.get(name)["dim"]}\n',
                    f'§7坐标:§6 {bot_dic.get(name)["pos"]}\n',
                    f'§7朝向:§6 {bot_dic.get(name)["facing"]}'
                )
            )
            server.reply(info, msg)
            
        else:
            server.reply(info, f"§b[BotKikai]§4未查询到§d{args[1]}§4对应的假人")

    elif len(args) == 3:
        if args[1] == "del" and permission >= permission_list:
            name = search(args[2])
            if name:
                del bot_dic[name]
                bot_list.remove(name) if name in bot_list else bot_list
                save()
                server.reply(info, f'§b[BotKikai]§a已删除机器人{name}')
            else:
                server.reply(info, f"§b[BotKikai]§4未查询到§d{args[1]}§4对应的假人")

        else:
            name = search(args[1])
            if name:
                if args[2] == "spawn" and permission >= permission_bot:
                    if name not in bot_list:
                        server.execute(spawn(server, info, name))
                        server.reply(info, f"§b[BotKikai]§a已创建假人§d{name}")
                    else:
                        server.reply(info, f"§b[BotKikai]§4假人§d{name}§4已经在线")

                elif args[2] == "kill" and permission >= permission_bot:
                    if name in bot_list:
                        server.execute(kill(name))
                        server.reply(info, f"§b[BotKikai]§a假人§d{name}§a已被下线")

                elif args[2] == "use" and permission >= permission_bot:
                    if name not in bot_list:
                        server.execute(spawn(server, info, name))
                        server.reply(info, f"§b[BotKikai]§a已自动创建假人§d{name}")
                        time.sleep(2)
                    server.execute(use(name))
                    server.reply(info, f"§b[BotKikai]§a假人§d{name}§a右键一次")

                elif args[2] == "huse" and permission >= permission_bot:
                    if name not in bot_list:
                        server.execute(spawn(server, info, name))
                        server.reply(info, f"§b[BotKikai]§a已自动创建假人§d{name}")
                        time.sleep(2)
                    server.execute(hold_use(name))
                    server.reply(info, f"§b[BotKikai]§a假人§d{name}§a持续右键")

                elif args[2] == "iatk" and permission >= permission_bot:
                    if name not in bot_list:
                        server.execute(spawn(server, info, name))
                        server.reply(info, f"§b[BotKikai]§a已自动创建假人§d{name}")
                        time.sleep(2)
                    server.execute(attack_14gt(name))
                    server.reply(info, f"§b[BotKikai]§a假人§d{name}§a间隔14gt攻击")
                
                elif args[2] == "stop" and permission >= permission_bot:
                    server.execute(stop(name))
                    server.reply(info, f"§b[BotKikai]§a假人§d{name}§a停止动作")
                    
                elif args[2] == "glowing" and permission >= permission_bot:
                    server.execute(glowing(name))
                    server.reply(info, f"§b[BotKikai]§a假人§d{name}§a发光两分钟")

                else:
                    server.reply(info, f"§b[BotKikai]§4参数输入错误，输入§6{prefix_short}§4查看帮助信息")
            else:
                server.reply(info, f"§b[BotKikai]§4未查询到§d{args[1]}§4对应的假人")

    elif len(args) == 4:
        if args[1] == 'add' and permission >= permission_list:
            nick_ls = [] if bot_dic.get(args[2], None) is None else bot_dic.get(args[2])['nick']
            if args[2] not in nick_ls:
                nick_ls.append(args[2])
            nick_ls.append(args[3]) if args[3] != args[2] else nick_ls
            pos, dim, facing = get_pos(server, info)
            bot_dic[args[2]] = {
                'nick': nick_ls,
                'dim': dim,
                'pos': pos,
                'facing': f'{facing[0]} {facing[1]}'
            }
            save()
            server.reply(info, f'§b[BotKikai]§a已添加假人{args[2]}')
        else:
            server.reply(info, '§b[BotKikai]§4命令格式不正确或权限不足')

    elif len(args) == 10:
        if args[1] == 'add' and permission >= permission_list:
            if args[4] in dimension_convert.keys():
                dim = dimension_convert[args[4]]
                pos = [int(i) for i in [args[5], args[6], args[7]]]
                facing = f'{args[8]} {args[9]}'
                nick_ls = [] if bot_dic.get(args[2], None) is None else bot_dic.get(args[2])['nick']
                if args[2] not in nick_ls:
                    nick_ls.append(args[2])
                nick_ls.append(args[3]) if args[3] != args[2] else nick_ls
                bot_dic[args[2]] = {
                    'nick': nick_ls,
                    'dim': dim,
                    'pos': pos,
                    'facing': facing
                }
                save()
                server.reply(info, f'§b[BotKikai]§a已添加假人{args[2]}')
            else:
                server.reply(info, '§b[BotKikai]§4无法识别的维度')
        else:
            server.reply(info, '§b[BotKikai]§4命令格式不正确或权限不足')


def on_load(server, old):
    global bot_list
    server.register_help_message(f'{prefix_short}', RText(
        '假人器械映射').c(RAction.run_command, f'{prefix_short}').h('点击查看帮助'))
    if old is not None and old.bot_list is not None:
        bot_list = old.bot_list
    else:
        bot_list = []
    if not os.path.isfile(config_path):
        save()
    else:
        try:
            read()
        except Exception as e:
            server.say('§b[BotKikai]§4配置加载失败，请确认配置路径是否正确：{}'.format(e))


def on_player_joined(server, player, info):
    bot_name = auth_player(player)
    if bot_name:
        if bot_name not in bot_list:
            bot_list.append(bot_name)


def on_player_left(server, player):
    bot_name = auth_player(player)
    if bot_name:
        if bot_name in bot_list:
            bot_list.remove(bot_name)


def on_info(server, info):
    if info.is_user:
        if info.content.startswith(prefix) or info.content.startswith(prefix_short):
            info.cancel_send_to_server()
            args = info.content.split(' ')
            operate_bot(server, info, args)


def on_server_stop(server, return_code):
    global bot_list
    bot_list = []

