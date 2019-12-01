# WebQuotes

WebQuotes is a simple web application for quotes posting designed for personal usage. 

## Features
* Simple frontend without modern javascript-powered ui
* Random quote, tags, ranking system
* Telegram notifications about new quotes
* Handler for telegram bot based on webhooks for rating quotes, getting random quotes, saving messages as quotes from telegram chat via bot's commands
* API with token-based auth 
* [Python](https://www.python.org/) and [Tornado](http://www.tornadoweb.org), [PostgreSQL](https://www.postgresql.org) and [aiopg](https://github.com/aio-libs/aiopg), [janus](https://github.com/aio-libs/janus), [pynacl](https://github.com/pyca/pynacl)

## TODO
* ~~API: add quotes, get a random quote, etc~~
* Notifications 
    * ~~Telegram~~
    * Web notifications (websockets + small notification block with suggestion to reload a page)
* Search

## Telegram Bot
Enter valid `bot_id`, `chat_id` and `bot_username` (telegram username) to `TG_BOT` dict (in conf.py) and set the value of `enabled` key to `True`. 
Keep the value of `url_token` in secret, url `https://example.com/tgbot/some_secret_token` will be registered as a webhook address, e.g. for getting POST requests with updates for the bot from Telegram. See more information about webhooks in [Telegram guide to Webhooks](https://core.telegram.org/bots/webhooks).

### Commands 
* `/help` - show help
* `/random` - get random quote
* `/get` - get quotes with given ids
    * examples
    * `/get 1`
    * `/get 2 8`
* `/top` - get three top rated quotes
    * `/top N` - get N top rated quotes, where 1 <= N <= 10
    * e.g. `/top 5`
* `/like` - rank up quote (use in reply messages)
* `/dislike` - rank down quote (use in reply messages)
* `/save` - save a message as a new quote (use in reply messages)
  * add tags via hashtags, e.g. `/save #tag1 #tag2 #tag3`

## API
Generally for sending API requests you have to provide valid and unexpired select_token and verify_token as request parameters. 

You can get first set of tokens with username and password and then request reissuing of new set with renew_token.

* select_token is used in select queries in db.
* verify_token is used for verification of selecting and renewing tokens. The verify_token isn't stored directly in db. Instead of that a hash of the token stored (blake2b). In case of unexpected read access to db (e.g. theft of db dump, injection, etc) plain verify_token isn't going to be compromised, it makes all stolen tokens useless because only the app knows the mac key used for hashing and the app always hashes the content of incoming verify_token parameter on post request.
* renew_token is used for one-time issuing new tokens. Since renew_token has been used all connected tokens are going to be deleted from db. 

### Get tokens
* uri: /api/tokens/get
* method: POST
* mandatory parameters: username and password
* returns: json with three tokens: select_token, verify_token and renew_token 

### Renew tokens 
* uri: /api/tokens/renew
* method: POST
* mandatory parameters: verify_token and renew_token
* returns: json with three tokens: select_token, verify_token and renew_token 

### Add quote
* uri: /api/quotes/add
* method: POST
* mandatory parameters: select_token, verify_token and text
* optional parameters: title and tag, tag can be used multiple times if you would like to set a few tags
* returns: json with quote_id

### Rate quote
* uri: /api/quotes/rate
* method: POST
* mandatory parameters: select_token, verify_token, quote_id and action ('up' or 'down')

### Get quotes
* uri: /api/quotes/get
* method: GET
* mandatory parameters: select_token and verify_token
* optional parameters:
    * quote_id - request one quote with given quote_id, if quote_id is used other parameters are ignored
    * tag_id - request quotes with given tag_id 
    * offset - request quotes not from the beginning, start from `offset` row (default: 0)
    * num - how many quotes request (0-500, default: 100)
* json data with quotes is reverse-ordered by datetime (the latest at the beginning). It means `offset` allows to request old quotes if more than 500 have been added.

```json
{
  "data": [
    {
      "quote_id": 53, 
      "quote_title": "i_am_a_title", 
      "quote": "some_quote", 
      "datetime": 1553180910, 
      "quote_tags": [
        {
          "quote_id": 53, 
          "tag_id": 19, 
          "tag_name": "test"
        }, 
        {
          "quote_id": 53, 
          "tag_id": 20, 
          "tag_name": "api"
        }
      ], 
      "quote_rating": 0
    }
  ], 
  "count": 1
}
```
    
### Get random quote
* uri: /api/quotes/random
* method: GET
* mandatory parameters: select_token and verify_token
* returns: json with one quote

### Get top rated quotes
* uri: /api/quotes/top
* method: GET
* mandatory parameters: select_token and verify_token
* optional parameters:
    * offset - request quotes not from the beginning, start from `offset` row (default: 0)
    * num - how many quotes request (0-500, default: 100)
* json data with quotes is reverse-ordered by rating (top rated ones at the beginning)

### Get tags
* uri: /api/tags/get
* method: GET
* mandatory parameters: select_token and verify_token
* optional parameters:
    * offset - request tags not from the beginning, start from `offset` row (default: 0)
    * num - how many tags request (0-500, default: 100)
* json data with tags is reverse-ordered by quotes count (most used tags at the beginning). It means `offset` allows to request less popular tags if more than 500 have been added. 

```json
{
  "data": [
    {
      "tag_id": 19,
      "tag_name": "test",
      "quotes_count": 5
    }, 
    {
      "tag_id": 20, 
      "tag_name": "api", 
      "quotes_count": 2
    }
  ], 
  "count": 2
}
```

## License
WebQuotes is free and opensource software, it is licensed under GNU GPL 3 (or newer) license. Check LICENSE for details.
