# Gyre


<blockquote><i>
Turning and turning in the widening gyre   
<br/>The falcon cannot hear the falconer;
<br/>Things fall apart; the centre cannot hold;
<br/>Mere anarchy is loosed upon the world,
</i></blockquote>

Gyre is a free social network. Not 'free as in beer', like every other social network, but 'free as in freedom': it is predicated on anti-capitalist and anti-racist principles of social and spiritual freedom.


## Features

### Your traffic is untraceable

All traffic is routed via Tor. You can't be surveilled by cops or monetized by capital. 

### Be as anonymous as you wish

Design a profile and account which is as anonymous as you want to make it. If you don't reveal yourself, your traffic or behavior elsewhere on the internet won't either.

### Best of what's out there

We present a simplified set of social media features drawn from everything that's out there and then some:

* Profile
  * Curate a profile with photo and posts (e.g. Twitter)
  * Show profile to world (e.g. Twitter)
  * Show profile only to friends (e.g. Facebook)
  * Show profile only to your local area (e.g. Nextdoor)

* Posting 
  * Post to the entire world (e.g. Twitter)
  * Post to your friends (e.g. Facebook)
  * Post to your surrounding area by a distance radius (e.g. Nextdoor)
  * Anonymously up-vote or down-vote posts (e.g. Reddit)
  * Post anonymously or from your account (new from Gyre)

* Organizing
  * Host events and invite others (e.g. Facebook)
  * Host events like protests anonymously (new from Gyre)

* Messaging
  * Message securely with encrypted contents (e.g. Signal)
  * Message securely with untraceable metadata (new from Gyre)


### Open-source and community run

Not just non-profit, we're anti-profit.

## Design

Design details are changing rapidly, but these are what we have so far.

### App

The 'client' or app is made with [KivyMD](https://github.com/kivymd/KivyMD), a variant of [Kivy](https://kivy.org/), a cross-platform mobile development framework in Python. Python is an easy and versatile progamming language to learn, which keeps the code accessible to as many people as possible.

### Server

The server also runs on Python, serving a graph database powered by [Neo4j](https://neo4j.com/).