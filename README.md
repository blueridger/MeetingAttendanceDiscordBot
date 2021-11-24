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
  - While the meeting is being watched by the bot, the original command-user can edit the duration by simply editing the parameter in the original command that they sent.

**Optional Parameters:**
- `--channel voice-channel-name` is for selecting which voice channel to watch. A partial name will be matched to the first channel that matches. Defaults to the one you are already in.
- `--outputchannel meeting-notes-channel` is for selecting which channel the bot should send the output to. A partial name will be matched to the first channel that matches. Defaults to the channel where the command is used.

Parameters are case-insensitive and must be included in the first line.

**Content:**
- All lines after the first line will be included as is in the output, including mentions and styling.
  - While the meeting is being watched by the bot and for 30 minutes after, the original command-user can edit the content by simply editing it in the original command that they sent.


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

# Admin Edit/Append Feature
Sometimes the bot crashes. Sometimes you forgot to add a piece of info and the edits expiration has passed. Users with the configured admin role can use the edit/append commands as a last resort. Using the edit command, new content will overwrite the old content. The append command will simply add content to the end of the existing content.

```
!edit messageLink
[content]

!append messageLink
[content]
```
Example:
```
!edit https://discord.com/channels/798975165342023700/798975167971196981/913133132243402763
my new content :)
yay
```

Note: If the original command user is also making edits by editing their original command, your edits overwrite each other.

# Installation
I used the infrastructure described in this tutorial: https://www.codementor.io/@garethdwyer/building-a-discord-bot-with-node-js-and-repl-it-mm46r1u8y

If you want to self-host, add [dotenv](https://www.npmjs.com/package/dotenv) as a dependency and add `require('dotenv').config()` to the top of index.js

You will need to fork this repo to set your own configs.

I gave the bot these permissions, but it may not need all of them. (permissions=84992)
- View Channels
- Send Messages
- Embed Links
- Read Message History

