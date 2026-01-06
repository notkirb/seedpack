#!/usr/bin/env python3
import json
import requests
import argparse
import shutil
import os
from rich.progress import Progress
from rich.console import Console

def get_latest_fabric_loader(version : str):
    response = requests.get(f"https://meta.fabricmc.net/v2/versions/loader/{version}")
    return json.loads(response.content)[0]["loader"]

parser = argparse.ArgumentParser()
parser.add_argument("-t", "--seed", help="Path of seed folder")
parser.add_argument("-c", "--create-seed", help="Path of modlist.json", nargs="?" , const=True, default=None)

parser.add_argument("-g", "--game-version", help="Override game version")
parser.add_argument("-v", "--verbose", help="Increate print verbosity", action="store_true")
parser.add_argument("-y", "--noconfirm", help="When -t used: Default 'yes' to download and package modpack | When -c used: Skip inputs and use defaults (DANGEROUS)", action="store_true")
parser.add_argument("-f", "--force", help="Force incompatible mods to be added (DANGEROUS)", action="store_true")
args = parser.parse_args()

console = Console(highlight=False)
print = console.print
input = console.input

if args.seed:
    seed_file = open(os.path.join(args.seed, "index.json"), "r") 
    seed = json.load(seed_file)

    if args.game_version:
        game_version = args.game_version
    else:
        game_version = seed["target_game_version"]

    print(f"\nUsing seed [cyan]{seed["pack_name"]} {seed["pack_version"]}[/] with game version [cyan]{game_version}[/]")

    match seed["loader"]:
        case "fabric":
            loader_index_name = "fabric-loader"
            loader = get_latest_fabric_loader(game_version)
            if args.verbose:
                print(f"Fabric loader version: {loader["version"]}")

    files = []
    incompatible = []

    print(f"\n[cyan]Checking mods...[/] this will take a while.")

    response = requests.get(f"https://api.modrinth.com/v2/projects", params={"ids": json.dumps(seed["mods"])})
    if response.ok:
        mods = json.loads(response.content)
        if args.verbose:
            print(f"[cyan]Found mods[/]: ")
            for mod in mods:
                print(f"   - {mod["title"]} [bright_black]({mod["id"]})[/]")
        with Progress() as progressbar:
            task = progressbar.add_task("Checking mods", total=len(mods))
            for mod in mods:
                response = requests.get(f"https://api.modrinth.com/v2/project/{mod["id"]}/version", params={"game_versions": json.dumps([game_version]), "loaders": json.dumps([seed["loader"]])})
                if response.ok:
                    try:
                        version = json.loads(response.content)[0]
                        if args.verbose:
                            print(f"\n[green]Found version[/]: '{version["version_number"]}' with target '{version["game_versions"][-1]}'")
                        files.append(version)
                    except IndexError:
                        if args.verbose:
                            print(f"\n[red]No compatible version found[/]: '{mod["title"]}'")
                        incompatible.append(mod)
                else:
                    print(f"[bold red]Error when getting version for mod[/] '{mod["id"]}' with target '{game_version}': '{response.status_code}' | '{response.content}'")
                progressbar.update(task, advance=1)

    else:
        print(f"[bold red]Error when getting mods[/]: '{response.status_code}' | '{response.content}'")

    if len(incompatible) > 0:
        print(f"\n{len(incompatible)} [red]mods are incompatible with[/] {game_version}:")
        for mod in incompatible:
            print(f"   - {mod["title"]} [bright_black]({mod["id"]})[/]")

    print("\nThe following mods will be added:")
    for mod in files:
        print(f"[bright_black]{mod["files"][0]["filename"]}[/]", end=", ")
    if os.path.exists(os.path.join(args.seed, "overrides")):
        print("\nThe following overrides will be added:")
        for file in os.listdir(os.path.join(args.seed, "overrides")):
            print(f"[bright_black]{file}[/]", end=", ")
    print()

    if args.noconfirm == False:
        while True:
            user_choice = input("\n[bright_yellow]Do you want to continue?[/] (Y/n): ")
            match user_choice.lower():
                case 'y':
                    break
                case '':
                    break
                case 'n':
                    exit()
                case _:
                    print("Invalid input. Please enter 'y' or 'n'.")

    files_formatted = []
    for file in files:
        new_file = {
            "downloads": [file["files"][0]["url"]],
            "env": {
                "client": "required",
                "server": "unsupported"
            },
            "fileSize": file["files"][0]["size"],
            "hashes": file["files"][0]["hashes"],
            "path": "mods/" + file["files"][0]["filename"]
        }
        files_formatted.append(new_file)

    modrinth_index = {
        "dependencies": {
            loader_index_name: loader["version"],
            seed["game"]: game_version
        },
        "files": files_formatted,
        "formatVersion": 1,
        "game": seed["game"],
        "name": seed["pack_name"],
        "versionId": seed["pack_version"]
    }

    os.mkdir(os.path.join(os.getcwd(), ".tmp"))
    modrinth_index_file = open(os.path.join(os.getcwd(), ".tmp", "modrinth.index.json"), "w")
    modrinth_index_file.write(json.dumps(modrinth_index))
    if os.path.exists(os.path.join(args.seed, "overrides")):
        shutil.copytree(os.path.join(args.seed, "overrides"), os.path.join(os.getcwd(), ".tmp", "overrides"))

    shutil.make_archive(f"{seed["pack_name"]}_{seed["pack_version"]}.mrpack", "zip", os.path.join(os.getcwd(), ".tmp"))
    shutil.move(os.path.join(os.getcwd(), f"{seed["pack_name"]}_{seed["pack_version"]}.mrpack.zip"), os.path.join(os.getcwd(), f"{seed["pack_name"]}_{seed["pack_version"]}.mrpack"))

    shutil.rmtree(os.path.join(os.getcwd(), ".tmp"))

    print(f"\n[green]Modrinth pack file written to[/] {seed["pack_name"]}_{seed["pack_version"]}.mrpack\n")
    seed_file.close()
    modrinth_index_file.close()

elif args.create_seed is not None:

    if args.noconfirm:
        print()
        pack_name = "my-modpack"
        pack_version = "1.0.0"
        loader = "fabric"
        game_version = "1.21.10"
    else:
        pack_name = input("[cyan]Enter pack name[/]: ")
        pack_version = input("[cyan]Enter pack version[/]: ")
        loader = input("[cyan]Enter mod loader[/]: ")
        game_version = input("[cyan]Enter target game version[/]: ")

    if args.noconfirm:
        print("[red]WARNING[/]: -y used, please change metadata in index.json before continuing.")

    if args.create_seed is True:
        mods = []
    else:
        modlist_file = open(args.create_seed, "r") 
        modlist = json.load(modlist_file)
        mods = []
        for mod in modlist:
            mod_id = mod["url"].split("/")[-1]
            if len(mod_id) == 8:
                mods.append(mod_id)

    index = {
        "game": "minecraft",
        "pack_name": pack_name,
        "pack_version": pack_version,
        "loader": loader,
        "target_game_version": game_version,
        "mods": mods,
        "template_format": ["modrinth", 1]
    }

    os.mkdir(os.path.join(os.getcwd(), "seed"))
    index_file = open(os.path.join(os.getcwd(), "seed", "index.json"), "w")
    index_file.write(json.dumps(index))

else:
    parser.print_help()
