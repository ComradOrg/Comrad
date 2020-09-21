*Please help edit this! I may be wrong about some of it:*

## Comparison of their designs

| Other cool thing                              | What is it?       | Kind of like...    | Decentralized? (P2P?)          | Anonymous? (IP address undiscoverable?)       | Confidential? (100% E2E encrypted?)         | Data robustness?                   | Identity verification?                | Need invitation/server?          | What data can user find?                  |
| --------------------------------------------- | ----------------- | ------------------ | ------------------------------ | --------------------------------------------- | ------------------------------------------- | ----------------------------------- | ------------------------------------- | -------------------------------- | ----------------------------------------- |
| *[Komrade](http://komrade.app)*               | *Social network*  | *Twitter*          | ❌ *No (central server on Tor)* | ✔️ *Yes (everything routed via Tor)*           | ✔️ *Yes (100% E2EE)*                         | *Minimal server (deleted ASAP)*     | *Yes (central public key repository)* | ***No (works like twitter)***    | Mixed (global feed; hashtag search only)  |
| [Secure Scuttlebutt](https://scuttlebutt.nz/) | Social network    | Twitter / Facebook | ✔️ Fully (P2P)                  | ❌ No (P2P reveals IP; friend networks public) | ⭕ Partly (private E2EE, public unencrypted) | Distributed across friend networks? | Yes? (federated key exchange?)        | Yes (need initial pub)           | Limited (search friends-of-friends' data) |
| [Diaspora](https://diasporafoundation.org/)   | Social network    | Twitter            | ⭕ Halfway (federated)          | ⭕ No (unless via Tor Browser)                 | ❌ No (unencrypted?)                         | ?                                   | ?                                     | Yes (need 'pod' server)          |                                           |
| [Mastodon](https://joinmastodon.org/)         | Social network    | Twitter            | ⭕ Halfway (federated)          | ⭕ No (unless via Tor Browser)                 | ❌ No (unencrypted?)                         | ?                                   | ?                                     | Yes (need 'instance' server)     |                                           |
| [Matrix](https://matrix.org/)                 | Co-working space  | Slack              | ⭕ Halfway (federated)          | ❌ No?                                         | ✔️ Yes? (100% E2EE)                          | ?                                   | Yes (?)                               | Yes (invited channels only?)     |                                           |
| [Briar Messenger](https://briarproject.org/)  | Messenger         | WhatsApp           | ✔️ Fully (P2P)                  | ✔️ Yes? (Tor)                                  | ✔️ Yes (100% E2EE)                           | None (needs 24/7 listener)          | Partly (public keys traded IRL)       | Yes (need initial contact?)      |                                           |
| [Cabal Chat](https://cabal.chat/)             | Private chatrooms | IRC                | ✔️ Fully (P2P)                  | ❌ No (P2P reveals IP) <sup>1</sup>            | ⭕ Mostly (shared key, not E2EE)             | Distributed Hash Table              | No (?)                                | Not really (public chat is open) |                                           |
| [Signal](https://signal.org/)                 | Messenger         | WhatsApp           | ❌ No?                          | ❌ No                                          | ✔️ Yes (E2EE, and audited)                   | ?                                   | ?                                     | No                               | Only what they send or are sent           |


Sources:

<sup>1.</sup> [Cabal FAQ: What kind of security is involved with Cabal?](https://cabal.chat/faq.html#:~:text=What%20kind%20of%20security%20does,is%20involved%20in%20a%20cabal)

## Comparison of their features


| Other cool thing                              | DM users (E2EE) | Group chat (E2EE) | Post to world | Post to friends/ties | Symmetric ties ('friends') | Asymmetric ties ('followers) | Like posts | Repost posts | Feed of all posts | Feed of people you follow |
| --------------------------------------------- | --------------- | ----------------- | ------------- | -------------------- | -------------------------- | ---------------------------- | ---------- | ------------ | ----------------- | ------------------------- |
| *[Komrade](http://komrade.app)*               | ✔️               | ❌?                | ✔️             | ✔️                    | ✔️                          | ✔️                            | ✔️?         | ❌            | ✔️                 | ✔️                         |
| [Secure Scuttlebutt](https://scuttlebutt.nz/) | ✔️               | ❌?                | ❌             | ✔️                    | ✔️                          | ✔️                            | ✔️          | ❌?           | ❌                 | ✔️                         |
| [Diaspora](https://diasporafoundation.org/)   | ❌?              | ❌?                | ❌?            | ✔️                    | ❌                          | ✔️                            | ✔️          | ✔️?           | ❌                 | ✔️                         |
| [Mastodon](https://joinmastodon.org/)         | ❌?              | ❌?                | ❌?            | ✔️                    | ❌                          | ✔️                            | ✔️          | ✔️?           | ❌                 | ✔️                         |
| [Matrix](https://matrix.org/)                 | ✔️               | ✔️                 | ❌?            | ✔️                    | ✔️                          | ❌                            | ❌?         | ❌?           | ❌?                | ❌?                        |
| [Briar Messenger](https://briarproject.org/)  | ✔️               | ✔️                 | ❌?            | ✔️                    | ✔️                          | ❌                            | ❌?         | ❌?           | ❌?                | ❌?                        |
| [Cabal Chat](https://cabal.chat/)             | ?               | ✔️                 | ❌?            | ✔️                    | ❌                          | ❌                            | ❌          | ❌            | ❌                 | ❌                         |
| [Signal](https://signal.org/)                 | ✔️               | ✔️                 | ❌             | ❌                    | ✔️                          | ❌                            | ❌          | ❌            | ❌                 | ❌                         |


