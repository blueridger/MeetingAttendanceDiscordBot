# Meeting Attendance Discord Bot
This is a simple discord bot that automates an operational process for the [SourceCred](sourcecred.io) community. It may be useful for other communities.

It posts a meeting summary message that auto-updates a list of participants as people join a designated voice channel in discord.

# Usage
```
!meeting --duration 60 [optional parameters]
[content]
```
**Required Parameter:**
- `--duration 60` is for choosing how many **minutes** the bot should watch for participants. Any integer between 1 and 120 is accepted.

**Optional Parameters:**
- `--channel voice-channel-name` is for selecting which voice channel to watch. A partial name will be matched to the first channel that matches. Defaults to the one you are already in.
- `--outputchannel meeting-notes-channel` is for selecting which channel the bot should send the output to. A partial name will be matched to the first channel that matches. Defaults to the channel where the command is used.

Parameters are case-insensitive and must be included in the first line.

**Content:**
- All lines after the first line will be included as is in the output, including mentions and styling.


# Example
```
!meeting --duration 59 --channel general --outputchannel notes
Hosts: @Garnet @everyone Amethyst
Fancypants: also @Garnet
Notes: https://www.github.com
```
will first output something like:
```
Hosts: @Garnet @everyone Amethyst
Fancypants: also @Garnet
Notes: https://www.github.com
Participants: (watching) @Pearl
```
In this example, @Pearl was already in the General-Voice channel, which matched to the partial name `general`. When another user joins the channel, the bot will update the last line:
```
Participants: (watching) @Pearl @Garnet
```
When 59 minutes pass, the code thread will finish and the output message will finalize as:
```
Hosts: @Garnet @everyone Amethyst
Fancypants: also @Garnet
Notes: https://www.github.com
Participants: @Pearl @Garnet
```

# Installation
I used the infrastructure described in this tutorial: https://www.codementor.io/@garethdwyer/building-a-discord-bot-with-node-js-and-repl-it-mm46r1u8y

I gave the bot these permissions, but it may not need all of them. (permissions=84992)
- View Channels
- Send Messages
- Embed Links
- Read Message History

