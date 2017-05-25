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
        return '欢迎 {}😉，请更改群名片（格式：城市-角色-职业-名字），记得去 https://girlscodingday.org/ 报名哦'.format(name)


# 在群中回复用户文本消息　
# noinspection PyUnusedLocal
@bot.register(cgc_groups, TEXT)
@get_reaction
def auto_reply_text_in_groups(msg, reaction):
    # 如果需要上报消息内容、获取服务端的回复，只需要用 `@get_reaction` 装饰函数即可
    # reaction 参数为从服务端获得的 json 内容 (dict)
    # 使用装饰器后，会自动执行 `text` 类的操作
    # 但其他类型的操作需要在被装饰函数内实现

    # 在这个函数中，除了回复文本外，没有其他额外的操作，所以直接 pass (下同)
    pass


# 机器人自动接受好友请求
# noinspection PyUnusedLocal
@bot.register(msg_types=FRIENDS)
@get_reaction
def auto_accept_friends(msg, reaction):
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
