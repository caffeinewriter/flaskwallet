====================
Flask Bitcoin Wallet
====================

Introduction
============

Flaskwallet a multi-node bitcoin client, a web app written with
flask_ . If you know how to use python and how to run a ``bitcoind`` you can
probably use it. Alternatively you can also run ``bitcoin-qt`` with the
``-server`` option. Flaskwallet is not a thin client, you need to run bitcoin
nodes to manage them through the RPC API.

You can also connect to many altcoin daemons. I have use this app to manage
a dozen or so different crypto currencies. See the caveats_ section though.

.. _flask: http://flask.pocoo.org/

Features
--------

- Manage multiple crypto currencies and nodes/wallets
- Sign messages
- Responsive, mobile-friendly, though you'll want to use a tablet to manage your
  coins from the couch
- Optional OTP for wallet decryption, using Google Authenticator (or
  alternatives)
- Use different accounts per wallet
- Send coins from specific accounts
- Move coins from account to account

One important note though: The account features don't mean that you can send
coins received from a specific account in a transaction. They are purely an
internal organizational tool for yourself and don't allow separating streams of
coins. You need multiple bitcoin nodes to do that.

.. _caveats:

Caveats
-------

1. I haven't tested encrypted RPC API connections. Please let me know if this
   works/doesn't work for you.
2. The flask development server uses HTTP, so the app's communication with your
   browser is not encrypted. As the app needs to sends the real wallet
   passphrase to the node and not a hash it could be intercepted. This shouldn't
   be an issue though, as flaskwallet only listens to localhost by default. If
   you change this setting securing your network is up to you.
3. All the app does is to send the data you enter to the ``bitcoind`` API. No input
   sanitization happens at all, and just minor validation.
4. There is no CSRF protection yet.
5. Due to the ``bitcoind`` behavior this app will create a second address for
   accounts with only one address in some circumstances. This shouldn't really
   matter, but you should be aware of it.
6. I didn't think about catching connection errors, except for the root view.
   I'll probably add an abstraction layer in the future. This can be a little
   annoying when using altcoins that don't implement some ``bitcoind`` features.
7. The default account is called ``""`` internally. As this leads to various
   problems it is displayed as ``__DEFAULT_ACCOUNT__``.
8. Oh right, I did zero testing in Internet Explorer.
9. Oh right, no python3 yet either, but I'll gladly accept patches.

Installation
============

Get the source::

    $ mkdir flaskwallet
    $ cd flaskwallet
    $ git clone ***

Create a virtualenv and activate it::

    $ virtualenv --system-site-packages virtualenv
    $ . virtualenv/bin/activate

You don't have to use virtualenv, but I highly recommend it. To install it on
Debian and Debian-based systems like Ubuntu use::

    $ sudo apt-get install python-virtualenv

Dependencies
------------

Install the requirements inside your virtualenv. From the source tree run::

    $ cd flaskwallet
    $ pip install -r doc/requirements.txt

This installs `bitcoin-python` from my own github repo, but you can also use the
upstream master branch. Some features aren't supported upstream though (in 3.0
at least). I am currently working on getting new code into the upstream release.

You will also need PIL/Pillow to if you wish to generate QR codes for OTP
authentication. I didn't include it as requirement because I prefer to use
system packages for big libraries::

    $ sudo apt-get install python-imaging python-docutils

The time on your boxes should be correct. OTP and displaying time deltas depends
on this. So on every computer that runs a node or flaskwallet you should::

    $ sudo apt-get install ntp

Configuration
-------------

Start by copying the configuration template::

    $ cp config_template.py config.py

Edit ``config.py`` and change the ``SECRET_KEY`` to a random string of
length 16, 24, or 32. This will be used to encrypt and decrypt various sensitive
information in the database. This feature will not greatly enhance security, but
at least the database itself won't reveal the API passwords or your OTP secret.
An attacker would need to get access to your database and the ``SECRET_KEY``.

To generate a passphrase you can use one of the examples below::

    $ openssl rand -base64 32 | head -c 32; echo
    $ date +%s | sha256sum | base64 | head -c 32; echo

Note that the app never saves your wallet passphrase. So even if somebody
manages to get hold of your app's secret key, the database and your OTP secret
(if you enable OTP) they can't do anything with your coins as they can't
decrypt the wallet. You did encrypt your wallet, didn't you?

First run
---------

After the configuration you can start the development server with::

    $ python main.py

That's all, now you can visit the app at http://localhost:8000. Happy
testing.

If you want to deploy this properly, ``flaskwallet.main:app`` is a WSGI
object. However, the code is in alpha, there is no "proper" way to deploy
this, and the wallet is only intended for personal use anyway, even if it's a
web app.

Usage
=====

You should start by adding a few nodes, using the ``Add new wallet`` button.
You have to provide a label and the connection info. If you don't know what to
put in here this app probably isn't for you. You are running a ``bitcoind``, aren't
you?

I hope the rest is self-explanatory. One note though: there are two *Send
coins* buttons, one on the wallet page and one on each account page. The former
sends from the wallet, the latter from specific accounts. This means you can
send coins that were received with addresses that belong to the account.

Configuring your nodes
----------------------

Flaskwallet uses the ``bitcoind`` RPC API, so it has to have access. You
probably already have a configuration file for each node. If not, a good one
to start with looks like::

    rpcuser=<username>
    rpcpassword=<password>
    rpcallowip=<optional, IP of the flaskwallet server>

You don't need the `rpcallowip` parameter if the node runs on localhost. Also
keep in mind to open the right ports in any firewalls on the way.

Feedback
========

I am interested in hearing from anybody who uses flaskwallet. Please let me know
what you like or dislike. However, it's a personal project right now that does
pretty much everything I want it to do, so don't expect miracles.

If you would like to support further development there are donation addresses
below. If you need something specific added you can contact_ me, I am available
for hire.

.. _contact: http://kuttler.eu/contact/

You probably got the flaskwallet source from github.
If you know github you probably know that there are also other ways to
contribute than with coins ;-)

Donations
---------

- Bitcoin ``1NG8BfDzequeiCDewn7v2AF4FcBKGxzKkH``
- Namecoin ``NDMMAbbyFZKNNkjg67Ev1AmbPmgw8FsqyB``
- Litecoin ``LZeWjWFFM2HxzM8zdGxagK8AT6E6gen7RG``
- Primecoin ``ASLHExCmrtCBWraMSiLif5oo8HHmMiaHJV``
- Novacoin ``4WktQAejCWcGKWRvoZSyveFq2rkbkH6VWo``
- Feathercoin ``6uWPpv9zebZbFzPGmSEx4f6S55S9JS7ag4``
- PPCoin ``PREaH4xoWUnbryevJmTuoZDUDEnoMW6GV9``

Suggest more altcoins and I'll add them to this list, and see if my wallet can
handle them.

Development
===========

Great that you're interested in the code. Just start by reading it, and see
``doc/Todo.rst``. There isn't much documentation in the code as everything is
very obvious (I think). Views have descriptive names, etc. If in doubt the test
code might give you a few hints at what's going on.

I'd like to point out that this is my first non-trivial flask app and that I'm
very open to refactoring if I chose some bad development patterns on the way. Of
course, patches are welcome.

Testing
-------

Running the test code isn't straight forward but not too hard
either. The tests need nodes they can connect to and coins they can spend, so
the `testnet box <https://github.com/freewil/bitcoin-testnet-box>`__ is used. To
install it and set everything up for the test runs use::

    $ make boxstart
    $ # Give them enough time to launch
    $ make test
    $ # This is supposed to fail the first time. One wallet is encrypted
    $ # and the bitcoind stops after that.
    $ make boxstart

After this is completed you only need to do this to run the tests::

    $ make test

You can also generate and view coverage reports::

    $ make coverage
    $ firefox coverage/index.html

Finally, to stop the testnet box from running use::

    $ make boxstop

I'd integrate flaskwallet testing with travis-ci_,
but installing the testnet there all the time doesn't seem like such a great
idea.

.. _travis-ci: https://travis-ci.org/
