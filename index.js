const keep_alive = require('./keep_alive.js')
const Discord = require('discord.js');

const client = new Discord.Client();
const token = process.env.DISCORD_BOT_SECRET;

// keys must be lowercase
const KEY_LENGTH_MINS = '--duration'.toLowerCase()
const KEY_CHANNEL = '--channel'.toLowerCase()
const KEY_OUTPUT_CHANNEL = '--outputchannel'.toLowerCase()

const REQUIRED_KEYS = [KEY_LENGTH_MINS]
const BUSY_WAIT_INTERVAL_SECONDS = 30
const DOCUMENTATION_LINK = 'https://github.com/blueridger/MeetingAttendanceDiscordBot/blob/mainline/README.md'

function* batch(arr, n=1) {
    const l = arr.length
    let i = 0;
    while (i <= l) {
        yield arr.slice(i, Math.min(i + n, l))
        i += n
    }
}

function sleep(seconds) {
  return new Promise(resolve => setTimeout(resolve, seconds * 1000));
}

client.on('ready', () => {
  console.log("I'm in");
  console.log(client.user.username);
});

client.on('message', async msg => {
    if (msg.author.id === client.user.id) {
        return;
    }
    if (msg.content.startsWith("!meeting")) {
        try {
            const args = parseArgumentsFromMessage(msg)
            if (!args) return
            let {
                metadata, 
                voiceChannelSubstring, 
                outputChannelSubstring, 
                durationMins
            } = args
            
            let voiceChannel;
            if (voiceChannelSubstring) {
                voiceChannel = msg.guild.channels.cache.find(channel => channel.type === 'voice' && channel.name.toLowerCase().includes(voiceChannelSubstring))
            } else if (msg.member.voice.channel) {
                voiceChannel = msg.member.voice.channel
            }

            let outputChannel = msg.channel
            if (outputChannelSubstring) {
                outputChannel = msg.guild.channels.cache.find(channel => channel.type === 'text' && channel.name.toLowerCase().includes(outputChannelSubstring))
            }

            if (!voiceChannel) {
                msg.author.send(`Voice channel was not found. Please join a voice channel or use the \`${KEY_CHANNEL}\` parameter.`)
                return
            }

            const meetingMsg = await outputChannel.send(metadata + '\nParticipants: (watching)')

            watchChannel(
                meetingMsg,
                msg,
                durationMins,
                metadata,
                voiceChannel,
            )
        } catch (e) {
            console.log(e)
            try {
                msg.author.send(
                    "An error was thrown. Please have the bot maintainer check the console log for details."
                )
            } catch (e) {
                console.log(e)
            }
        }
    }
});

function parseArgumentsFromMessage(msg) {
    let voiceChannelSubstring, outputChannelSubstring, durationMins;
    const firstLineBreakIndex = msg.content.indexOf('\n') > 0 ? msg.content.indexOf('\n') : msg.content.length
    const command = msg.content.slice(0, firstLineBreakIndex).toLowerCase().match(/\S+/g) || []
    const metadata = msg.content.slice(firstLineBreakIndex)

    try {
        if (command.includes(KEY_CHANNEL))
            voiceChannelSubstring = command[command.indexOf(KEY_CHANNEL) + 1]
        if (command.includes(KEY_OUTPUT_CHANNEL))
            outputChannelSubstring = command[command.indexOf(KEY_OUTPUT_CHANNEL) + 1]
        if (command.includes(KEY_LENGTH_MINS))
            durationMins = command[command.indexOf(KEY_LENGTH_MINS) + 1]
    } catch {
        msg.author.send(`Failed to parse. Unexpected end of parameters.\n${DOCUMENTATION_LINK}`)
        return null
    }

    if (REQUIRED_KEYS.filter(key => !command.includes(key)).length) {
        msg.author.send(`A required key was not found. Please provide the keys: ${REQUIRED_KEYS}\n${DOCUMENTATION_LINK}`)
        return null
    }
    if (isNaN(parseInt(durationMins, 10)) || durationMins < 1 || durationMins > 120) {
        msg.author.send(`${KEY_LENGTH_MINS} [${durationMins}] was not valid. Please provide an integer between 1 and 120.`)
        return null
    }
    durationMins = parseInt(durationMins, 10)
    return {metadata, voiceChannelSubstring, outputChannelSubstring, durationMins}
}

async function watchChannel(
    meetingMsg,
    commandMsg,
    durationMins,
    metadata,
    voiceChannel,
) {
    startTime = new Date(meetingMsg.createdAt)
    expiration = startTime.setMinutes(startTime.getMinutes() + durationMins)
    const participantMentions = new Set()

    console.log(`[${meetingMsg.id}] Starting to watch.`)
    while (Date.now() < expiration) {
        (await voiceChannel.fetch()).members.each((member) => {
            if (!member.user.bot) {
                participantMentions.add(member.user.toString())
            }
        })
        const participantsString = `\nParticipants: (watching) ${Array.from(participantMentions).join(' ')}`
        await meetingMsg.edit(metadata + participantsString)
        console.log(`[${meetingMsg.id}] Current list: [${Array.from(participantMentions)}].`)
        await sleep(BUSY_WAIT_INTERVAL_SECONDS)
    }

    console.log(`[${meetingMsg.id}] Finished watching.`)

    const participantsString = `\nParticipants: ${Array.from(participantMentions).join(' ')}`
    await meetingMsg.edit(metadata + participantsString)

    console.log(`[${meetingMsg.id}] Finished thread.`)
}

client.login(token);