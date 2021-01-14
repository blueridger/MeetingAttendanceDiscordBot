import discord
import os
from datetime import datetime, timedelta
import time
from keep_alive import keep_alive

client = discord.Client()

KEY_LENGTH_MINS = 'LengthMins:'
KEY_CHANNEL = 'Channel:'

def formatMessage(msgDict):
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

    # Send the initial output
    meeting_message = await message.channel.send(formatMessage(result))

    # Parse some helper variables
    timeLimitSecs = int(result[KEY_LENGTH_MINS]) * 60
    voice_channel = None
    for channel in message.guild.channels:
      if channel.name == result[KEY_CHANNEL]:
        voice_channel = channel

    # Watch and build the participants lists and update the output
    participants = set()
    participant_names = set()
    while datetime.utcnow() < startTime + timedelta(seconds=20):
      users = [(await client.fetch_user(user_id)) for user_id in voice_channel.voice_states.keys()]
      participants = participants | set([user.mention for user in users])
      participant_names = participant_names | set([user.name for user in users])
      result['Participants:'] = '(watching) ' + ' '.join(participants)
      await meeting_message.edit(content=formatMessage(result), suppress=True)
      time.sleep(3)

    # Finalize outputs
    result['Participants:'] = ' '.join(participants)
    await meeting_message.edit(content=formatMessage(result))
    roam_formatted = '[[' + ']]\n[['.join(participant_names) + ']]'
    await message.author.send(content=roam_formatted)
    
keep_alive()
client.run(os.getenv('TOKEN'))