import os
import re

import httpx
from nonebot import on_command, logger
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Bot
from nonebot.internal.matcher import Matcher

On = on_command("fo-on", aliases={"开启念佛模式", "开启诵经模式"})
Off = on_command("fo-off", aliases={"关闭念佛模式", "关闭诵经模式"})


async def create_cache(group_id, group_name, group_card) -> None:
    """创建群信息缓存"""
    # 若不存在文件夹则进行创建
    if not os.path.exists("GroupCache"):
        logger.warning("对应文件夹不存在，将创建新文件夹")
        os.mkdir("GroupCache")
    #  腾讯qq群头像原生接口
    group_profile = 'http://p.qlogo.cn/gh/{}/{}/640/'.format(group_id,group_id)
    img = httpx.get(group_profile).content
    with open('GroupCache/{}：{}.jpg'.format(group_name, group_card), 'wb') as f:
        f.write(img)
        f.close()
        logger.success("缓存文件创建成功~")


async def load_cache() -> tuple[str, str, str]:
    """读取群信息缓存"""
    for filename in os.listdir("GroupCache/"):
        pattern = '[A-Za-z0-9_\u4e00-\u9fa5]+'
        group_name = re.findall('({})：{}\.jpg'.format(pattern, pattern), filename)[0]
        bot_card = re.findall('{}：({})\.jpg'.format(pattern, pattern), filename)[0]
        logger.success("读取群信息缓存成功！")
        return group_name, bot_card, filename


@On.handle()
async def fo_on(bot: Bot, event: GroupMessageEvent, matcher: Matcher):
    #  念佛初始化：缓存原始信息，修改群名称、群头像群名片
    group_id = event.group_id
    user_id = bot.self_id
    group_info = await bot.get_group_info(
        group_id=group_id)
    member_info = await bot.get_group_member_info(
        group_id=group_id,
        user_id=int(user_id)
    )
    await create_cache(
        group_id,
        group_info['group_name'],
        member_info['card'])  # 缓存原始信息

    await bot.set_group_name(
        group_id=group_id,
        group_name="净")
    await bot.set_group_card(
        group_id=group_id,
        user_id=int(user_id),
        card="功德无量"
    )
    profile = "http://m.gx8899.com/uploads/allimg/2016070112/1irc0riem02.jpg"
    await bot.call_api(
        "set_group_portrait",
        group_id=group_id,
        file=profile
    )
    await bot.set_group_whole_ban(group_id=group_id)  # 启动清净模式
    logger.success("念佛环境准备完成")
    await matcher.finish("阿弥陀佛！念佛绝佳环境已准备完毕")


@Off.handle()
async def fo_off(bot: Bot, event: GroupMessageEvent, matcher: Matcher):
    group_name, group_card, filename = await load_cache()
    group_id = event.group_id
    user_id = bot.self_id
    await bot.set_group_name(
        group_id=group_id,
        group_name=group_name)
    await bot.set_group_card(
        group_id=group_id,
        user_id=int(user_id),
        card=group_card
    )
    abs_filepath = os.path.abspath('GroupCache/' + filename)
    await bot.call_api(
        "set_group_portrait",
        group_id=group_id,
        file="file:///" + abs_filepath  # 格式化绝对路径
    )
    await bot.set_group_whole_ban(group_id=group_id, enable=False)  # 关闭清净模式
    logger.success("念佛模式已关闭")
    await matcher.finish("阿弥陀佛！您已关闭念佛模式")