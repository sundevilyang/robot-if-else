#!/usr/bin/python3
import logging
import re
from functools import wraps

import requests
from wxpy import *

logging.basicConfig(level=logging.INFO)

# 减少网络层日志的干扰
for m in 'requests', 'urllib3':
    logging.getLogger(m).setLevel(logging.WARNING)

bot = Bot(cache_path=True, console_qr=True)

# 开启 puid 获取功能，指定 puid 映射数据的保存路径
bot.enable_puid('wxpy_puid.pkl')

server_url = 'http://localhost:3000/wechat'
session = requests.Session()

wenyang = ensure_one(bot.friends().search('文洋'))

# 管理员列表，将来可以把其他运营人员加进去
admins = (wenyang,)

# 单群人数限制
single_group_limit = 450

# 所有 CGC 群列表
# 目前为简单处理方式 (按群名), 将来可加强
cgc_groups = list(filter(
    lambda x: re.search(r'Coding Day', str(x.name)),
    bot.groups()
))


def get_reaction(func):
    """
    装饰器：
        将消息发送给服务端，获得对应的回馈操作 (reaction)

    注意: 
        * 当操作类型为 'text' 时会自动执行回复操作
        * 其他类型的操作需要额外在被装饰的函数中实现
    """

    @wraps(func)
    def wrapper(msg):

        # 如果是好友请求，会自动接受，并定位到新的好友
        if msg.type == FRIENDS:
            sender = msg.card.accept()
        else:
            sender = msg.chat

        # 获取消息对应的 reaction
        resp = session.post(server_url, json=dict(
            sender_puid=sender.puid,
            member_puid=msg.member.puid if msg.member else '',
            # 注意: file_path 暂未用到，将来用到时需要另外处理
            message=dict(type=msg.type, text=msg.text, file_path='')
        ))
        resp.raise_for_status()
        reaction = resp.json()

        # 若 reaction 类型为 'text'，则自动执行回复
        if reaction['type'].lower() == 'text':
            sender.send(reaction['info'])

        # 注意: 非 'text' 类型的 reaction 需要在被装饰函数中处理!
        return func(msg, reaction)

    return wrapper


def from_admin(msg):
    """
    判断 msg 的发送者是否为管理员
    """
    if not isinstance(msg, Message):
        raise TypeError('expected Message, got {}'.format(type(msg)))
    from_user = msg.member if isinstance(msg.chat, Group) else msg.sender
    return from_user in admins


# 远程踢人命令: 移出 @<需要被移出的人>
rp_kick = re.compile(r'^移出\s*@(.+?)(?:\u2005?\s*$)')


def remote_kick(msg):
    """
    判断
        1. 消息中是否包含踢人命令
        2. 消息是否来自管理员
    
    若满足条件，则执行移出，并返回回复文本；若未满足条件，也可能返回回复文本，作为错误提示
    
    :return: 回复文本 (无需回复时为 None)
    """
    if msg.type is TEXT:
        match = rp_kick.search(msg.text)
        if match:
            name_to_kick = match.group(1)

            if not from_admin(msg):
                # logger.warning('{} tried to kick {}'.format(
                #     msg.member.name, name_to_kick))
                return '感觉有点不对劲… @{}'.format(msg.member.name)

            member_to_kick = ensure_one(list(filter(
                lambda x: x.name == name_to_kick, msg.chat)))

            if member_to_kick in admins:
                # logger.error('{} tried to kick {} whom was an admin'.format(
                #     msg.member.name, member_to_kick.name))
                return '无法移出 @{}'.format(member_to_kick.name)

            member_to_kick.remove()
            return '成功移出 @{}'.format(member_to_kick.name)


# 新人入群通知的匹配正则
rp_new_member_name = (
    re.compile(r'^"(.+)"通过'),
    re.compile(r'邀请"(.+)"加入'),
)


# 从新人入群通知中获取新人的名称
def get_new_member_name(msg):
    # itchat 1.2.32 版本未格式化群中的 Note 消息
    from itchat.utils import msg_formatter
    msg_formatter(msg.raw, 'Text')

    for rp in rp_new_member_name:
        match = rp.search(msg.text)
        if match:
            return match.group(1)


# 新人入群的欢迎消息
@bot.register(cgc_groups, NOTE)
def welcome(msg):
    name = get_new_member_name(msg)
    if name:
        return '欢迎 {}😉'.format(name)


# 在群中回复用户文本消息　
# noinspection PyUnusedLocal
@bot.register(cgc_groups, TEXT)
@get_reaction
def auto_reply_text_in_groups(msg, reaction):
    # 如果需要上报消息内容、获取服务端的回复，只需要用 `@get_reaction` 装饰函数即可
    # reaction 参数为从服务端获得的 json 内容 (dict)
    # 使用装饰器后，会自动执行 `text` 类的操作
    # 但其他类型的操作需要在被装饰函数内实现

    # 会判断消息 / 满足时才会踢人 / 可能会回复消息
    return remote_kick(msg)


# 机器人自动接受好友请求
# noinspection PyUnusedLocal
@bot.register(msg_types=FRIENDS)
@get_reaction
def auto_accept_friends(msg, reaction):
    pass


# 手动加为好友后自动发送消息
# noinspection PyUnusedLocal
@bot.register(Friend, NOTE)
@get_reaction
def manually_accept_friends(msg):
    # 需要服务端判断消息文本中是否包含 "现在可以开始聊天了"
    # 若包含，需回复加为好友后的第一句话

    # Todo: 请在服务端实现后去掉这个 raise
    raise NotImplementedError

    pass


# 私聊回复用户文本消息
@bot.register(Friend, TEXT)
@get_reaction
def auto_reply_text_to_friends(msg, reaction):
    if reaction['type'] == 'add_member':
        group_name = reaction['info']
        found = bot.groups().search(group_name)

        if found:

            # 扫描已加入的 CGC 群
            joined = list()
            for g in cgc_groups:
                if msg.chat in cgc_groups:
                    joined.append(g)

            if joined:
                # 回复已加入的群列表
                return '您已加入了\n{}'.format('\n'.join(map(lambda x: str(x.name), joined)))
            else:
                # 根据群人数找出适合加入的群 (未满的，人数最多的那个群)
                found.sort(key=len, reverse=True)
                for group in found:
                    if len(group) < single_group_limit:
                        group.add_members(msg.sender, use_invitation=True)
                        return

        # 没有找到，或没有合适的群，则创建新的
        group = bot.create_group([wenyang, msg.sender], topic=group_name)
        cgc_groups.append(group)


embed()
