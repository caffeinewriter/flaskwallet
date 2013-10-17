Todo
====

Before the next release
-----------------------

- bitcoin-python abstraction layer to catch all connection errors
- CSRF, http://wtforms.simplecodes.com/docs/1.0.2/ext.html#module-wtforms.ext.csrf
- Make __DEFAULT_ACCOUNT__ string configurable.

..
    getnewaddress foo; getaddressesbyaccount foo returns one; getaccountaddress foo
    returns a new one. i would have expected getaccountaddress foo to return the
    first address so it's confusing if i add a wallet and each new account ends
    up with two addresses in it.. or old ones with only one have two. i could ofc
    code around the getaccountaddress behavior by not using it, but still..

    <@gmaxwell> nkuttler: you're not supposted to reuse addresses. Generally the api
    is setup so that you don't.

    So... hide the addresses? What's the sensible approach here?

Roadmap
-------

This is a list of things I'm intereseted in doing:

- Verifying messages
- OTP before sending coins
- Confirm amount when sending coins
- Namecoin support

  - http://dot-bit.org/Namespace:Domain_names_v2.0
  - https://github.com/vinced/namecoin/blob/master/README.md
  - http://dot-bit.org/HowToRegisterAndConfigureBitDomains
- Move all coins from many accounts into one in one step
- Address book
- When sending payment, save comment-to as new 'contact'
- Bookmark for addresses used to sign
- When creating a new address, attach a note to it
- The API doesn't seem to order transactions in a useful way. Mirror
  them to the db? Keep track of local transactions?
- Quickjump nav between wallets
- Maybe enable different functionalities for different coins
- Add edit/delete/stop buttons to wallet detail view
