# sanic-oauth2
> An oauth2 server implementation with [sanic](https://github.com/channelcat/sanic).
> The development sees <https://www.oauth.com/> as a guideline to ensure that all the API's stick to the protocol.


## Tasks
> job break down for the server. they are not listed in order.

### application related API's
* create ✔
* get ✔
* delete ✔
* reset client_secret ✔


### user registration API's
* create ✔
* update password ✔


### access token

>I will be doing introspection for token verification.

* access token generation ✔️

    *a very long nonce string shall be sufficient.*
 
 
* handlers for grant types
    * password ✔️
    * client credentials ✔️
    * authorization code
    * implicit
    * refresh token ✔️
    
 
* token introspection ✔️
