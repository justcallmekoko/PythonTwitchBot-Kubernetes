import os
import random
from dotenv import load_dotenv
from datetime import datetime
from twitchio.ext import commands
from ast import literal_eval as make_tuple

global admin_user
global giveaway_title
global giveaway_running
global giveaway_participants

load_dotenv()
ADMIN_USER = str(os.getenv('ADMIN_USER'))
TWITCH_TOKEN = os.getenv('TWITCH_TOKEN')
API_TOKEN = os.getenv('API_TOKEN')
CLIENT_ID = os.getenv('CLIENT_ID')
NICK = str(os.getenv('NICK'))
PREFIX = str(os.getenv('PREFIX'))
INITIAL_CHANNELS = str(os.getenv('INITIAL_CHANNELS'))

print('Going to join channel: ' + INITIAL_CHANNELS)

nick = str(NICK)
admin_user = ADMIN_USER
giveaway_title = ''
giveaway_running = False
giveaway_participants = []

random.seed(datetime.now())

bot = commands.Bot(
	irc_token=TWITCH_TOKEN,
	api_token=API_TOKEN,
	client_id=CLIENT_ID,
	nick=nick,
	prefix=PREFIX,
	initial_channels=[INITIAL_CHANNELS]
)

# Aux functions
async def get_user_id(username):
	user_tuple = await bot.get_users(str(username))

	try:
		(id, login, display, type, broadcast_type, desc, views, created, offline_img, profile_img, email) = user_tuple[0]

		return str(id)
	except:
		return None

async def check_following(from_id, to_id):
	if await bot.get_follow(from_id, to_id) != None:
		return True
	else:
		return False

# Register an event with the bot
@bot.event
async def event_ready():
	print(f'Ready | {bot.nick}')

@bot.event
async def event_webhook(webhook):
	print('Webhook event')

@bot.event
async def event_join(user):
	print('User joined: ' + str(user.name))

@bot.event
async def event_message(message):
	print(str(message.author.name) + ': ' + (message.content))

	# If you override event_message you will need to handle_commands for commands to work.
	await bot.handle_commands(message)


# Register a command with the bot
@bot.command(name='test', aliases=['t'])
async def test_command(ctx):
	await ctx.send(f'Hello {ctx.author.name}')

@bot.command(name='help', aliases=['h'])
async def help_command(ctx):
	await ctx.send(f'{ctx.author.name} Get a full list of commands at https://github.com/justcallmekoko/TwitchMCU')

@bot.command(name='discord', aliases=['d'])
async def discord_command(ctx):
	await ctx.send(f'{ctx.author.name} Come be a part of the community on discord https://discord.gg/invite/M2YWpfjAvM')

@bot.command(name='socials', aliases=['s'])
async def socials_command(ctx):
	await ctx.send(f'YouTube: https://www.youtube.com/justcallmekoko')
	await ctx.send(f'Instagram: https://www.instagram.com/just.call.me.koko')
	await ctx.send(f'Twitter: https://twitter.com/jcmkyoutube')

@bot.command(name='giveaway', aliases=['g'])
async def giveaway_command(ctx):
	global giveaway_running
	global giveaway_title
	global giveaway_participants

	if not giveaway_running:
		await ctx.send(f'{ctx.author.name} There are no give aways currently running.')
	else:
		await ctx.send(f'{ctx.author.name} "{giveaway_title}" is currently running with {str(len(giveaway_participants))} participant(s). Use "!tk" to join')

@bot.command(name='ticket', aliases=['tk'])
async def ticket_command(ctx):
	global admin_user
	global giveaway_running
	global giveaway_title
	global giveaway_participants

	if not giveaway_running:
		await ctx.send(f'{ctx.author.name} There are no give aways currently running.')
	else:
		id = await get_user_id(f'{ctx.author.name}')

		# Check if user is following the admin
		if not await check_following(await get_user_id(str(ctx.author.name)), await get_user_id(str(admin_user))):
			await ctx.send(f'{ctx.author.name} You need to follow {admin_user} to participate')
			return

		if [str(id), str(ctx.author.name)] in giveaway_participants:
			await ctx.send(f'{ctx.author.name} You are already on the list')
			return

		giveaway_participants.append([str(id), str(ctx.author.name)])

		await ctx.send(f'{ctx.author.name} Welcome to the give away "{giveaway_title}"')

# Admin commands
@bot.command(name='startgiveaway', aliases=['sg'])
async def start_giveaway_command(ctx):
	global admin_user
	global giveaway_running
	global giveaway_title
	global giveaway_participants
	# Check if command is run by admin
	if admin_user != str(ctx.author.name):
		await ctx.send(f'{ctx.author.name} This command is for admins')
		return
	else:
		try:
			command = str(ctx.message.content).split(' ')[0]
			title = str(ctx.message.content).replace(command, '')
		except Exception as e:
			print(e)
			return

		giveaway_running = True
		giveaway_title = title
		giveaway_participants.clear()
		print('Participant list size: ' + str(len(giveaway_participants)))
		await ctx.send(f'Give away started! "{title}". Use "!tk" to join')

@bot.command(name='stopgiveaway', aliases=['spg'])
async def stop_giveaway_command(ctx):
	global admin_user
	global giveaway_running
	global giveaway_title
	global giveaway_participants
	# Check if command is run by admin
	if admin_user != str(ctx.author.name):
		await ctx.send(f'{ctx.author.name} This command is for admins')
		return
	elif not giveaway_running:
		await ctx.send(f'{ctx.author.name} There are no give aways currently running.')
		return
	else:
		giveaway_running = False
		giveaway_participants.clear()
		print('Participant list size: ' + str(len(giveaway_participants)))
		await ctx.send(f'Give away stopped! "{giveaway_title}"')
		giveaway_title = ''

@bot.command(name='pickwinner', aliases=['pw'])
async def pick_winner_command(ctx):
	global admin_user
	global giveaway_running
	global giveaway_title
	global giveaway_participants
	# Check if command is run by admin
	if admin_user != str(ctx.author.name):
		await ctx.send(f'{ctx.author.name} This command is for admins')
		return
	else:
		picked = False

		while not picked:
			if giveaway_running and (len(giveaway_participants) > 0):
				winner = random.choice(giveaway_participants)
				if not await check_following(str(winner[0]), await get_user_id(str(admin_user))):
					giveaway_participants.remove(winner)
				else:
					picked = True
					await ctx.send(f'The winner of "{giveaway_title}" is {str(winner[1])}')
					break
			elif len(giveaway_participants) <= 0:
				await ctx.send(f'{ctx.author.name} There are no participants')
				return
			else:
				await ctx.send(f'{ctx.author.name} There are no give aways currently running.')
				return

# Backend commands
@bot.command(name='checkfollow', aliases=['cf'])
async def check_follow_command(ctx):
	try:
		command, arg = str(ctx.message.content).split(' ')
	except Exception as e:
		print(e)
		return

	from_id = await get_user_id(str(arg))

	to_id = await get_user_id(f'{ctx.author.name}')

	if await bot.get_follow(from_id, to_id) != None:
		print(str(arg) + ' is following ' + str(f'{ctx.author.name}'))

@bot.command(name='getuser', aliases=['gu'])
async def get_user_command(ctx):
	try:
		command, arg = str(ctx.message.content).split(' ')
	except Exception as e:
		print(e)
		return

	id = await get_user_id(str(arg))

	print(str(arg) + ': ' + str(id))

bot.run()
