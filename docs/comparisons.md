*Please help edit this! I may be wrong about some of it:*

## Comparison of their designs

| Other cool thing                              | What is it?       | Kind of like...    | Decentralized? (P2P?)          | Anonymous? (IP hidden?)                       | Confidential? (100% E2EE?)                  | Data robustness?                      | Identity verification?                  | Requires invitation/server?        |
| --------------------------------------------- | ----------------- | ------------------ | ------------------------------ | --------------------------------------------- | ------------------------------------------- | ------------------------------------- | --------------------------------------- | ---------------------------------- |
| *[Comrad](http://comrad.app)*               | *Social network*  | *Twitter*          | ❌ *No (central server on Tor)* | ✔️ *Yes (everything routed via Tor)*           | ✔️ *Yes (100% E2EE)*                         | ⭕ *Minimal server (deleted ASAP)*     | ✔️ *Yes (central public key repository)* | ✔️ *No (works like twitter)*        |
| [Secure Scuttlebutt](https://scuttlebutt.nz/) | Social network    | Twitter / Facebook | ✔️ Fully (P2P)                  | ❌ No (P2P reveals IP; friend networks public) | ⭕ Partly (private E2EE, public unencrypted) | ✔️ Distributed across friend networks? | ✔️ Yes? (federated key exchange?)        | ❌ Yes (need initial pub)           |
| [Diaspora](https://diasporafoundation.org/)   | Social network    | Twitter            | ⭕ Halfway (federated)          | ⭕ No (unless via Tor Browser)                 | ❌ No (unencrypted?)                         | ✔️                                     | ?                                       | ❌ Yes (need 'pod' server)          |
| [Mastodon](https://joinmastodon.org/)         | Social network    | Twitter            | ⭕ Halfway (federated)          | ⭕ No (unless via Tor Browser)                 | ❌ No (unencrypted?)                         | ✔️                                     | ?                                       | ❌ Yes (need 'instance' server)     |
| [Matrix](https://matrix.org/)                 | Co-working space  | Slack              | ⭕ Halfway (federated)          | ❌ No?                                         | ✔️ Yes? (100% E2EE)                          | ?                                     | ✔️ Yes (?)                               | ❌ Yes (invited channels only?)     |
| [Briar Messenger](https://briarproject.org/)  | Messenger         | WhatsApp           | ✔️ Fully (P2P)                  | ✔️ Yes? (Tor)                                  | ✔️ Yes (100% E2EE)                           | ❌ None (needs 24/7 listener)          | ⭕ Partly (public keys traded IRL)       | ❌ Yes (need initial contact?)      |
| [Cabal Chat](https://cabal.chat/)             | Private chatrooms | IRC                | ✔️ Fully (P2P)                  | ❌ No (P2P reveals IP)                         | ⭕ Mostly (shared key, not E2EE)             | ✔️ Distributed Hash Table              | ❌ No (?)                                | ✔️ Not really (public chat is open) |
| [Signal](https://signal.org/)                 | Messenger         | WhatsApp           | ❌ No?                          | ❌ No                                          | ✔️ Yes (E2EE, and audited)                   | ?                                     | ?                                       | ✔️                                  |

## Comparison of their features


| Other cool thing                              | DM users (E2EE) | Group chat (E2EE) | Post to world | Post to friends/ties | Symmetric ties (friends) | Asymmetric ties (followers) | Like posts | Repost posts | Edit posts | Delete posts |
| --------------------------------------------- | --------------- | ----------------- | ------------- | -------------------- | ------------------------ | --------------------------- | ---------- | ------------ | ---------- | ------------ |
| *[Comrad](http://comrad.app)*               | ✔️               | ❌?                | ✔️             | ✔️                    | ✔️                        | ✔️                           | ✔️?         | ❌            | ❌          | ✔️            |
| [Secure Scuttlebutt](https://scuttlebutt.nz/) | ✔️               | ❌?                | ❌             | ✔️                    | ✔️                        | ✔️                           | ✔️          | ❌?           | ❌          | ❌            |
| [Diaspora](https://diasporafoundation.org/)   | ❌?              | ❌?                | ❌?            | ✔️                    | ❌                        | ✔️                           | ✔️          | ✔️?           |
| [Mastodon](https://joinmastodon.org/)         | ✔️               | ❌?                | ✔️             | ✔️                    | ❌                        | ✔️                           | ✔️          | ✔️?           |
| [Matrix](https://matrix.org/)                 | ✔️               | ✔️                 | ❌?            | ✔️                    | ✔️                        | ❌                           | ❌?         | ❌?           |
| [Briar Messenger](https://briarproject.org/)  | ✔️               | ✔️                 | ❌?            | ✔️                    | ✔️                        | ❌                           | ❌?         | ❌?           |
| [Cabal Chat](https://cabal.chat/)             | ?               | ✔️                 | ❌?            | ✔️                    | ❌                        | ❌                           | ❌          | ❌            |
| [Signal](https://signal.org/)                 | ✔️               | ✔️                 | ❌             | ❌                    | ✔️                        | ❌                           | ❌          | ❌            |


