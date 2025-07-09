"""Command details and descriptions"""

COMMAND_DETAILS = {
    "sultan": {
        "title": "SULTAN COMMAND",
        "description": "MUSIC PLAYBACK CONTROLS",
        "commands": [
            "/pause :- PAUSE CURRENT PLAYING STREAM",
            "/resume :- RESUME PAUSED STREAM",
            "/skip :- SKIP TO NEXT TRACK IN QUEUE",
            "/stop :- CLEAN QUEUE AND END STREAM",
            "/player :- GET INTERACTIVE PLAYER PANEL",
            "/end :- END THE STREAM",
            "/queue :- SHOW QUEUED TRACKS LIST"
        ]
    },
    "license": {
        "title": "LICENSE COMMAND",
        "description": "USER AUTHORIZATION SYSTEM",
        "commands": [
            "/auth user_id :- ADD USER TO AUTH LIST",
            "/unauth user_id :- REMOVE USER FROM AUTH LIST",
            "/authusers :- SHOWS LIST OF AUTH USERS"
        ]
    },
    "broadcast": {
        "title": "BROADCAST COMMAND",
        "description": "MESSAGE BROADCASTING SYSTEM",
        "commands": [
            "/broadcast text :- BROADCAST TO ALL CHATS",
            "/broadcast -pin :- PIN BROADCASTED MESSAGES",
            "/broadcast -pinloud :- PIN WITH NOTIFICATION",
            "/broadcast -user :- BROADCAST TO USERS",
            "/broadcast -assistant :- BROADCAST FROM ASSISTANT",
            "/broadcast -nobot :- FORCE BOT TO NOT BROADCAST"
        ]
    },
    "block": {
        "title": "BLOCK COMMAND",
        "description": "USER BLOCKING SYSTEM",
        "commands": [
            "/block username :- BLOCK USER FROM BOT",
            "/unblock username :- UNBLOCK USER",
            "/blockedusers :- SHOWS BLOCKED USERS LIST"
        ]
    },
    "blacklist": {
        "title": "BLACKLIST COMMAND",
        "description": "CHAT BLACKLIST SYSTEM",
        "commands": [
            "/blacklistchat chat_id :- BLACKLIST CHAT",
            "/whitelistchat chat_id :- WHITELIST CHAT",
            "/blacklistedchat :- SHOWS BLACKLISTED CHATS"
        ]
    },
    "channel": {
        "title": "CHANNEL-PLAY COMMAND",
        "description": "CHANNEL STREAMING CONTROLS",
        "commands": [
            "/cplay :- STREAM AUDIO IN CHANNEL",
            "/cvplay :- STREAM VIDEO IN CHANNEL",
            "/cplayforce :- FORCE PLAY NEW TRACK",
            "/channelplay :- CONNECT CHANNEL TO GROUP"
        ]
    },
    "speed": {
        "title": "SPEEDTEST COMMAND",
        "description": "PLAYBACK SPEED CONTROLS",
        "commands": [
            "/speed :- ADJUST PLAYBACK SPEED IN GROUP",
            "/cSpeed :- ADJUST SPEED IN CHANNEL"
        ]
    },
    "song": {
        "title": "SONG COMMAND",
        "description": "TRACK DOWNLOAD SYSTEM",
        "commands": [
            "/song url/name :- DOWNLOAD TRACK FROM YOUTUBE"
        ]
    },
    "seek": {
        "title": "SEEK COMMAND",
        "description": "PLAYBACK POSITION CONTROL",
        "commands": [
            "/seek time-dur :- SEEK TO POSITION",
            "/seekback time-dur :- SEEK BACKWARDS"
        ]
    },
    "shuffle": {
        "title": "SHUFFLE COMMANDS",
        "description": "QUEUE MANAGEMENT",
        "commands": [
            "/shuffle :- SHUFFLE THE QUEUE",
            "/queue :- SHOW SHUFFLED QUEUE"
        ]
    },
    "vplay": {
        "title": "VPLAY COMMAND",
        "description": "VIDEO STREAMING CONTROLS",
        "commands": [
            "/vplay :- START VIDEO STREAM",
            "/vplayforce :- FORCE NEW VIDEO STREAM"
        ]
    },
    "ping": {
        "title": "PING COMMAND",
        "description": "BOT STATUS SYSTEM",
        "commands": [
            "/ping :- SHOW BOT PING AND STATS",
            "/stats :- SHOW BOT STATISTICS",
            "/uptime :- SHOW BOT UPTIME"
        ]
    },
    "revamp": {
        "title": "REVAMP COMMAND",
        "description": "BOT MAINTENANCE CONTROLS",
        "commands": [
            "/logs :- GET BOT LOGS",
            "/logger :- TOGGLE ACTIVITY LOGGING",
            "/maintenance :- TOGGLE MAINTENANCE MODE"
        ]
    },
    "spiral": {
        "title": "SPIRAL COMMAND",
        "description": "LOOPING CONTROLS",
        "commands": [
            "/loop enable/disable :- TOGGLE LOOP",
            "/loop 1/2/3 :- SET LOOP COUNT"
        ]
    },
    "gbans": {
        "title": "G-BANS COMMAND",
        "description": "GLOBAL BAN SYSTEM",
        "commands": [
            "/gban user_id :- GLOBALLY BAN USER",
            "/ungban user_id :- REMOVE GLOBAL BAN",
            "/gbannedusers :- SHOW GLOBALLY BANNED USERS"
        ]
    },
    "troubleshoot": {
        "title": "TROUBLESHOOT COMMANDS",
        "description": "SELF-REPAIR SYSTEM",
        "commands": [
            "/fixbot :- REPAIR COMMON ISSUES",
            "/diagnose :- CHECK BOT HEALTH",
            "/fixproblem :- (ADMIN ONLY) REMOTE REPAIRS"
        ]
    },
    "settings": {
        "title": "SETTINGS COMMAND",
        "description": "USER PREFERENCES SYSTEM",
        "commands": [
            "/settings :- SHOW SETTINGS PANEL",
            "/settings volume [1-200] :- SET PLAYBACK VOLUME",
            "/settings quality [low|medium|high] :- SET STREAM QUALITY",
            "/settings language [en|hi|etc] :- SET BOT LANGUAGE",
            "/settings notifications [on|off] :- TOGGLE NOTIFICATIONS"
        ]
    },
    "radio": {
        "title": "RADIO COMMAND",
        "description": "GLOBAL FM RADIO SYSTEM",
        "commands": [
            "/radio search [query] :- SEARCH RADIO STATIONS",
            "/radio play [ID] :- PLAY RADIO STATION",
            "/radio stop :- STOP RADIO PLAYBACK",
            "/radio list :- SHOW POPULAR STATIONS"
        ]
    }
}