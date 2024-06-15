import discord
from discord.ext import commands
from datetime import datetime, timedelta
import pickle
import os
from dotenv import load_dotenv


# 加载环境变量
load_dotenv()

# 从环境变量中获取 Discord Bot Token
TOKEN = os.getenv('DISCORD_TOKEN')

# 設定命令前綴，例如 '!' 或 '/'
bot = commands.Bot(command_prefix='/')

# 存儲冷卻時間的文件名稱
COOLDOWN_FILE = 'cooldown.pkl'

# 加載冷卻時間
if os.path.exists(COOLDOWN_FILE) and os.path.getsize(COOLDOWN_FILE) > 0:
    with open(COOLDOWN_FILE, 'rb') as f:
        cooldown = pickle.load(f)
else:
    cooldown = {}

def save_cooldown():
    with open(COOLDOWN_FILE, 'wb') as f:
        pickle.dump(cooldown, f)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} - {bot.user.id}')
    print('------')

@bot.command(name='setgroup')
@commands.has_permissions(manage_roles=True)
async def setgroup(ctx, member: discord.Member, role: discord.Role):
    current_time = datetime.now()
    
    # 檢查該用戶是否在冷卻時間內
    if member.id in cooldown and role.id in cooldown[member.id]:
        cooldown_time = cooldown[member.id][role.id]
        if current_time < cooldown_time + timedelta(hours=72):
            remaining_time = (cooldown_time + timedelta(hours=72) - current_time).total_seconds()
            hours, remainder = divmod(remaining_time, 3600)
            minutes, seconds = divmod(remainder, 60)
            await ctx.send(f'距離重新添加角色 {role.name} 還剩 {int(hours)} 小時 {int(minutes)} 分鐘 {int(seconds)} 秒。')
            return
    
    try:
        await member.add_roles(role)
        await ctx.send(f'成功將 {member.mention} 添加到角色 {role.name} 中！')
        # 清除冷卻時間
        if member.id in cooldown and role.id in cooldown[member.id]:
            del cooldown[member.id][role.id]
            if not cooldown[member.id]:
                del cooldown[member.id]
        save_cooldown()
    except discord.Forbidden as e:
        await ctx.send(f'發生錯誤：{e}')
    except Exception as e:
        await ctx.send(f'發生錯誤：{e}')

@bot.command(name='rmgroup')
@commands.has_permissions(manage_roles=True)
async def rmgroup(ctx, member: discord.Member, role: discord.Role):
    try:
        await member.remove_roles(role)
        await ctx.send(f'成功將 {member.mention} 從角色 {role.name} 中移除！')
        
        # 記錄角色移除的時間
        if member.id not in cooldown:
            cooldown[member.id] = {}
        cooldown[member.id][role.id] = datetime.now()
        save_cooldown()
    except discord.Forbidden as e:
        await ctx.send(f'發生錯誤：{e}')
    except Exception as e:
        await ctx.send(f'發生錯誤：{e}')

@bot.command(name='rmgroupCD')
@commands.has_permissions(manage_roles=True)
async def rmgroup_cd(ctx, member: discord.Member, role: discord.Role):
    try:
        # 移除冷卻時間
        if member.id in cooldown and role.id in cooldown[member.id]:
            del cooldown[member.id][role.id]
            if not cooldown[member.id]:
                del cooldown[member.id]
        save_cooldown()
        
        await ctx.send(f'成功將 {member.mention} 在移除角色 {role.name} 後的冷卻時間歸零。')
    except Exception as e:
        await ctx.send(f'發生錯誤：{e}')

@setgroup.error
async def setgroup_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send('你沒有權限使用這個命令。')
    elif isinstance(error, commands.BadArgument):
        await ctx.send('參數錯誤。請確保你正確地指定了用戶和角色。')
    else:
        await ctx.send(f'發生錯誤：{error}')

@rmgroup.error
async def rmgroup_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send('你沒有權限使用這個命令。')
    elif isinstance(error, commands.BadArgument):
        await ctx.send('參數錯誤。請確保你正確地指定了用戶和角色。')
    else:
        await ctx.send(f'發生錯誤：{error}')

@rmgroup_cd.error
async def rmgroup_cd_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send('你沒有權限使用這個命令。')
    elif isinstance(error, commands.BadArgument):
        await ctx.send('參數錯誤。請確保你正確地指定了用戶和角色。')
    else:
        await ctx.send(f'發生錯誤：{error}')

bot.run(TOKEN)
