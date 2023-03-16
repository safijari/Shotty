# ShotAgg: Local Screenshot Aggregator for The Steam Deck

## What?
This is a plugin for the the Steam Deck that uses Decky (Plugin) Loader. It contains two functions:

1. A way to bring all screenshots on your Deck to the `/home/deck/Pictures/Screenshots` folder as symlinks (use the `Aggregate` button)
2. A background service to symlink any new screenshots you take after installing the plugin

Symlinks are used here so as to not duplicate data. The files in the `Screenshots` folder thus will only be links, 
but if you copy them over ssh or using DeckMTP they sould copy the actual files that the link is poiting to.

The screenshots are categorized under separate folders for each app. For Steam native apps the folder will have the same name as the app
(e.g. `Half Life`). For non-steam apps the folder will be the app ID (e.g. `2254521` for Moonlight on my Deck).

## How?

Install it from the Decky Loader's app store.

## Why?

The Steam screenshot system is a pain. All I wanna do is send a screenshot to my friends I shouldn't have to jump hoops like
finding them in the UI and uploading them to the Steam cloud first. This allows me to use a simple app on my phone (CX File Explorer)
to browse my Deck's hard drive and share a screenshot using Telegram.

## TODO?

Honestly I consider this pretty complete, but possibly I could add:

1. A "copy mode" for thos that fear symlinks
2. User configurable folder
3. Better folder names for non-steam games (Though I don't know how to get that...)