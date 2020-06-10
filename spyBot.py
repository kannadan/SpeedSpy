import os
from discord.ext import commands
from dotenv import load_dotenv
import asyncio
import speedrun
import db

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
CHANNEL = int(os.getenv('DISCORD_CHANNEL'))
OWNER = int(os.getenv('OWNER_ID'))
loop = asyncio.get_event_loop()


def checkMember(member):
    if member.nick:
        name = member.nick
    else:
        name = member.name
    name = name.replace(" ", "")
    if not db.getUser(name):
        user = speedrun.getUser(name)
        if user:
            db.insertWhitelist(user["id"], name)
            bests = speedrun.getBest(user)
            if bests:
                pb = speedrun.parsePB(bests, user["id"])
                for run in pb:
                    db.insertrun(run)
        else:
            db.insertBlacklist(name)

async def backgroundUpdateTask():
    await bot.wait_until_ready()
    await asyncio.sleep(3600)
    while not bot.is_closed():
        try:
            print("Background update")
            users = db.getAllWhite()
            for user in users:
                updateMember(user[1])
            print("update done")
            await asyncio.sleep(7200)
        except Exception as e:
            print(str(e))
            await asyncio.sleep(7200)



def updateMember(name):
    user = speedrun.getUser(name)
    if user:
        bests = speedrun.getBest(user)
        if bests:
            pb = speedrun.parsePB(bests, user["id"])
            old = db.getUserruns(user["id"])
            oldids = [x[0] for x in old]
            for run in pb:
                if run["runid"] not in oldids:
                    for oldrun in old:
                        if oldrun[3] == run["game"] and oldrun[4] == run["category"]:
                            db.deleterun(oldrun[0])
                    db.insertrun(run)
                    loop.create_task(announceRun(run))
                else:
                    for oldrun in old:
                        if oldrun[0] == run["runid"] and oldrun[2] != run["place"]:
                            db.updaterun(run)
                            loop.create_task(announceDrop(run))
                            break

async def announceRun(run):
    channel = bot.get_channel(CHANNEL)
    name = db.getUserName(run["userid"])
    await channel.send('{} is now rank {} in {} {}'.format(name, run["place"], run["game"], run["category"]))

async def announceDrop(run):
    channel = bot.get_channel(CHANNEL)
    name = db.getUserName(run["userid"])
    await channel.send('{} has dropped to rank {} in {} {}'.format(name, run["place"], run["game"], run["category"]))

#client = discord.Client()
bot = commands.Bot(command_prefix='/')

@bot.event
async def on_ready():
    for guild in bot.guilds:
        if guild.name == GUILD:
            break

    print(
        f'{bot.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )
    count = 0
    users = guild.member_count
    print("guild has {} members\n".format(guild.member_count))
    print("Checking speedrun.com")
    db.createTables()
    print("{}/{} members verified".format(count, users))
    for member in guild.members:
        checkMember(member)
        count += 1
        if count % 10 == 0:
            print("{}/{} members verified".format(count, users))
            await asyncio.sleep(10)
    print("{}/{} members verified".format(count, users))

@bot.event
async def on_member_join(member):
    print("checking new member")
    checkMember(member)

@bot.event
async def on_member_update(old, member):
    print("checking member update")
    if old.nick != member.nick:
        checkMember(member)


@bot.command(name='update', help='Checks for new runs in speedrun.com')
async def checkUpdates(ctx):
    print("Run update")
    users = db.getAllWhite()
    await ctx.send("Will now check for new runs")
    for user in users:
        updateMember(user[1])
    print("update done")

@bot.command(name='runlist', help='/runlist <name>: lists all runs that person has. No name will list all runs on server')
async def sendRankings(ctx, name: str = ""):
    if name:
        users = db.getUser(name)
    else:
        if ctx.message.author.id != OWNER:
            await ctx.send("Needs a name")
            return
        users = db.getAllWhite()
        await ctx.send("This might take a while")
    if not users or len(users[0]) == 1:
        await ctx.send("No runs on such user")
        return
    msg = ""
    for user in users:
        msg = msg + "**{}**\n".format(user[1])
        runs = db.getUserruns(user[0])
        for run in runs:
            msg = msg + "> Rank {} on {} {}\n".format(run[2], run[3], run[4])
            if len(msg) > 1700:
                await ctx.send(msg)
                msg = ""
    if msg != "":
        await ctx.send(msg)

@bot.command(name='follow', help='/follow <name> adds that name to be followed on speedrun.com')
async def follow(ctx, name : str = ""):
    if not name:
        await ctx.send("You need to give a name")
        return
    user = db.getUser(name)
    if not user or len(user[0]) == 1:
        userSr = speedrun.getUser(name)
        if userSr:
            db.insertWhitelist(userSr["id"], name)
            if len(user) != 0:
                db.deleteBlack(name)
            await ctx.send("Will now follow {}".format(name))
            bests = speedrun.getBest(userSr)
            if bests:
                pb = speedrun.parsePB(bests, userSr["id"])
                for run in pb:
                    db.insertrun(run)
        else:
            await ctx.send("Speedrun.com has no {}".format(name))
    else:
        await ctx.send("Already following {}".format(name))

@bot.command(name='unfollow', help='/unfollow <name> will stop following that guy')
async def unfollow(ctx, name : str = ""):
    if not name:
        await ctx.send("You need to give a name")
        return
    user = db.getUser(name)
    if not user or len(user[0]) == 1:
        await ctx.send("I wasn't even following {}".format(name))
        return
    else:
        user = db.getUser(name)
        db.deleteWhite(user[0][0])
        db.insertBlacklist(user[0][1])
        runs = db.getUserruns(user[0][0])
        for run in runs:
            db.deleterun(run[0])
        await ctx.send("Will now forget {}".format(name))

@bot.command(name='shutdown', help='Closes bot')
async def closeBot(ctx):

    if ctx.message.author.id == OWNER:
        await ctx.send("Bye bye")
        await ctx.bot.logout()

    else:
        await ctx.send("I'm sorry {}. I'm afraid I can't do that. ".format(ctx.message.author.name))

bot.loop.create_task(backgroundUpdateTask())
bot.run(TOKEN)
