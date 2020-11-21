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


def check_member(member):
    if member.nick:
        name = member.nick
    else:
        name = member.name
    name = name.replace(" ", "")
    if not db.getuser(name):
        user = speedrun.getuser(name)
        if user:
            db.insert_whitelist(user["id"], name)
            bests = speedrun.get_best(user)
            if bests:
                pb = speedrun.parse_pb(bests, user["id"])
                for run in pb:
                    db.insertrun(run)
        else:
            db.insert_blacklist(name)


async def background_update_task():
    await bot.wait_until_ready()
    await asyncio.sleep(3600)
    while not bot.is_closed():
        try:
            print("Background update")
            users = db.getallwhite()
            for user in users:
                update_member(user[1])
            print("update done")
            await asyncio.sleep(7200)
        except Exception as e:
            print(str(e))
            await asyncio.sleep(7200)


def update_member(name, shout=True):
    user = speedrun.getuser(name)
    bests = speedrun.get_best(user)
    if user and bests:
        pb = speedrun.parse_pb(bests, user["id"])
        old = db.getuserruns(user["id"])
        oldids = [x[0] for x in old]
        for run in pb:
            if run["runid"] not in oldids:
                for oldrun in old:
                    if oldrun[3] == run["game"] and oldrun[4] == run["category"]:
                        db.deleterun(oldrun[0])
                db.insertrun(run)
                if shout:
                    loop.create_task(announce_run(run))
            else:
                for oldrun in old:
                    if oldrun[0] == run["runid"] and oldrun[2] != run["place"]:
                        db.updaterun(run)
                        if shout:
                            loop.create_task(announce_change(run, oldrun[2] - run["place"]))
                        break


async def announce_run(run):
    channel = bot.get_channel(CHANNEL)
    name = db.getuserName(run["userid"])
    await channel.send('New run! {} is now rank {}/{} in {} {} with a time of {}\n<{}>'.format(name, run["place"], run["totalruns"], run["game"], run["category"], run["time"], run["link"]))


async def announce_change(run, change):
    channel = bot.get_channel(CHANNEL)
    name = db.getuserName(run["userid"])
    if change > 0:
        await channel.send('{} has risen to rank {}/{} in {} {}'.format(name, run["place"], run["totalruns"], run["game"], run["category"]))
    else:
        await channel.send('{} has dropped to rank {}/{} in {} {}'.format(name, run["place"], run["totalruns"], run["game"], run["category"]))


# client = discord.Client()
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
    db.create_tables()
    print("{}/{} members verified".format(count, users))
    for member in guild.members:
        check_member(member)
        count += 1
        if count % 10 == 0:
            print("{}/{} members verified".format(count, users))
            await asyncio.sleep(10)
    print("{}/{} members verified".format(count, users))


@bot.event
async def on_member_join(member):
    print("checking new member")
    check_member(member)


@bot.event
async def on_member_update(old, member):
    print("checking member update")
    if old.nick != member.nick:
        check_member(member)


@bot.command(name='update', help='Checks for new runs in speedrun.com')
async def check_updates(ctx):
    print("Run update")
    users = db.getallwhite()
    await ctx.send("Will now check for new runs")
    for user in users:
        update_member(user[1])
    print("update done")


@bot.command(name='drop_table', help='Drops all runs and fetches again. Will not shout')
async def renew_runs(ctx):
    if ctx.message.author.id == OWNER:
        print("Run update")
        users = db.getallwhite()
        db.drop_runs()
        db.create_tables()
        await ctx.send("Will reacquire runs")
        for user in users:
            update_member(user[1], False)
        print("update done")
    else:
        await ctx.send("You don't have rights for this function")


@bot.command(name='runlist', help='/runlist <name>: lists all runs that person has. No name will list all runs on server')
async def send_rankings(ctx, name: str = ""):
    if name:
        users = db.getuser(name)
    else:
        if ctx.message.author.id != OWNER:
            await ctx.send("Needs a name")
            return
        users = db.getallwhite()
        await ctx.send("This might take a while")
    if not users or len(users[0]) == 1:
        await ctx.send("I do not know this user. Try /follow <name> to add user to followed")
        return
    msg = ""
    for user in users:
        runs = db.getuserruns(user[0])
        if runs:
            msg = msg + "**{}**\n".format(user[1])
        for run in runs:
            # msg = msg + "> Rank {}/{}, ({}) on {} {}\n> WR {}\n".format(run[2], run[9], run[5], run[3], run[4], run[10])
            msg = msg + "> {} {}\n> \tRank {}/{}, ({})\n> \tWR {}\n".format(run[3], run[4], run[2], run[9], run[5], run[10])
            if len(msg) > 1700:
                await ctx.send(msg)
                msg = ""
    if msg != "":
        await ctx.send(msg)


@bot.command(name='follow', help='/follow <name> adds that name to be followed on speedrun.com')
async def follow(ctx, name: str = ""):
    if not name:
        await ctx.send("You need to give a name")
        return
    user = db.getuser(name)
    if not user or len(user[0]) == 1:
        user_sr = speedrun.getuser(name)
        if user_sr:
            db.insert_whitelist(user_sr["id"], name)
            if len(user) != 0:
                db.deleteblack(name)
            await ctx.send("Will now follow {}".format(name))
            bests = speedrun.get_best(user_sr)
            if bests:
                pb = speedrun.parse_pb(bests, user_sr["id"])
                for run in pb:
                    db.insertrun(run)
        else:
            await ctx.send("Speedrun.com has no {}".format(name))
    else:
        await ctx.send("Already following {}".format(name))


@bot.command(name='unfollow', help='/unfollow <name> will stop following that guy')
async def unfollow(ctx, name: str = ""):
    if not name:
        await ctx.send("You need to give a name")
        return
    user = db.getuser(name)
    if not user or len(user[0]) == 1:
        await ctx.send("I wasn't even following {}".format(name))
        return
    else:
        user = db.getuser(name)
        db.deletewhite(user[0][0])
        db.insert_blacklist(user[0][1])
        runs = db.getuserruns(user[0][0])
        for run in runs:
            db.deleterun(run[0])
        await ctx.send("Will now forget {}".format(name))


@bot.command(name='shutdown', help='Closes bot')
async def close_bot(ctx):

    if ctx.message.author.id == OWNER:
        await ctx.send("Bye bye")
        await ctx.bot.logout()

    else:
        await ctx.send("I'm sorry {}. I'm afraid I can't do that. ".format(ctx.message.author.name))

bot.loop.create_task(background_update_task())
bot.run(TOKEN)
