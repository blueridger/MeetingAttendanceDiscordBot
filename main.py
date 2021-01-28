import discord
import os
from datetime import datetime, timedelta
import time
import traceback
from keep_alive import keep_alive
import threading
from replit import db

client = discord.Client()

# keys must be lowercase
KEY_LENGTH_MINS = 'duration:'.lower()
KEY_CHANNEL = 'channel:'.lower()
KEY_OUTPUT_CHANNEL = 'outputchannel:'.lower()
KEY_PARTICIPANTS = 'participants:'.lower()

REQUIRED_KEYS = [KEY_CHANNEL, KEY_LENGTH_MINS]
OUTPUT_OMITTED_KEYS = [KEY_OUTPUT_CHANNEL]
BUSY_WAIT_INTERVAL_SECONDS = 15

def is_int(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False

def format_message(msgDict):
  message = ""
  for key, value in msgDict.items():
    if key not in OUTPUT_OMITTED_KEYS:
      message = message + "\n" + key.capitalize() + "  " + value
  return message

@client.event
async def on_ready():
  print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
  if message.author == client.user:
    return

  if message.content.startswith('$meeting'):
    try:

      # Parse the command
      parsed_params = {}
      currentKey = None
      for param in message.content.split():
        if param.endswith(':'):
          currentKey = param.lower()
        elif currentKey in parsed_params.keys() and currentKey not in REQUIRED_KEYS:
          parsed_params[currentKey] = ' '.join([parsed_params[currentKey], param])
        elif currentKey:
          parsed_params[currentKey] = param
      
      # Handle incorrect usage
      if not all(key in parsed_params.keys() for key in REQUIRED_KEYS):
        await message.author.send(content="A required key was not found. Please provide the keys: {requiredKeys}\n https://github.com/blueridger/MeetingAttendanceDiscordBot/blob/mainline/README.md".format(requiredKeys=REQUIRED_KEYS))
        return
      if (not is_int(parsed_params[KEY_LENGTH_MINS]) or int(parsed_params[KEY_LENGTH_MINS]) < 1 or int(parsed_params[KEY_LENGTH_MINS]) > 120):
        await message.author.send(content="%s [%s] was not valid. Please provide an integer between 1 and 120." % (KEY_LENGTH_MINS, parsed_params[KEY_LENGTH_MINS]))
        return

      # Parse some helper variables
      voice_channel = None
      for channel in message.guild.voice_channels:
        if parsed_params[KEY_CHANNEL] in channel.name:
          voice_channel = channel
          parsed_params[KEY_CHANNEL] = channel.name
          break

      output_channel = message.channel
      if KEY_OUTPUT_CHANNEL in parsed_params.keys():
        for channel in message.guild.text_channels:
          if parsed_params[KEY_OUTPUT_CHANNEL] in channel.name:
            output_channel = channel
            parsed_params[KEY_OUTPUT_CHANNEL] = channel.name
            break
      
      # Handle more incorrect usage
      if (not voice_channel):
        await message.author.send(content="Channel: %s was not found. Please provide a valid voice channel name." % parsed_params[KEY_CHANNEL])
        return
      
      # Send the initial output
      meeting_message = await output_channel.send(format_message(parsed_params))
      startWatching(meeting_message, message.author, parsed_params, voice_channel.id)

      
    except discord.errors.NotFound:
      # Message was deleted
      print('[%s] Message was deleted.' % meeting_message.id)
    except discord.errors.HTTPException as e:
      print(e)
    except:
      traceback.print_exc()
      try:
        await message.author.send(content="An error was thrown. Please have the bot maintainer check the console log for details.")
      except Exception as e:
        print(e)

def startWatching(meeting_message, user, parsed_params, voice_channel_id, participant_ids = set(), participants = set(), participant_names = set()):
  startTime = meeting_message.created_at
  timeLimitSecs = int(parsed_params[KEY_LENGTH_MINS]) * 60
  # Watch and build the participants lists and update the output
  print('[%s] Starting to watch.' % meeting_message.id)
  while datetime.utcnow() < startTime + timedelta(seconds=timeLimitSecs):
    new_ids = set((await client.fetch_channel(voice_channel_id)).voice_states.keys()) - participant_ids
    users = [(await client.fetch_user(user_id)) for user_id in new_ids]
    users = list(filter(lambda u: not u.bot, users))
    participants = participants | set([user.mention for user in users])
    participant_names = participant_names | set([user.name for user in users])
    participant_ids = participant_ids | new_ids
    parsed_params[KEY_PARTICIPANTS] = '(watching) ' + ' '.join(participants)
    if len(new_ids) > 0:
      print('[%s] Adding %s' % (meeting_message.id, new_ids))
      await meeting_message.edit(content=format_message(parsed_params), suppress=True)
    time.sleep(BUSY_WAIT_INTERVAL_SECONDS)
  
  print('[%s] Finished watching.' % meeting_message.id)

  # Finalize outputs
  parsed_params[KEY_PARTICIPANTS] = ' '.join(participants)
  await meeting_message.edit(content=format_message(parsed_params))
  roam_formatted = '\n```[[' + ']]\n[['.join(participant_names) + ']]```'
  await user.send(content=roam_formatted)
  print('[%s] Finished thread.' % meeting_message.id)

keep_alive()
try:
  client.run(os.getenv('TOKEN'))
except discord.errors.HTTPException as e:
  print(e)
  print(e.response)