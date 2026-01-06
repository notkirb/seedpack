# Seedpack 🌱: Declarative modpacks
Seedpack is a modpack management utility for modpack developers to quickly update and distribute modpacks. It uses templates called *seeds* to find compatible mods and generate a modpack. All a developer has to do is define the game version, then generate a modpack.

## Terminology

| Word | Meaning |
| --- | --- |
| Seed | A template for Seedpack to follow |
| Grow | Turning a seed into a distributable modpack file |
| Plant | Creating a seed either from another source or fresh |

## Using Seedpack
To grow a modpack:

```bash
$ python3 seedpack.py -t ~/my-cool-modpack
```

To plant a seed with a modlist.json from Prism Launcher:

```bash
$ python3 seedpack.py -c modlist.json
```

To grow a modpack with a specific game version:

```bash
$ python3 seedpack.py -t ~/my-cool-modpack -g 1.21.11
```

To see a list of additional commands: 

```bash
$ python3 seedpack.py -h
```

## Understanding seeds
Seeds must follow a specific structure to work properly. A seed is a folder that consists of an index/config file and an overrides folder. 

```bash
# example
my-cool-modpack/
├ index.json
└ overrides/
  ├ config/
  ├ resourcepacks/
  └ options.txt
```

The overrides folder contains files that will be copied to the Minecraft instance after the modpack is installed. This is usually how you should put mod config files into your modpack.

The index.json is the most important part of a seed. It contains the IDs of each of the mods, and additional metadata about your modpack. Mod IDs are the unique identifiers for each mod. A modpack must confine to only one mod provider at once. For Modrinth mods, the ID can be found by opening the kabab menu on a mod page and pressing 'Copy ID.'

The following is an example for an index.json:

```json
{
    "game": "minecraft",
    "pack_name": "kirbium",
    "pack_version": "1.0.0",
    "loader": "fabric",
    "target_game_version": "1.21.11",
    "mods": [
        "EsAfCjCV",
        "lhGA9TYQ",
        "g96Z4WVZ"
    ],
    "template_format": [
        "modrinth",
        1
    ]
}
```
