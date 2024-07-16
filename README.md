# General
This bot helps you to manage your schedule.
Bot is based on the aiogram python package using webhooks.

# Bot demo:

https://t.me/andrew_notifications_bot

# How to set up:

1. Set up Python environment v3.10+, activate the environment, install all the packages from the requirements.txt
2. Get a bot token from Bot father, put it into the token.txt file near the source files (create a Telegram bot)
3. Set up firewall to pass your bot IP
4. Generate SSL keys with the command ```openssl req -newkey rsa:2048 -sha256 -nodes -keyout tg_private.key -x509 -days 1000 -out tg_public.pem -subj "/C=AT/ST=Linz/CN=HOSTNAME"```, where HOSTNAME is your server's IP or domain name.
5. Create a PostgreSQL DB named "user". 
Example: https://www.hostinger.com/tutorials/how-to-install-postgresql-on-centos-7/
6. Create DB tables executing query from the ddl.sql in DB command promt.
7. Change your IP and Port in config/webhook.txt.
8. run server with ```python main.py```