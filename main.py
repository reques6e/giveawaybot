import nextcord
import os
from nextcord.ext import commands

intents = nextcord.Intents.all()
bot = commands.Bot(command_prefix='$$$', intents=intents)
bot.remove_command('help')

for fn in os.listdir("./cogs"):
	if fn.endswith(".py"):
		bot.load_extension(f"cogs.{fn[:-3]}")

@bot.command()
async def load(ctx, extension):
	bot.load_extension(extension)
	await ctx.send("Подключил cogs")
	
bot.run('YourToken')
