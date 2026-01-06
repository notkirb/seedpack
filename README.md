<div align="center">
<br><br>

<img src="assets/images/logo.svg">

# Seedpack - Declarative modpacks
<br>
</div>

![Static Badge](https://img.shields.io/badge/Built%20with%20-%20Seedpack%20-%20green?style=for-the-badge)


Seedpack is a modpack management utility for modpack developers to quickly update and distribute modpacks. It uses templates called *seeds* to find compatible mods and generate a modpack. All a developer has to do is define the game version, then generate a modpack.
<br><br>


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

To grow a modpack with a specific game version:

```bash
$ python3 seedpack.py -t ~/my-cool-modpack -g 1.21.11
```

To plant a seed with a modlist.json from Prism Launcher:

```bash
$ python3 seedpack.py -c ~/path/to/modlist.json
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
        "P7dR8mSH",
        "AANobbMI",
        "YL57xq9U"
    ],
    "template_format": [
        "modrinth",
        1
    ]
}
```

## Create a seed
You can start with a blank slate and add mods manually, or you can start with an existing modpack. 

### From an existing modpack
If you want to start with an existing modpack, you will need Prism Launcher to export a modlist in JSON format with URLs. Here is an example of what you should have:

```json
[
    {
        "name": "Fabric API",
        "url": "https://modrinth.com/mod/P7dR8mSH"
    },
    {
        "name": "Sodium",
        "url": "https://modrinth.com/mod/AANobbMI"
    }
]
```

You can get this by following this process:
- select your modpack
- press edit
- press Mods tab
- press Export modlist
- change format to JSON
- toggle URL
- make sure the format is correct in the Result pane
- press Save and choose a location

Note that only mods that have been downloaded from Modrinth will be added to the modpack. 

Once you have your modlist.json, run:

```bash
$ python3 seedpack.py -c ~/path/to/modlist.json
```

The resulting seed will be generated in your working directory with metadata you enter. You can also run:

```bash
$ python3 seedpack.py -c ~/path/to/modlist.json -y
```

To generate with default metadata to change later.

### From scratch
If you want to start with a blank slate to add mods onto manually, you can run:

```bash
$ python3 seedpack.py -c
```

This will generate a seed in your working directory with metadata you enter. You can also run:

```bash
$ python3 seedpack.py -c -y
```

To generate with default metadata to change later.