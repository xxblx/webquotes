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
* mandatory parameters: text
* optional parameters: title and tag, tag can be used multiple times if you would like to set a few tags
* returns: json with quote_id

### Rate quote
* uri: /api/quotes/rate
* method: POST
* mandatory parameters: quote_id and action ('up' or 'down')

### Get quotes
* uri: /api/quotes/get
* method: GET
* optional parameters:
    * quote_id - request one quote with given quote_id, if quote_id is used other parameters are ignored
    * tag_id - request quotes with given tag_id 
    * offset - request quotes not from the beginning, start from `offset` row (default: 0)
    * num - how many quotes request (0-500, default: 100)
* json with quotes like
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
* returns: json with one quote

## License
WebQuotes is free and opensource software, it is licensed under GNU GPL 3 (or newer) license. Check LICENSE for details.
