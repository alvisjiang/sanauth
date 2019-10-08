# sanauth

[![CircleCI](https://circleci.com/gh/alvisjiang/sanauth.svg?style=svg)](https://circleci.com/gh/alvisjiang/sanauth)
[![codecov](https://codecov.io/gh/alvisjiang/sanauth/branch/master/graph/badge.svg)](https://codecov.io/gh/alvisjiang/sanauth)

> An oauth2 server implementation with [sanic](https://github.com/channelcat/sanic).
> The development sees <https://www.oauth.com/> as a guideline to ensure that all the API's stick to the protocol.
>

* features
  * application CRUD
    * including disabling and re-enabling an app
      * via both *web API* and *function calling*
  * user CRUD
    * including disabling and re-enabling an user account
    * via both *web API* and *function calling*
  * access token granting, invalidating and retrospecting
* availability
  * developers shall be able to use the program as a drop in extension for their own sanic project.
  * the program shall be able to run as a standalone service app.
  * developers shall be able to install this program via pypi

## Tasks

> job break down for the server.

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

    *a very long nonce string shall be sufficient at this.*

* [ ] handlers for grant types
  * [x] password
  * [x] client credentials
  * [ ] authorization code
  * [ ] ~~implicit~~ *dropped*
  * [x] refresh token

* [x] token introspection

## Possible further plan

* add a layer for DB accessing. it'll allow developer to use which ever database they like.
  * default redis and postgres will be extracted to separate pypi package as extension.
* add more token generation solutions.
  * could also add a token generation/validation layer.
