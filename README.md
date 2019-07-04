# sanauth
> An oauth2 server implementation with [sanic](https://github.com/channelcat/sanic).
> The development sees <https://www.oauth.com/> as a guideline to ensure that all the API's stick to the protocol.

## Some Thoughts
> as I kept adding API's to the project, I started asking one ultimate question. 
what shall be the boundary of this project? 
So I want to list some ultimate goals here and make sure the project will end there.
* features
    * application CRUD
        * including disabling and re-enabling an app
        * via both *web API* and *function calling* 
    * user CRUD
        * including disabling and re-enabling an user account
        * via both *web API* and *function calling* 
    * access token granting and invalidating
* availability
    * developers shall be able to use the program as a drop in extension for their own sanic project.
    * the program shall also be able to run as a standalone service app.
    * developers shall be able to install this program via pypi


## Tasks
> job break down for the server. they are not listed in order.

### application related API's
* [x] create
* [x] get
* [x] delete
* [x] reset client_secret


### user registration API's
* [x] create
* [x] update password


### access token

>I will be doing introspection for token verification.

* [x] access token generation

    *a very long nonce string shall be sufficient.*
 
 
* [ ] handlers for grant types
    * [x] password
    * [x] client credentials
    * [ ] authorization code
    * [ ] ~~implicit~~ *dropped*
    * [x] refresh token
    
 
* [x] token introspection
