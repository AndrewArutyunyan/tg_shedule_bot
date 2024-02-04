# General
This bot helps you to manage your schedule.
Set new assignment and specify time, day of the week and a description with the command: **schedule [time] [day of the week] [description]**.
Time should be in the ISO format HH:mm.
    Example: ```schedule 14:00 Tuesday English lesson```.

Set one-time event with the command: **once [datatime] [description]** in the ISO format yyyy-MM-dd HH:mm.
    Example: ```once 2024-02-10 18:30 Doctor appointment```.

Remove a planned one-time or periodic event by specifing its description or id with the command **remove [description/id]**.
Id lookup table could be fetched by **list** command.
    Examples: ```remove English lesson```, ```remove 843099249```

Disable one eventfrom a serie by specifing its description AND datetime with the command **disable [description] [datetime]**.
    Examples: ```disable English lesson 2024-02-10 18:30```.

List all planned tasks with the command **list**.

List today's planned tasks with the command **today**.

Bot is based on the aiogram python package using webhooks.
# Bot demo:

https://t.me/andrew_notifications_bot

# How to set up:

1. Set Python environment, setup all the packages from requirements.txt
2. Get a bot token from Bot father, put it into the token.txt file near the source files
3. Generate SSL keys with the command ```openssl req -newkey rsa:2048 -sha256 -nodes -keyout tg_private.key -x509 -days 1000 -out tg_public.pem -subj "/C=AT/ST=Linz/CN=HOSTNAME"```, where HOSTNAME is your server's IP or domain name.
3. Change webhooks server parameters inside the shedule_bot.py code.
4. run server with ```python shedule_bot.py```