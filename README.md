# Shotty: Local Screenshot Aggregator for The Steam Deck

## What?
This is a plugin for the the Steam Deck that uses Decky (Plugin) Loader. It contains two functions:

1. A way to bring all screenshots on your Deck to the `~/Pictures/Screenshots` folder (use the `Aggregate` button)
2. A background service to copy any new screenshots you take after installing the plugin.

Note that "copy" here means making a hardlink, so even though the files will behave like normal files, they won't take up any more hard drive space.

You can then copy these files over ssh or using DeckMTP. I personally use CX File Explorer on my phone.

The screenshots are categorized under separate folders for each app. For Steam native apps the folder will have the same name as the app
(e.g. `Half Life`). For non-steam apps a best effort is done to get the name. If a name cannot be found then the folder will be the app ID (e.g. `2254521` for Moonlight on my Deck).

Additionally the most recent screenshot is copied at `~/Pictures/Screenshots/most_recent.jpg`.

## How?

Install it from the Decky Loader's app store.

## Why?

The Steam screenshot system is a pain. All I wanna do is send a screenshot to my friends I shouldn't have to jump hoops like
finding them in the UI and uploading them to the Steam cloud first. This allows me to use a simple app on my phone (CX File Explorer)
to browse my Deck's hard drive and share a screenshot using Telegram.

## TODO?

Honestly I consider this pretty complete, but possibly I could add:

1. User configurable folder (though you can always symlink)