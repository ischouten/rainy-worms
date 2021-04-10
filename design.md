# Flask app

## Game relations

- New game,
Return a random game shortID.

- Join game,

- Start game, (host only)
- Remove player (host only)
- End game

## Turns

Websocket connection (listen to new messages)

## Turn

Roll or new turn response:
The claimable attribute is optional, depending on if there are any stones that can be claimed.

```json
{
  "total": 23,
  "worms": 2,
  "selected": [1, 2, 3, 4, 5, "w"],
  "available_dice": 2,
  "claimable": [19, 20, 21, 22, 23],
  "stealable": {"player_name": 25, "player_name2": 18},
  "player_name": "x"
}
```

## Select dice

Select a number for this roll to be added.

POST /select/2

## Roll again

PUT /roll

## Claim a stone

PUT /claim/18
