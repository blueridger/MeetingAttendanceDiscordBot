import discord
import os
import asyncio
from datetime import datetime, timedelta
import traceback
from keep_alive import keep_alive
import threading
from replit import db

client = discord.Client()

# keys must be lowercase
KEY_LENGTH_MINS = '--duration'.lower()
KEY_CHANNEL = '--channel'.lower()
KEY_OUTPUT_CHANNEL = '--outputchannel'.lower()

REQUIRED_KEYS = [KEY_LENGTH_MINS]
BUSY_WAIT_INTERVAL_SECONDS = 30
DOCUMENTATION_LINK = 'https://github.com/blueridger/MeetingAttendanceDiscordBot/blob/mainline/README.md'

def batch(iterable, n=1):
    l = len(iterable)
    for ndx in range(0, l, n):
        yield iterable[ndx:min(ndx + n, l)]

def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!meeting'):
        try:
            voice_channel_substring = None
            output_channel_substring = None
            duration_mins = None

            command, _, metadata = message.content.partition('\n')
            command = command.lower().split()
            try:
                if KEY_CHANNEL in command:
                    voice_channel_substring = command[
                        command.index(KEY_CHANNEL) + 1
                    ]
                if KEY_OUTPUT_CHANNEL in command:
                    output_channel_substring = command[
                        command.index(KEY_OUTPUT_CHANNEL) + 1
                    ]
                if KEY_LENGTH_MINS in command:
                    duration_mins = command[command.index(KEY_LENGTH_MINS) + 1]
            except:
                await message.author.send(
                    content=f"Failed to parse. Unexpected end of parameters.\n{DOCUMENTATION_LINK}"
                )
                return

            # Handle incorrect usage
            if not all(key in command for key in REQUIRED_KEYS):
                await message.author.send(
                    content="A required key was not found. "
                    f"Please provide the keys: {REQUIRED_KEYS}\n{DOCUMENTATION_LINK}"
                )
                return
            if (not is_int(duration_mins) or int(duration_mins) < 1 or int(duration_mins) > 120):
                await message.author.send(
                    content=
                    f"{KEY_LENGTH_MINS} [{duration_mins}] was not valid. "
                    "Please provide an integer between 1 and 120."
                )
                return

            # Parse some helper variables
            voice_channel = None
            if voice_channel_substring is not None:
                for channel in message.guild.voice_channels:
                    if voice_channel_substring in channel.name.lower():
                        voice_channel = channel
                        voice_channel_substring = channel.name
                        break
            elif message.author.voice is not None:
                voice_channel = message.author.voice.channel

            output_channel = message.channel
            if output_channel_substring is not None:
                for channel in message.guild.text_channels:
                    if output_channel_substring in channel.name.lower():
                        output_channel = channel
                        output_channel_substring = channel.name
                        break

            # Handle more incorrect usage
            if (not voice_channel):
                await message.author.send(
                    content="Voice channel was not found. "
                    "Please enter a voice channel or use the `channel:` parameter."
                )
                return

            # Send the initial output
            meeting_message = await output_channel.send(
                content=metadata + '\nParticipants: (watching)'
            )
            await startWatching(
                meeting_message,
                duration_mins,
                message.author,
                metadata,
                voice_channel.id
            )

        except discord.errors.NotFound:
            # Message was deleted
            print('[%s] Message was deleted.' % meeting_message.id)
        except discord.errors.HTTPException as e:
            print(e)
            print(e.response)
        except:
            traceback.print_exc()
            try:
                await message.author.send(
                    content="An error was thrown. Please have the bot maintainer check the console log for details."
                )
            except Exception as e:
                print(e)


async def startWatching(
    meeting_message,
    duration_mins,
    user,
    metadata,
    voice_channel_id,
    participant_ids=set(),
):
    startTime = meeting_message.created_at
    timeLimitSecs = int(duration_mins) * 60
    for ids_batch in batch(participant_ids, 3):
        users = set([(await client.fetch_user(user_id)) for user_id in ids_batch])
        await asyncio.sleep(6)

    # Watch and build the participants lists and update the output
    print('[%s] Starting to watch.' % meeting_message.id)
    while datetime.utcnow() < startTime + timedelta(seconds=timeLimitSecs):
        current_ids = set((await client.fetch_channel(voice_channel_id)).voice_states.keys())
        new_ids = current_ids - participant_ids
        if len(new_ids) > 0:
            for ids_batch in batch(new_ids, 3):
                users |= set([(await client.fetch_user(user_id)) for user_id in ids_batch])
                await asyncio.sleep(6)
            users = set(filter(lambda u: not u.bot, users))
            participants = set([user.mention for user in users])
            participant_ids |= new_ids
            participants_string = f"\nParticipants: (watching) {' '.join(participants)}"
            print(f'[{meeting_message.id}] Adding {new_ids}')
            await meeting_message.edit(
                content=metadata + participants_string,
                suppress=True
            )
        await asyncio.sleep(BUSY_WAIT_INTERVAL_SECONDS)

    print(f'[{meeting_message.id}] Finished watching.')

    # Finalize outputs
    participants = set([user.mention for user in users])
    participants_string = f"\nParticipants: {' '.join(participants)}"
    await asyncio.sleep(6)
    await meeting_message.edit(
        content=metadata + participants_string,
        suppress=True
    )
    roam_participants = '\n'.join([f'[[{user.name}]]' for user in users])
    roam_formatted = f"\n```{roam_participants}```"
    await user.send(content=metadata + roam_formatted)
    print('[%s] Finished thread.' % meeting_message.id)


keep_alive()
try:
    client.run(os.getenv('TOKEN'))
except discord.errors.HTTPException as e:
    print(e)
    print(e.response)
