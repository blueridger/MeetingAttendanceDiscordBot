import discord
import os
from datetime import datetime, timedelta
import time
import traceback
from keep_alive import keep_alive

client = discord.Client()

# keys must be lowercase
KEY_LENGTH_MINS = 'duration:'.lower()
KEY_CHANNEL = 'channel:'.lower()
KEY_OUTPUT_CHANNEL = 'outputchannel:'.lower()
KEY_PARTICIPANTS = 'participants:'.lower()

REQUIRED_KEYS = [KEY_CHANNEL, KEY_LENGTH_MINS]
OUTPUT_OMITTED_KEYS = [KEY_OUTPUT_CHANNEL]
BUSY_WAIT_INTERVAL_SECONDS = 10

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
      startTime = datetime.utcnow()

      # Parse the command
      result = {}
      currentKey = None
      for param in message.content.split():
        if param.endswith(':'):
          currentKey = param.lower()
        elif currentKey in result.keys() and currentKey not in REQUIRED_KEYS:
          result[currentKey] = ' '.join([result[currentKey], param])
        elif currentKey:
          result[currentKey] = param
      
      # Handle incorrect usage
      if not all(key in result.keys() for key in REQUIRED_KEYS):
        await message.author.send(content="A required key was not found. Please provide the keys: {requiredKeys}\n https://github.com/blueridger/MeetingAttendanceDiscordBot/blob/mainline/README.md".format(requiredKeys=REQUIRED_KEYS))
        return
      if (not is_int(result[KEY_LENGTH_MINS]) or int(result[KEY_LENGTH_MINS]) < 1 or int(result[KEY_LENGTH_MINS]) > 120):
        await message.author.send(content="{length_mins_key} [{length_mins}] was not valid. Please provide an integer between 1 and 120.".format(length_mins_key=KEY_LENGTH_MINS, length_mins=result[KEY_LENGTH_MINS]))
        return

      # Parse some helper variables
      timeLimitSecs = int(result[KEY_LENGTH_MINS]) * 60
      voice_channel = None
      for channel in message.guild.voice_channels:
        if result[KEY_CHANNEL] in channel.name:
          voice_channel = channel
          result[KEY_CHANNEL] = channel.name
          break

      output_channel = message.channel
      if KEY_OUTPUT_CHANNEL in result.keys():
        for channel in message.guild.text_channels:
          if result[KEY_OUTPUT_CHANNEL] in channel.name:
            output_channel = channel
            result[KEY_OUTPUT_CHANNEL] = channel.name
            break
      
      # Handle more incorrect usage
      if (not voice_channel):
        await message.author.send(content="Channel: [{channel}] was not found. Please provide a valid voice channel name.".format(channel=result[KEY_CHANNEL]))
        return
      
      # Send the initial output
      meeting_message = await output_channel.send(format_message(result))

      # Watch and build the participants lists and update the output
      participants = set()
      participant_names = set()
      while datetime.utcnow() < startTime + timedelta(seconds=timeLimitSecs):
        users = [(await client.fetch_user(user_id)) for user_id in voice_channel.voice_states.keys()]
        filter(lambda u: not u.bot, users)
        participants = participants | set([user.mention for user in users])
        participant_names = participant_names | set([user.name for user in users])
        result[KEY_PARTICIPANTS] = '(watching) ' + ' '.join(participants)
        await meeting_message.edit(content=format_message(result), suppress=True)
        time.sleep(BUSY_WAIT_INTERVAL_SECONDS)

      # Finalize outputs
      result[KEY_PARTICIPANTS] = ' '.join(participants)
      await meeting_message.edit(content=format_message(result))
      roam_formatted = message.content + '\n[[' + ']]\n[['.join(participant_names) + ']]'
      await message.author.send(content=roam_formatted)
    except discord.errors.NotFound:
      # Message was deleted
      pass
    except:
      traceback.print_exc()
      try:
        await message.author.send(content="An error was thrown. Please have the bot maintainer check the console log for details.")
      except:
        pass
    
keep_alive()
client.run(os.getenv('TOKEN'))