# Placeholder

Add here your:
- webhook.ini - telegram web-server address, port
- database.ini - database connection configuration,
example:
```ini
[postgresql]
host=localhost
database=user
user=user
password=user
```
- token.txt - telegram bot secret token received from Bot Father
- tg_private.key - SSL private key TLS1.2(+) 
- tg_public.pem - SSL public key TLS1.2(+) 

### How to get SSL keys

Generate self-signed cerificate using openssl v1.1.1+:
- https://core.telegram.org/bots/self-signed
	