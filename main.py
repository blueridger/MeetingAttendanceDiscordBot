import discord
import os
from datetime import datetime, timedelta
import time
import traceback
from keep_alive import keep_alive

client = discord.Client()

KEY_LENGTH_MINS = 'LengthMins:'
KEY_CHANNEL = 'Channel:'
REQUIRED_KEYS = [KEY_CHANNEL, KEY_LENGTH_MINS]
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
    message = message + "\n" + key + "  " + value
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
      currentKey = ""
      for param in message.content.split():
        if param.endswith(':'):
          currentKey = param
          result[currentKey] = ""
        elif currentKey in [KEY_LENGTH_MINS, KEY_CHANNEL]:
          result[currentKey] = param
        elif currentKey in result.keys():
          result[currentKey] = ' '.join([result[currentKey], param])
      
      # Handle incorrect usage
      if not all(key in result.keys() for key in REQUIRED_KEYS):
        await message.author.send(content="A required key was not found. Please provide the keys: {requiredKeys}\n https://github.com/blueridger/MeetingAttendanceDiscordBot/blob/mainline/README.md".format(requiredKeys=REQUIRED_KEYS))
        return
      if (not is_int(result[KEY_LENGTH_MINS]) or int(result[KEY_LENGTH_MINS]) < 1 or int(result[KEY_LENGTH_MINS]) > 120):
        await message.author.send(content="LengthMins: [{lengthMins}] was not valid. Please provide an integer between 1 and 120.".format(lengthMins=result[KEY_LENGTH_MINS]))
        return

      # Parse some helper variables
      timeLimitSecs = int(result[KEY_LENGTH_MINS]) * 60
      voice_channel = None
      for channel in message.guild.channels:
        if channel.name == result[KEY_CHANNEL]:
          voice_channel = channel
      
      # Handle more incorrect usage
      if (not voice_channel):
        await message.author.send(content="Channel: [{channel}] was not found. Please provide a valid voice channel name.".format(channel=result[KEY_CHANNEL]))
        return
      
      # Send the initial output
      meeting_message = await message.channel.send(format_message(result))

      # Watch and build the participants lists and update the output
      participants = set()
      participant_names = set()
      while datetime.utcnow() < startTime + timedelta(seconds=timeLimitSecs):
        users = [(await client.fetch_user(user_id)) for user_id in voice_channel.voice_states.keys()]
        filter(lambda u: not u.bot, users)
        participants = participants | set([user.mention for user in users])
        participant_names = participant_names | set([user.name for user in users])
        result['Participants:'] = '(watching) ' + ' '.join(participants)
        await meeting_message.edit(content=format_message(result), suppress=True)
        time.sleep(BUSY_WAIT_INTERVAL_SECONDS)

      # Finalize outputs
      result['Participants:'] = ' '.join(participants)
      await meeting_message.edit(content=format_message(result))
      roam_formatted = message.content + '\n[[' + ']]\n[['.join(participant_names) + ']]'
      await message.author.send(content=roam_formatted)
    except:
      traceback.print_exc()
      try:
        await message.author.send(content="An error was thrown. Please have the bot maintainer check the console log for details.")
      except:
        pass
    
keep_alive()
client.run(os.getenv('TOKEN'))