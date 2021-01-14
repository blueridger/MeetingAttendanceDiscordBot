# Meeting Attendance Discord Bot
This is a simple discord bot that automates an operational process for the [SourceCred](sourcecred.io) community. It may be useful for other communities.

It posts a meeting summary message that auto-updates a list of participants as people join a designated voice channel in discord. It also direct messages a Roam Research friendly version of the participants list to the command user at the end of the meeting.

# Usage
```
$meeting Channel: voice_channel_name LengthMins: length_in_minutes
```
You can also intersperse additional key-values arguments of the form `Key: value1 value2 ...` in any order, which will appear as additional lines in the output.

White space is reformatted, so feel free to use line breaks if you want more human-readable commands. User tags and text formatting are carried over into the output.

# Example
```
$meeting Topic: Community Call LengthMins: 60 Channel: General-Voice Hosts: @Garnet @everyone Amethyst Fancypants: also @Garnet Notes: https://www.github.com
```
which equivalent to:
```
$meeting Topic: Community Call 
LengthMins: 60
Channel: General-Voice 
Hosts: @Garnet @everyone      Amethyst 
Fancypants: also @Garnet 
Notes: https://www.github.com
```
will first output:
```
Topic: Community Call
LengthMins: 60
Channel: General-Voice
Hosts: @Garnet @everyone Amethyst
Fancypants: also @Garnet
Notes: https://www.github.com
Participants: (watching) @Pearl
```
In this example, @Pearl was already in the General-Voice channel. When another user joins the channel, the bot will update the last line to:
```
Participants: (watching) @Pearl @Garnet
```
When LengthMins minutes pass, the code thread will finish and the last line will finalize as:
```
Participants: @Pearl @Garnet
```

# Installation
I used the infrastructure described in this tutorial: https://www.freecodecamp.org/news/create-a-discord-bot-with-python/

I gave the bot these permissions, but it may not need all of them. (permissions=84992)
- View Channels
- Send Messages
- Embed Links
- Read Message History

