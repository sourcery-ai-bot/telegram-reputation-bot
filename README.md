# Telegram reputation bot
[![Visits Badge](https://badges.pufler.dev/visits/kevinpita/telegram-reputation-bot)](https://badges.pufler.dev)
[![Updated Badge](https://badges.pufler.dev/updated/kevinpita/telegram-reputation-bot)](https://badges.pufler.dev)

This bot allows you to track reputation (+/-) in a Telegram group, having total and date-relative score.
## README is on WIP (Work in progress)

## Commands
### `/toprep`
This command can be used by any user, it will send a message showing (by default) the **top 10 most reputated users**, with their rank and total reputation.

You can use an argument to specify the number of users to be shown on the ranking

##### Examples
Using the command without any argument

```
/toprep

1º - USER1 - 10
2º - USER2 - 9
3º - USER3 - 8
4º - USER4 - 7
5º - USER5 - 6
6º - USER6 - 5
7º - USER7 - 4
8º - USER8 - 3
9º - USER9 - 2
10º - USER10 - 1

```

Using the command with a numeric argument

```
/toprep 5

1º - USER1 - 10
2º - USER2 - 9
3º - USER3 - 8
4º - USER4 - 7
5º - USER5 - 6

```
---
#### `/weeklyrep`
This command can be used by any user, it will send a message showing the top 20 most reputated users  with their rank and reputation **computed in the last (by default) week**.

You can use an argument to specify the number of weeks to consider.

##### Examples
Using the command without any argument

```
/toprep


Since a week ago:

1º - USER1 - 10
2º - USER2 - 9
3º - USER3 - 8
...
20º - USER20 - -1
```

Using the command with a numeric argument

```
/toprep 5


Since 5 weeks ago:

1º - USER1 - 10
2º - USER2 - 9
3º - USER3 - 8
...
20º - USER20 - -1

```

