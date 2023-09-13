import datetime, time, discord, json, requests, sys
from discord.ext import commands, tasks
from discord import app_commands
from discord.errors import Forbidden
from datetime import datetime, timezone, timedelta, date
from html2image import Html2Image
from PIL import Image
from typing import Union


def get_emoji_name(readable_name: str):
	return readable_name.replace(" ", "_").lower()


def get_readable_name(emoji_name: str):
	return emoji_name.replace("_", " ").title()


# Voting

# A-Z emote choices (6 choices = A, B, C, D, E, F)
# Reaction voting
# /vote duration type (sotw/botw, maybe) choices (should be enum) WoM_duration
# Auto update vote message to show timestamp
# Start WoM

# WoM (Wise Old Man)

# Announce the winning vote and begin the challenge
# Auto update message to show top 3
# Announce winners at the end of the duration and show top 5
# Auto assign role?


with open("token.txt", 'r') as r:
	token = r.read()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
client = commands.Bot(command_prefix='!', case_insensitive=True, intents=intents)

CHANNEL_ID = 978493716564160563
GUILD_ID = "978464595935105055"
BOT_MEMBER_ID = 1051655294675058688
EVENTS_ROLE_ID = 1031010206693470290
KEY_ADMIN_ID = 978754310466850877

DB_FILE_PATH = "OSRS_DATABASE.json"
REACTION_HISTORY_FILE_PATH = "MESSAGE_HISTORY.json"

# skill_emoji_map = {'agility': '<:agility:1051874138878394448>', 'attack': '<:attack:1051874139792752660>', 'construction': '<:construction:1051874141193637918>', 'cooking': '<:cooking:1051874142200283187>', 'crafting': '<:crafting:1051874143328542780>', 'defence': '<:defence:1051874144234516530>', 'farming': '<:farming:1051874145643806770>', 'firemaking': '<:firemaking:1051874146629464115>', 'fishing': '<:fishing:1051874147711586414>', 'fletching': '<:fletching:1051874148487544832>', 'herblore': '<:herblore:1051874148886007840>', 'hitpoints': '<:hitpoints:1051874150182043669>', 'hunter': '<:hunter:1051874151767486505>', 'magic': '<:magic:1051874152849621153>', 'mining': '<:mining:1051874153969504329>', 'overall': '<:overall:1051874154934194206>', 'prayer': '<:prayer:1051874155898884136>', 'ranged': '<:ranged:1051874156733538324>', 'runecrafting': '<:runecrafting:1051874157744369795>', 'slayer': '<:slayer:1051874159057190982>', 'smithing': '<:smithing:1051874160030261248>', 'strength': '<:strength:1051874160835567666>', 'thieving': '<:thieving:1051874162131619930>', 'woodcutting': '<:woodcutting:1051874163532513290>'}
# boss_emoji_map = {'barrows_chests': '<:barrows_chests:1070119709539848232>', 'callisto': '<:callisto:1070119710701658232>', 'chambers_of_xeric': '<:chambers_of_xeric:1070119711897026580>', 'commander_zilyana': '<:commander_zilyana:1070119713625100388>', 'dagannoth_prime': '<:dagannoth_prime:1070119714547839097>', 'dagannoth_rex': '<:dagannoth_rex:1070119716187820194>', 'dagannoth_supreme': '<:dagannoth_supreme:1070119720747028521>', 'general_graardor': '<:general_graardor:1070119722525409342>', 'giant_mole': '<:giant_mole:1070119724433809458>', 'king_black_dragon': '<:king_black_dragon:1070119725474005032>', 'kraken': '<:kraken:1070119726837141564>', 'kreearra': '<:kreearra:1070119728422600805>', 'kril_tsutsaroth': '<:kril_tsutsaroth:1070119730259705896>', 'phantom_muspah': "<:phantom_muspah:1071849378681208984>", 'sarachnis': '<:sarachnis:1070119731236966401>', 'tempoross': '<:tempoross:1070119733136994404>', 'theatre_of_blood': '<:theatre_of_blood:1070119734412066937>', 'the_corrupted_gauntlet': '<:the_corrupted_gauntlet:1070119735435460638>', 'tombs_of_amascut': '<:tombs_of_amascut:1070119736861536286>', 'tztok_jad': '<:tztok_jad:1070119738111438928>', 'venenatis': '<:venenatis:1070119739193561199>', 'vetion': '<:vetion:1070119740623831110>', 'zulrah': "<:zulrah:1070119745594073110>"}

skill_emoji_map = {}
boss_emoji_map = {}

# Gets all skill/boss choices that the bot displays
all_skills = ['overall', 'attack', 'defence', 'strength', 'hitpoints', 'ranged', 'prayer', 'magic', 'cooking', 'woodcutting', 'fletching', 'fishing', 'firemaking', 'crafting', 'smithing', 'mining', 'herblore', 'agility', 'thieving', 'slayer', 'farming', 'runecrafting', 'hunter', 'construction']
#skill_select_choices = [discord.SelectOption(label=get_readable_name(skill), value=get_readable_name(skill), description=f"The skill of {get_readable_name(skill)}", emoji=skill_emoji_map[get_emoji_name(skill)]) for skill in all_skills]

curated_bosses = ['nightmare', 'tztok_jad', 'dagannoth_prime', 'dagannoth_rex', 'dagannoth_supreme', 'kraken', 'callisto', 'venenatis', 'vetion', 'sarachnis', 'chambers_of_xeric', 'commander_zilyana', 'general_graardor', 'barrows_chests', 'the_corrupted_gauntlet', 'tombs_of_amascut', 'theatre_of_blood', 'king_black_dragon', 'giant_mole', 'kril_tsutsaroth', 'kreearra', 'phantom_muspah', "zulrah"]
print(len(curated_bosses))
#curated_boss_select_choices = [discord.SelectOption(label=get_readable_name(boss), value=get_readable_name(boss), description=f"The boss {get_readable_name(boss)}", emoji=boss_emoji_map[get_emoji_name(boss)]) for boss in curated_bosses]


def get_emoji(guild: discord.Guild, emoji_str: str) -> Union[discord.Emoji, None]:
	for emoji in guild.emojis:
		if emoji.name.lower() == emoji_str.lower():
			return emoji

	return None


def runescapeify_text(quantity: int):
	"""
	:param quantity: 1912401923
	:return: 1.9m
	"""
	if quantity > 1e6:
		quantity = f"{str(round(quantity / 1e6, 2))}m"

	elif quantity > 1000:
		quantity = f"{str(round(quantity / 1000, 2))}k"

	return quantity


def get_total_gained(wom_comp_id: str) -> int:
	"""
	Gets the total gained xp/kc of the competition

	:param wom_comp_id: The wom competition ID
	:return: total_amount_gained
	"""
	while True:
		try:
			total_gained = 0
			url = f"https://api.wiseoldman.net/v2/competitions/{wom_comp_id}"

			r = requests.session()
			page = r.get(url)
			for player in page.json()['participations']:
				total_gained += player['progress']['gained']

			return total_gained
		except Exception as e:
			print(page.text)
			print(e, "ERROR GETTING TOTAL GAINED")


def get_top_players(wom_comp_id: str):
	"""
	Gets the top 5 players, if the sum of the values are >= 0: show players & chart

	:param wom_comp_id: The wom competition ID
	:return: {player: gained,}
	"""
	try:
		r = requests.session()
		top_five = {}
		url = f"https://api.wiseoldman.net/v2/competitions/{wom_comp_id}/top-history"

		page = r.get(url)
		if not page.ok:
			print(page.json())
		for i in page.json():
			if i.get("history", None) is not None and i.get("history", None) != []:
				top_five[i['player']['displayName']] = {"gained": i['history'][0]['value'] - i['history'][-1]['value']}

		return top_five
	except Exception as e:
		return None


def get_top_chart(comp_id: str):
	hti = Html2Image(browser_executable=r"C:\Program Files\Google\Chrome\Application\chrome.exe",custom_flags=['--virtual-time-budget=10000', '--hide-scrollbars'])
	hti.screenshot(url=f'https://wiseoldman.net/competitions/{comp_id}/chart', save_as='WoM_Chart123.png')

	im = Image.open(r"WoM_Chart123.png")

	# Setting the points for cropped image
	left = 733
	top = 467
	right = 1457
	bottom = 845

	# Cropped image of above dimension
	# (It will not change original image)
	im1 = im.crop((left, top, right, bottom))

	# Shows the image in image viewer
	im1.save("WoM_chart.png")
	return "WoM_chart.png"


async def get_reaction_count(message_id: str, poll_index: int) -> dict:
	"""
	:param message_id: MESSAGE
	:return: dict of count: {"A": 0, "B": "5", ...}
	"""
	with open(DB_FILE_PATH, 'r', encoding="utf-8") as r:
		db = json.loads(r.read())
	channel = await client.fetch_channel(CHANNEL_ID)
	message = await channel.fetch_message(int(message_id))
	reactions = message.reactions
	all_reactions = {}

	if reactions is not None:
		for reaction in reactions:
			if str(reaction.emoji) in list(db[GUILD_ID]['poll'][poll_index]["poll_choices"].values()):
				if reaction.emoji not in all_reactions.keys():
					all_reactions[reaction.emoji] = reaction.count - 1
				else:
					all_reactions[reaction.emoji] += 1
			else:
				print("NOT ADDING", reaction.emoji)

	return all_reactions if all_reactions != {} else {item: 0 for item in db[GUILD_ID]['poll'][poll_index]['poll_choices'].keys()}


def start_wom_challenge(
		challenge: str,
		poll_index: int
) -> str:
	"""
	Starts Challenge with details from DB
	:return: Link to WoM Challenge
	"""
	with open(DB_FILE_PATH, 'r', encoding="utf-8") as r:
		db = json.loads(r.read())

	r = requests.session()

	def convert_unix_to_tz(unix_timestamp: int, offset: int = 0):
		unix_timestamp += offset
		tz = timezone(timedelta(hours=0))
		return datetime.fromtimestamp(unix_timestamp, tz).isoformat()

	url = f"https://api.wiseoldman.net/v2/competitions"

	headers = {
		"Content-type": "application/json"
	}

	print(db[GUILD_ID]['poll'][poll_index]['wom_start_time'])
	payload = {
		"title": db[GUILD_ID]['poll'][poll_index]['poll_title'].strip(" Poll").strip("Iron Drip "),
		"metric": challenge,
		"startsAt": convert_unix_to_tz(db[GUILD_ID]['poll'][poll_index]['wom_start_time']),
		"endsAt": convert_unix_to_tz(db[GUILD_ID]['poll'][poll_index]['wom_start_time'], offset=60 * 60 * 24 * 7),  # 7 days
		"groupId": 2919,
		"groupVerificationCode": "160-283-217"
	}
	page = r.post(url, headers=headers, json=payload)
	print(page.status_code, page.content)

	if page.ok:
		return page.json()['competition']['id']

	else:
		return "Bot failed to get WoM ID"


async def send_result_poll(poll_index: int):
	with open(DB_FILE_PATH, 'r', encoding="utf-8") as r:
		db = json.loads(r.read())

	poll_message_id = db[GUILD_ID]['poll'][poll_index].get("poll_message_id", None)
	poll_reaction_count = await get_reaction_count(poll_message_id, poll_index)
	winning_emoji = sorted(poll_reaction_count, key=lambda x: poll_reaction_count[x], reverse=True)[0]  # Sorts the reactions by most and gets first
	winning_emoji_votes = poll_reaction_count[winning_emoji]
	channel = await client.fetch_channel(CHANNEL_ID)
	message = await channel.fetch_message(poll_message_id)
	current_time = (datetime.now(timezone.utc).timestamp())
	total_votes = sum(list(poll_reaction_count.values()))

	if db[GUILD_ID]['poll'][poll_index]['poll_end_time'] <= current_time and db[GUILD_ID]['poll'][poll_index][
		'active'] is True:
		print("ENDING POLL")
		# Edit poll message to show past tense
		embed = discord.Embed(
			title=db[GUILD_ID]['poll'][poll_index]['poll_title'],
			description=db[GUILD_ID]['poll'][poll_index]['poll_description'],
			color=15548997  # Red
		)
		nl = "\n"
		embed.add_field(name="Choices:", value=nl.join(f"{v} {i}" for i, v in db[GUILD_ID]['poll'][poll_index]['poll_choices'].items()), inline=False)
		embed.add_field(name="Results:", value=f"{nl.join(f'{i} {v} | `{round(v / total_votes * 100, 1)}%`' for i, v in poll_reaction_count.items())}\nTotal votes: {total_votes}", inline=False)  # Get reactions of each letter
		embed.add_field(name=f"{db[GUILD_ID]['poll'][poll_index]['poll_title'].strip('Iron Drip ')} Winner:", value=f"{winning_emoji} {str(winning_emoji.name).title()} {winning_emoji_votes}/{total_votes} ({round(winning_emoji_votes / total_votes * 100, 1)}%)", inline=False)
		embed.add_field(name="Terms:", value=f"⏰ Poll ended at: <t:{db[GUILD_ID]['poll'][poll_index]['poll_end_time']}>\n⏰ WoM Starts at: <t:{db[GUILD_ID]['poll'][poll_index]['wom_start_time']}:R>", inline=False)
		embed.timestamp = datetime.now()
		embed.set_footer(text="Updated at:")
		await message.edit(embed=embed)

		# Set poll to inactive
		db[GUILD_ID]['poll'][poll_index]['active'] = False

		# Start WoM Event (Actual start time happens at wom_start_time, this just creates the event)
		new_wom_id = start_wom_challenge(winning_emoji.name, poll_index)

		# Adds wom to DB for updating wom embed (live leaderboard)
		db[GUILD_ID]['poll'][poll_index]['wom']['wom_title'] = db[GUILD_ID]['poll'][poll_index]['poll_title'].strip(' Poll')
		db[GUILD_ID]['poll'][poll_index]['wom']['wom_message_id'] = None  # Inaccessible til the WoM webhook is sent in send_wom_webhook
		db[GUILD_ID]['poll'][poll_index]['wom']['wom_start_time'] = db[GUILD_ID]['poll'][poll_index]['wom_start_time']
		db[GUILD_ID]['poll'][poll_index]['wom']['wom_end_time'] = db[GUILD_ID]['poll'][poll_index]['wom_start_time'] + (60 * 60 * 24 * 7)
		db[GUILD_ID]['poll'][poll_index]['wom']['wom_id'] = new_wom_id
		db[GUILD_ID]['poll'][poll_index]['wom']['winning_emoji'] = str(winning_emoji)
		db[GUILD_ID]['poll'][poll_index]['wom']['active'] = False
		db[GUILD_ID]['poll'][poll_index]['wom_started'] = True

	with open(DB_FILE_PATH, 'w', encoding="utf-8") as r:
		r.write(json.dumps(db, indent=4, ensure_ascii=False))


async def send_wom_webhook(
		poll_index: int,
		mention: bool = True
):
	with open(DB_FILE_PATH, 'r', encoding="utf-8") as r:
		db = json.loads(r.read())

	poll_message_id = db[GUILD_ID]['poll'][poll_index].get("poll_message_id", None)
	poll_reaction_count = await get_reaction_count(poll_message_id, poll_index)
	winning_emoji = db[GUILD_ID]['poll'][poll_index]['wom']['winning_emoji']  # Sorts the reactions by most and gets first (if tie gets lexicographically)
	current_time = (datetime.now(timezone.utc).timestamp())

	if db[GUILD_ID]['poll'][poll_index]['wom_start_time'] <= current_time:  # Fail safe
		print("Sending WOM WEBHOOK (ALREADY STARTED)")

		wom_title = db[GUILD_ID]['poll'][poll_index]['wom']['wom_title']
		embed = discord.Embed(
			title=db[GUILD_ID]['poll'][poll_index]['wom']['wom_title'],
			description=f"{winning_emoji} {str(winning_emoji).title()}\nThe competition has begun!",
			color=5763719
		)
		embed.add_field(name="Wise Old Man:", value=f"[{wom_title}](https://wiseoldman.net/competitions/{db[GUILD_ID]['poll'][poll_index]['wom']['wom_id']}/participants)", inline=False)
		embed.set_image(url=f"attachment://{get_top_chart(db[GUILD_ID]['poll'][poll_index]['wom']['wom_id'])}")  # Get reactions of each letter
		embed.timestamp = datetime.now()
		embed.set_footer(text="Updated:")

		channel = await client.fetch_channel(CHANNEL_ID)
		wom_msg = await channel.send(embed=embed)
		if mention:
			await channel.send(f"<@&{EVENTS_ROLE_ID}> {wom_title} has begun!")

		# TODO: not adding to DB?
		print(int(wom_msg.id))
		db[GUILD_ID]['poll'][poll_index]['wom']['wom_message_id'] = int(wom_msg.id)  # Add message_id for editting

	print("Updating wom message ID", wom_msg)

	with open(DB_FILE_PATH, 'w', encoding="utf-8") as r:
		r.write(json.dumps(db, indent=4, ensure_ascii=False))


def update_competition(comp_id: str) -> bool:
	url = f"https://api.wiseoldman.net/v2/competitions/{comp_id}/update-all"
	data = {
		"verificationCode": "160-283-217"
	}
	headers = {
		"Content-type": "application/json",
		"user-agent": "Jacobfinn123#3076",
		"x-api-key": "cldszhsbk000908l5fcaa8c3q"
	}
	page = requests.post(url, data, headers=headers)

	if page.ok:
		return True
	else:
		return False


@tasks.loop(seconds=60)
async def update_wom():
	# TODO: STOP TASK ONCE WOM FINISHED

	with open(DB_FILE_PATH, 'r', encoding="utf-8") as r:
		db = json.loads(r.read())

	for index, poll in enumerate(db[GUILD_ID]['poll']):
		current_time = (datetime.now(timezone.utc).timestamp())
		if db[GUILD_ID]['poll'][index]['wom'] != {}:
			if db[GUILD_ID]['poll'][index]['wom']['active'] is True:

				# Check if the WoM is ended or about to start
				if db[GUILD_ID]['poll'][index]['wom']['wom_end_time'] <= current_time:
					print("Concluding/Starting WoM event!")
					started_new_wom = False
					# Update Active WoM webhook to show past tense and alert winner.
					wom_id = db[GUILD_ID]['poll'][index]['wom']['wom_id']
					wom_msg_id = db[GUILD_ID]['poll'][index]['wom']["wom_message_id"]
					channel = await client.fetch_channel(CHANNEL_ID)
					message = await channel.fetch_message(wom_msg_id)
					top_five_players = get_top_players(wom_id)
					if top_five_players is None:
						continue
					wom_sum = sum(x['gained'] for x in top_five_players.values()) > 0  # Checks if there is any data to start showing image
					wom_title = db[GUILD_ID]['poll'][index]['wom']['wom_title']

					embed = discord.Embed(
						title=wom_title,
						description=f"{db[GUILD_ID]['poll'][index]['wom']['winning_emoji']} **{get_readable_name(db[GUILD_ID]['poll'][index]['wom']['winning_emoji'].split(':')[1])}** {db[GUILD_ID]['poll'][index]['wom']['winning_emoji']}\n\n**The competition has ended!**\n",
						color=15548997  # Red
					)
					embed.add_field(name="Wise Old Man:", value=f"[{wom_title}](https://wiseoldman.net/competitions/{db[GUILD_ID]['poll'][index]['wom']['wom_id']}/participants)", inline=False)  # Get reactions of each letter
					embed.timestamp = datetime.now()
					embed.set_footer(text="Updated:")

					# Only add file if top 5
					if wom_sum:
						guild = client.get_guild(int(GUILD_ID))

						for user in top_five_players:
							for member in guild.members:
								if member.name.lower() == user.lower():
									break
								elif member.nick is not None:
									if member.nick.lower() == user.lower():
										break
							else:
								member = None

							if member is not None:
								top_five_players[user]['discord_id'] = f"<@{member.id}>"
							else:
								print("UNABLE TO FIND IN DISCORD: ", member, user)
								top_five_players[user]['discord_id'] = f"@{user}"

						if "SOTW" in db[GUILD_ID]['poll'][index]['wom']['wom_title']:
							gained_type = "xp"
							assign_role = discord.utils.get(guild.roles, name="SOTW Winner")
						elif "BOTW" in db[GUILD_ID]['poll'][index]['wom']['wom_title']:
							gained_type = "kc"
							assign_role = discord.utils.get(guild.roles, name="BOTW Winner")

						emoji_medals = [":first_place:", ":second_place:", ":third_place:", ":medal:", ":medal:"]

						chart = get_top_chart(wom_id)
						nl = "\n"
						embed.add_field(name=f"Top 5:", value=f"{nl.join(f'{emoji} {top_five_players[player][list(top_five_players[player].keys())[1]]} `+{runescapeify_text(top_five_players[player][list(top_five_players[player].keys())[0]])} {gained_type}`' for emoji, player in zip(emoji_medals, top_five_players))}")

						embed.add_field(name=f":chart_with_upwards_trend: Total Gained:", value=f"`+{runescapeify_text(get_total_gained(wom_comp_id=wom_id))} {gained_type}`", inline=False)
						embed.add_field(name=f"⏰ Event Ended:", value=f"<t:{db[GUILD_ID]['poll'][index]['wom']['wom_end_time']}:R>", inline=False)
						embed.add_field(name=f":first_place: Winner:", value=f"{top_five_players[list(top_five_players.keys())[0]]['discord_id']}", inline=False)
						embed.set_image(url=f"attachment://{chart}")  # Get reactions of each letter
						file = discord.File(rf"C:\Users\Administrator\Desktop\{chart}")
						await message.edit(attachments=[file], embed=embed)

						# Assign the BOTW/SOTW Winner Role
						try:
							print(int(top_five_players[list(top_five_players.keys())[0]]['discord_id'].replace("@", "").replace("<", "").replace(">", "")))
							member = discord.utils.get(client.get_all_members(), id=int(top_five_players[list(top_five_players.keys())[0]]['discord_id'].replace("@", "").replace("<", "").replace(">", "")))
							if member is not None:
								await member.add_roles(assign_role)
							else:
								print("Can't assign roles to member, please do manually. (Unable to find member)")
						except ValueError:
							print("Can't assign roles to member, please do manually. (Unable to find member)")

						# Update activeness to False
						db[GUILD_ID]['poll'][index]['wom']['active'] = False

					# Post WoM starting webhook if another WoM starting soon (if within 6 hours)
					for wom_index, wom_poll in enumerate(db[GUILD_ID]['poll']):
						if db[GUILD_ID]['poll'][index]['wom'] != {}:
							if db[GUILD_ID]['poll'][index]['wom']['active'] is False:
								if db[GUILD_ID]['poll'][wom_index]['wom']['wom_start_time'] >= (datetime.now(timezone.utc) - timedelta(hours=6)).timestamp():  # Gets 6 hours ago
									print("Sending initial poll:", db[GUILD_ID]['poll'][wom_index]['wom']['wom_title'])
									# Post webhook of starting WoM
									new_wom_title = db[GUILD_ID]['poll'][wom_index]['wom']['wom_title']
									await send_wom_webhook(wom_index, False)
									started_new_wom = True

									db[GUILD_ID]['poll'][wom_index]['wom']['active'] = True

					if not started_new_wom:
						await channel.send(f"<@&{EVENTS_ROLE_ID}>\n\n {emoji_medals[0]} {top_five_players[list(top_five_players.keys())[0]]['discord_id']} Congratz on winning {wom_title}! Speak to any <@&{KEY_ADMIN_ID}> to claim your reward.")
						print("Not starrt")
					else:
						await channel.send(f"<@&{EVENTS_ROLE_ID}>\n\n {emoji_medals[0]} {top_five_players[list(top_five_players.keys())[0]]['discord_id']} Congratz on winning {wom_title}! Speak to any <@&{KEY_ADMIN_ID}> to claim your reward.\n\n{new_wom_title} has begun!")
						print("HERERE")

					# Update DB Entry
					with open(DB_FILE_PATH, 'w', encoding="utf-8") as r:
						r.write(json.dumps(db, indent=4, ensure_ascii=False))
#
					continue

				# In the last 15 minutes; send an update all batch
				elif datetime.now(timezone.utc).timestamp() < db[GUILD_ID]['poll'][index]['wom']['wom_end_time'] <= (datetime.now(timezone.utc) + timedelta(minutes=15)).timestamp():
					print("Updating competition")
					update_competition(db[GUILD_ID]['poll'][index]['wom']['wom_id'])

				wom_id = db[GUILD_ID]['poll'][index]['wom']['wom_id']
				wom_msg_id = db[GUILD_ID]['poll'][index]['wom']["wom_message_id"]
				channel = await client.fetch_channel(CHANNEL_ID)
				message = await channel.fetch_message(wom_msg_id)
				top_five_players = get_top_players(wom_id)
				if top_five_players is None:
					continue
				wom_sum = sum(x['gained'] for x in top_five_players.values()) > 0  # Checks if there is any data to start showing image

				embed = discord.Embed(
					title=db[GUILD_ID]['poll'][index]['wom']['wom_title'].strip(' Poll'),
					description=f"{db[GUILD_ID]['poll'][index]['wom']['winning_emoji']} **{db[GUILD_ID]['poll'][index]['wom']['winning_emoji'].split(':')[1].split(':')[0].title()}** {db[GUILD_ID]['poll'][index]['wom']['winning_emoji']}\n\n**The competition has begun!**\n",
					color=5763719
				)
				embed.add_field(name="Wise Old Man:", value=f"[{db[GUILD_ID]['poll'][index]['wom']['wom_title'].strip(' Poll')}](https://wiseoldman.net/competitions/{db[GUILD_ID]['poll'][index]['wom']['wom_id']}/participants)", inline=False)  # Get reactions of each letter
				embed.timestamp = datetime.now()
				embed.set_footer(text="Updated:")

				# Only add file if top 5
				if wom_sum:
					guild = client.get_guild(int(GUILD_ID))

					for user in top_five_players:
						for member in guild.members:
							if member.name.lower() == user.lower():
								break
							elif member.nick is not None:
								if member.nick.lower() == user.lower():
									break
						else:
							member = None

						if member is not None:
							top_five_players[user]['discord_id'] = f"<@{member.id}>"
						else:
							print("UNABLE TO FIND IN DISCORD: ", member, user)
							top_five_players[user]['discord_id'] = f"@{user}"

					if "SOTW" in db[GUILD_ID]['poll'][index]['wom']['wom_title']:
						gained_type = "xp"
					elif "BOTW" in db[GUILD_ID]['poll'][index]['wom']['wom_title']:
						gained_type = "kc"

					emoji_medals = [":first_place:", ":second_place:", ":third_place:", ":medal:", ":medal:"]

					chart = get_top_chart(wom_id)
					nl = "\n"
					embed.add_field(name=f"Top 5:", value=f"{nl.join(f'{emoji} {top_five_players[player][list(top_five_players[player].keys())[1]]} `+{runescapeify_text(top_five_players[player][list(top_five_players[player].keys())[0]])} {gained_type}`' for emoji, player in zip(emoji_medals, top_five_players))}")

					embed.add_field(name=f":chart_with_upwards_trend: Total Gained:", value=f"`+{runescapeify_text(get_total_gained(wom_comp_id=wom_id))} {gained_type}`", inline=False)
					embed.add_field(name=f"⏰ Event Ends:", value=f"<t:{db[GUILD_ID]['poll'][index]['wom']['wom_end_time']}:R>", inline=False)
					embed.set_image(url=f"attachment://{chart}")  # Get reactions of each letter
					file = discord.File(rf"C:\Users\Administrator\Desktop\{chart}")
					await message.edit(attachments=[file], embed=embed)

				else:
					await message.edit(embed=embed)


@tasks.loop(seconds=15)
async def update_poll():
	try:
		with open(DB_FILE_PATH, 'r', encoding="utf-8") as r:
			db = json.loads(r.read())

		# Check if current_time >= wom_start_time
		current_time = (datetime.now(timezone.utc).timestamp())

		if db[GUILD_ID]['poll'] != []:

			for index, poll in enumerate(db[GUILD_ID]['poll']):
				if poll['active'] is False:  # FAIL SAFE, SHOULD NEVER HAPPEN
					if poll['wom_start_time'] <= current_time and poll['wom_started'] is False:
						# Start WoM Poll Send webhook with link and conclusion
						print("Stopping update_poll task, starting WOM")
						await send_wom_webhook(index)
						update_poll.stop()

					continue

				elif poll['poll_end_time'] <= current_time:
					print("ENDING POLL")
					# Ends the poll, updates the webhook red and shows winner and sets to inactive
					await send_result_poll(index)
					return

				poll_msg_id = poll["poll_message_id"]

				channel = await client.fetch_channel(CHANNEL_ID)
				message = await channel.fetch_message(poll_msg_id)

				embed = discord.Embed(
					title=poll['poll_title'],
					description=poll['poll_description'],
					color=5763719
				)
				nl = "\n"
				embed.add_field(name="Choices:", value=nl.join(f"{v} {i}" for i, v in poll['poll_choices'].items()), inline=False)
				votes = await get_reaction_count(poll_msg_id, index)
				embed.add_field(name="Results:", value=f"{nl.join(f'{i} {v}' for i, v in votes.items())}\nTotal votes: {sum(list(votes.values()))}", inline=False)  # Get reactions of each letter
				embed.add_field(name="Terms:", value=f"⏰ Poll ends: <t:{poll['poll_end_time']}:R>\n⏰ WoM Starts: <t:{poll['wom_start_time']}:R>\n🤓 One vote allowed!", inline=False)
				embed.timestamp = datetime.now()
				embed.set_footer(text="Updated at:")
				new_message_id = await message.edit(embed=embed)

				poll["poll_message_id"] = int(new_message_id.id)

		# Update DB Entry
		with open(DB_FILE_PATH, 'w', encoding="utf-8") as r:
			r.write(json.dumps(db, indent=4, ensure_ascii=False))

	except Exception as e:
		print("EXCEPTION IN UPDATE_POLL", e)
		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		print(exc_type, fname, exc_tb.tb_lineno)


class Dropdown(discord.ui.Select):
	def __init__(
			self,
			poll_duration: str,
			event_type: str,
			poll_title: str
	):
		self.poll_duration = poll_duration
		self.event_type = event_type
		self.poll_title = poll_title
		self.wom_start_time = int(time.mktime((date.today() + timedelta((4-date.today().weekday()) % 7)).timetuple())) + (60 * 60 * 21)
		self.end_time = int((datetime.utcnow() + timedelta(hours=float(poll_duration))).timestamp())
		# The placeholder is what will be shown when no option is chosen
		# The min and max values indicate we can only pick one of the three options
		# The options parameter defines the dropdown options. We defined this above

		guild = client.get_guild(int(GUILD_ID))
		for emoji in guild.emojis:
			if emoji.name.lower() in all_skills:
				skill_emoji_map[emoji.name] = f"<:{emoji.name}:{emoji.id}>"
			elif emoji.name.lower() in curated_bosses:
				boss_emoji_map[emoji.name] = f"<:{emoji.name}:{emoji.id}>"

		#skill_emoji_map = {emoji.name: f"<:{emoji.name}:{emoji.id}>" for emoji in guild.emojis if emoji.name.lower() in all_skills}
		#boss_emoji_map = {emoji.name: f"<:{emoji.name}:{emoji.id}>" for emoji in guild.emojis if emoji.name.lower() in curated_bosses}

		print(boss_emoji_map)

		# Gets all skill/boss choices that the bot displays
		skill_select_choices = [discord.SelectOption(label=get_readable_name(skill), value=get_readable_name(skill), description=f"The skill of {get_readable_name(skill)}", emoji=skill_emoji_map[get_emoji_name(skill)]) for skill in all_skills]
		curated_boss_select_choices = [discord.SelectOption(label=get_readable_name(boss), value=get_readable_name(boss), description=f"The boss {get_readable_name(boss)}", emoji=boss_emoji_map[get_emoji_name(boss)]) for boss in curated_bosses]

		if self.event_type == "BOTW":
			options = curated_boss_select_choices

		elif self.event_type == "SOTW":
			options = skill_select_choices


		# noinspection PyUnboundLocalVariable
		super().__init__(placeholder='Select the options for the poll...', min_values=2, max_values=10, options=options)

	async def callback(self, interaction: discord.Interaction):

		with open(DB_FILE_PATH, 'r', encoding="utf-8") as r:
			db = json.loads(r.read())

		nl = "\n"
		if self.event_type == "BOTW":
			emoji_map = boss_emoji_map

			poll_prefix = "boss"
			for boss_value in self.values:
				print(boss_value, get_emoji_name(boss_value), emoji_map)
			first_results = {emoji_map[get_emoji_name(boss_value)]: 0 for boss_value in self.values}
			choices = nl.join(f"{emoji_map[get_emoji_name(boss_value)]} {boss_value}" for boss_value in self.values)
			results = f"{nl.join(f'{i} {v}' for i, v in first_results.items())}\nTotal votes: {sum(list(first_results.values()))}"

		elif self.event_type == "SOTW":
			emoji_map = skill_emoji_map

			poll_prefix = "skill"
			first_results = {emoji_map[get_emoji_name(skill_value)]: 0 for skill_value in self.values}
			choices = nl.join(f"{emoji_map[get_emoji_name(skill_value)]} {skill_value}" for skill_value in self.values)
			results = f"{nl.join(f'{i} {v}' for i, v in first_results.items())}\nTotal votes: {sum(list(first_results.values()))}"

		embed = discord.Embed(
			title=f"Iron Drip {self.poll_title} Poll",
			# noinspection PyUnboundLocalVariable
			description=f"Vote for the {poll_prefix} of the week!",  # noinspection PyUnboundLocalVariable
			color=5763719
		)
		# noinspection PyUnboundLocalVariable
		embed.add_field(name="Choices:", value=choices, inline=False)  # NOTE: Only works for skills atm
		# noinspection PyUnboundLocalVariable
		embed.add_field(name="Results:", value=results, inline=False)  # Get reactions of each letter
		embed.add_field(name="Terms:", value=f"⏰ Poll ends: <t:{self.end_time}:R>\n⏰ WoM Starts: <t:{self.wom_start_time}:R>\n🤓 One vote allowed!", inline=False)
		embed.timestamp = datetime.now()
		embed.set_footer(text="Updated:")
		await interaction.response.send_message(embed=embed)

		channel = client.get_channel(CHANNEL_ID)
		await channel.send(f"<@&{EVENTS_ROLE_ID}> {self.poll_title} poll has begun!")

		guild = client.get_guild(int(GUILD_ID))
		original_response = await interaction.original_response()
		print("Original Response: ", original_response.id)

		if str(interaction.guild_id) not in db.keys():
			db[str(guild.id)] = {"server_name": guild.name, "poll": [], 'wom': []}

		db[str(guild.id)]['poll'].append(
			{
				"poll_title": f"Iron Drip {self.poll_title} Poll",
				"poll_description": f"Vote for the {poll_prefix} of the week!",
				"poll_end_time": int(self.end_time),
				"poll_duration": int(self.poll_duration),
				"poll_choices": {choice_value: emoji_map[get_emoji_name(choice_value)] for choice_value in self.values},
				# noinspection PyUnboundLocalVariable
				"wom_start_time": int(self.wom_start_time),
				"poll_message_id": original_response.id,
				"event_type": self.event_type,
				"active": True,
				"wom_started": False,
				"wom": {}
			}
		)
		# Add DB Entry
		with open(DB_FILE_PATH, 'w', encoding="utf-8") as r:
			r.write(json.dumps(db, indent=4, ensure_ascii=False))

		# Add reactions
		print("ADDING REACTIONS")
		for value in self.values:
			print(value, emoji_map[get_emoji_name(value)])
			await original_response.add_reaction(emoji_map[get_emoji_name(value)])

		time.sleep(1)
		update_poll.start()


@client.tree.command(name="vote")
@app_commands.describe(poll_duration="The number of hours you want the poll to run for.")
@app_commands.describe(poll_title="The title of your poll, EG: 'BOTW #8'.")
@app_commands.choices(
	event_type=[
		app_commands.Choice(name="SOTW", value="SOTW"),
		app_commands.Choice(name="BOTW", value="BOTW")
	]
)
async def vote(interaction: discord.Interaction, poll_duration: str, poll_title: str, event_type: str):

	view = discord.ui.View()
	view.add_item(Dropdown(poll_duration=poll_duration, poll_title=poll_title, event_type=event_type))
	await interaction.response.send_message(view=view, ephemeral=True)

	with open(REACTION_HISTORY_FILE_PATH, 'w', encoding="utf-8") as r:
		r.write(json.dumps({}, indent=4, ensure_ascii=False))


@client.event
async def on_raw_reaction_remove(payload):
	with open(REACTION_HISTORY_FILE_PATH, 'r', encoding="utf-8") as r:
		message_db = json.loads(r.read())

	# TODO: Access specific poll message ID (loop through polls and find if reaction_msg_id == poll_msg_id)

	reaction_message_id = str(payload.message_id)
	user_id = str(payload.user_id)
	reaction_emoji_id = str(payload.emoji.id)

	if reaction_message_id in list(message_db.keys()):
		if message_db[reaction_message_id].get(user_id, None) is None:
			print("REACTION REMOVE NOT FOUND (SHOULD ONLY HAPPEN ON_READY DUPLICATE REMOVAL): ", reaction_message_id, user_id)
			return

		# Only deletes the users reaction if the user selected (and removed) the emoji
		if user_id in message_db[reaction_message_id]:
			if reaction_emoji_id == message_db[reaction_message_id][user_id]:
				del message_db[reaction_message_id][user_id]

		with open(REACTION_HISTORY_FILE_PATH, 'w', encoding="utf-8") as r:
			r.write(json.dumps(message_db, indent=4, ensure_ascii=False))


@client.event
async def on_raw_reaction_add(payload):
	print(payload)
	with open(DB_FILE_PATH, 'r', encoding="utf-8") as r:
		db = json.loads(r.read())

	with open(REACTION_HISTORY_FILE_PATH, 'r', encoding="utf-8") as r:
		message_db = json.loads(r.read())

	# TODO: Access specific poll message ID (loop through polls and find if reaction_msg_id == poll_msg_id)

	reaction_message_id = str(payload.message_id)
	user_id = str(payload.user_id)
	reaction_emoji_id = str(payload.emoji.id)

	poll_message_ids = []
	for poll in db[str(payload.guild_id)]['poll']:
		msg_id = poll.get("poll_message_id", None)
		if msg_id is not None:
			poll_message_ids.append(msg_id)

	if int(reaction_message_id) in poll_message_ids:  # Ensure the targeted message is that of the poll
		if int(user_id) != BOT_MEMBER_ID:  # checking if it's sent by the bot
			print("I AM HERE LOL")
			# If user in DB already, remove the reaction
			print(message_db.get(reaction_message_id, None), message_db[reaction_message_id].get(user_id, None))
			if message_db.get(reaction_message_id, None) is not None:
				if message_db[reaction_message_id].get(user_id, None) is not None:
					print(f"TOO MANY: {payload.member.name}#{payload.member.discriminator}, {message_db[reaction_message_id][user_id]}")

					channel = client.get_channel(CHANNEL_ID)
					message = await channel.fetch_message(int(reaction_message_id))

					await message.remove_reaction(payload.emoji, payload.member)
					return

				# Else add the user to the DB
				else:
					print("ADDING", user_id)
					message_db[reaction_message_id][user_id] = reaction_emoji_id

		else:
			print("RESETING MESSAGE DB")
			message_db[reaction_message_id] = {}

	with open(REACTION_HISTORY_FILE_PATH, 'w', encoding="utf-8") as r:
		r.write(json.dumps(message_db, indent=4, ensure_ascii=False))


@client.event
async def on_ready():
	print(f"{client.user} is now online.")
	with open(DB_FILE_PATH, 'r', encoding="utf-8") as r:
		db = json.loads(r.read())

	with open(REACTION_HISTORY_FILE_PATH, 'r', encoding="utf-8") as r:
		message_db = json.loads(r.read())

	# boss_emoji_map = {}
	# for guild in client.guilds:
	#	if str(guild.id) == GUILD_ID:
	#		print(guild)
	#		for emoji in guild.emojis:
	#			if emoji.name.lower() in curated_bosses:
	#				boss_emoji_map[emoji.name] = f"<:{emoji.name}:{emoji.id}>"
	#				# agility': '<:agility:1051872061280223272>'
	# print(boss_emoji_map)

	# INCASE OF BOT SHUTDOWN THIS WILL REMOVE DUPLICATE VOTES ON STARTUP
	# -------------------------------------------------------
	channel = client.get_channel(CHANNEL_ID)
	if db.get(GUILD_ID) is not None:

		for index, poll in enumerate(db[GUILD_ID]['poll']):
			if poll['active'] is True:
				poll_message_id = poll['poll_message_id']
				message = await channel.fetch_message(poll_message_id)
				reactions = message.reactions
				all_users = []
				for reaction in reactions:
					all_users += [user async for user in reaction.users()]

				duplicates = [member for member in all_users if len([user.id for user in all_users if member.id == user.id]) > 1]
				for duplicate_user in set(duplicates):
					if duplicate_user.id == BOT_MEMBER_ID:  # Doesn't remove bot reactions
						continue

					for emoji in poll['poll_choices'].values():
						print("Removing reaction duplicates from: ", duplicate_user.name, "Emoji: ", emoji)
						await message.remove_reaction(emoji, duplicate_user)  # Removes reaction
						if message_db[str(poll_message_id)].get(str(duplicate_user.id), None) is not None:
							del message_db[str(poll_message_id)][str(duplicate_user.id)]  # Updates DB locally

							# Updates DB
							with open(REACTION_HISTORY_FILE_PATH, 'w', encoding="utf-8") as r:
								r.write(json.dumps(message_db, indent=4, ensure_ascii=False))

				print(all_users)
				# -------------------------------------------------------

			if poll != {}:
				if poll['active'] is True or poll['wom_started'] is False:
					print(f"Starting update poll for: {poll['poll_title']}, {poll['poll_message_id']}")
					update_poll.start()  # Incase of error, the task will be started again.

			if poll['wom'] != {} and poll['wom_started'] is True and poll['wom']['active'] is True:
				print(f"Starting update wom for: {poll['wom']['wom_title']}, {poll['wom']['wom_id']}")
				update_wom.start()

	try:
		synced = await client.tree.sync()
		print(f"Synced {len(synced)} command(s)")
	except Exception as e:
		print(321, e)


# TODO: (NOTE) FOR CHANGING RSN ON USER JOIN (HAS NOTIN TO DO WITH SOTW)
@client.event
async def on_message(message: discord.Message):
	if message.channel.id == 1085003013367812128 and message.author.bot is False:
		try:
			print(message.author.bot)
			await message.author.edit(nick=message.content)
			await message.author.add_roles(client.get_guild(int(GUILD_ID)).get_role(1007082577972166656)) # Newcomer role
			await message.author.remove_roles(client.get_guild(int(GUILD_ID)).get_role(987130322162446397)) # New role
			try:
				await message.delete()
			except Exception as e:
				print("Unable to delete message", e)
		except Exception as e:
			print("ROLE ASSIGN", e)
			await message.reply("Failed to changed name. TRY AGAIN!!!")
			await message.delete()


@client.event
async def on_member_join(member: discord.Member):
	await member.add_roles(client.get_guild(int(GUILD_ID)).get_role(987130322162446397))
	print(member.name, "Assigned role")

client.run(token)
