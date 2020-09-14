# Komrade

Komrade is a socialist network. It seizes the means of digital production.

## Why another social network?

Is a 'socialist network' possible? Although the internet began with anarchic design principles, it quickly consolidated into the hands of a few of the largest corporations in the world. It has effectively recreated the capitalist mode of production within itself: the means of content production (social media platforms) are privatized while the work of production (posting) remains socially distributed. Exploitation inheres in that relation, whether in the industrial factory or the digital platform, because the value you produce is taken from you, concentrated and privatized.

But a digital network can be redesigned. The technology behind these social media platforms is actually quite simple. We can easily build our own social network, one which is secure, insurveillable, and unmonetizable—one which would give people the security they need to communicate about whatever they want, including protesting against capital and the state..

## Core principles

### Illegible

All of your data are strongly encrypted end-to-end: only you and those you write to can decrypt and read it. To anyone without the right decryption 'key', the data is nonsense.

### Untraceable

All network traffic is routed through Tor, a "deep web" of computers so dense even the FBI can't follow you through it. Komrade's "Operator" or central server is accessible only from Tor. It's impossible to tell who is sending what to whom, or even who is using the app at all.

### Unmonetizable

What's untraceable is also unmonetizable: your data can't be harvested by technology companies and used for advertising algorithms. You're protected from both surveillance capitalism and the surveillance state.

### Democratized

Group accounts or 'collectives', like @portland or @socialists, grow as existing members 'vouch for' new ones, forming webs of trust. Other komrades can see how many times a given person has been vouched for, both within a group and overall, but not who has vouched for them. In order to join a group, at least one member must vouch for you; this minimum (or 'quorum') may grow as the group grows.

### (Semi-)decentralized

Data is deleted as soon as possible from Komrade. Komrade's "Operator" simply sorts and holds the mail temporarily: as soon as users log in to download their mail, the messages are deleted from the server and network forever.

### Anti-profit

Not just non-profit, we're anti-profit.

### Open-source

Information wants to be communist.

## Social media features

We present a simplified set of social media features drawn from everything that's out there:

#### Profile
  * Curate a profile with photo and posts (e.g. Twitter)
  * Show profile to world (e.g. Twitter)
  * Show profile only to those you trust (e.g. Facebook)
  * Show profile only to your local area (e.g. Nextdoor)

#### Posting
  * Post up to 1 image and/or 1000 characters
  * Post to the entire world (e.g. Twitter)
  * Post to those you trust (e.g. Facebook)
  * Post to your surrounding area by a distance radius (e.g. Nextdoor)
  * Anonymously up-vote or down-vote posts (e.g. Reddit)
  * Post anonymously or from your account

#### Organizing
  * Host events and invite others (e.g. Facebook)
  * Host events like protests anonymously (new)
  * Anonymously pin on a map sites of danger, like police (e.g. Waze)

#### Messaging
  * Message securely with encrypted contents (e.g. Signal)
  * Message securely with untraceable metadata (new)


## Progress

### Preview animation

As of the 23rd of August.

<img src="komrade/app/assets/komrade-screen-preview-2020-08-23.gif" height="600" alt="GIF animation" />

### Backend preview

See [here](https://www.dropbox.com/s/8r8gqgfswojmtwd/komrade-terminal-preview--2020-09-13.mkv?dl=0).




## Usage

### Install

In one line (via [this auto-installer script](https://github.com/Komrade/Komrade/blob/master/script/install)):

```
bash <(curl -s https://raw.githubusercontent.com/Komrade/Komrade/master/script/install)
```

This will install a virtual environment for running Komrade on your computer, complete with the correct version of Python, and without overriding your existing Python configuration.

### Run

Install as above.

For the terminal client, run:

```
komrade-cli
```

For the mobile/desktop app, run:

```
komrade-app
```

Or to run the server or Operator (for development only):

```
komrade-op
```


## Details

### Frontend

#### Mobile/desktop

The mobile/desktop app is made with [KivyMD](https://github.com/kivymd/KivyMD), a variant of [Kivy](https://kivy.org/), a cross-platform app development framework in Python. Python is an easy and versatile progamming language to learn, which keeps the code accessible to as many people as possible. Code for the app is in [komrade/app](komrade/app).

#### Terminal app

Vanilla Python. Code is in [komrade/cli](komrade/cli).

### Backend

#### Ontology

All plain object-oriented stuff in Python. The root entity is a "Keymaker": anyone from @Telephone, to @Operator, to users, to groups, who has a public/private key pair. The database uses a simple file-based key-value store, written in Python ([simplekv](https://github.com/mbr/simplekv)). Code is in [komrade/backend](komrade/backend).

#### Cryptography

We are using [Themis](https://github.com/cossacklabs/themis), a high-level cross-platform cryptography library, for all cryptographic functions, rather than handling any primitives ourselves.

Code is primarily in:
* [komrade/backend/keymaker.py](komrade/backend/keymaker.py)
* [komrade/backend/komrades.py](komrade/backend/komrades.py)
* [komrade/backend/phonelines.py](komrade/backend/phonelines.py)

