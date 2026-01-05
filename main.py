#!/usr/bin/env python3
import json
import requests
import argparse
import shutil
import os

def get_latest_fabric_loader(version : str):
    response = requests.get(f"https://meta.fabricmc.net/v2/versions/loader/{version}")
    return json.loads(response.content)[0]["loader"]

parser = argparse.ArgumentParser()
parser.add_argument("-t", "--template", help="Path of template folder")
parser.add_argument("-c", "--create-template", help="Path of modlist.json")
parser.add_argument("-v", "--verbose", help="Increate print verbosity", action="store_true")
parser.add_argument("-y", "--noconfirm", help="Default 'yes' to download and package modpack", action="store_true")
parser.add_argument("-f", "--force", help="Force incompatible mods to be installed", action="store_true")
args = parser.parse_args()

if args.template:
    template_file = open(os.path.join(args.template, "index.json"), "r") 
    template = json.load(template_file)

    print(f"\nUsing template {template["pack_name"]}@{template["pack_version"]}")

    match template["loader"]:
        case "fabric":
            loader_index_name = "fabric-loader"
            loader = get_latest_fabric_loader(template["target_game_version"])
            if args.verbose:
                print(f"Fabric loader version: {loader["version"]}")

    files = []
    incompatible = []

    print(f"\n\033[96mChecking mods...\033[0m this will take a while.")

    response = requests.get(f"https://api.modrinth.com/v2/projects", params={"ids": json.dumps(template["mods"])})
    if response.ok:
        mods = json.loads(response.content)
        if args.verbose:
            print(f"\033[96mFound mods\033[0m: ")
            for mod in mods:
                print(f"   - {mod["title"]} \033[90m({mod["id"]})\033[0m")
        for mod in mods:
            response = requests.get(f"https://api.modrinth.com/v2/project/{mod["id"]}/version", params={"game_versions": json.dumps([template["target_game_version"]]), "loaders": json.dumps([template["loader"]])})
            if response.ok:
                try:
                    version = json.loads(response.content)[0]
                    if args.verbose:
                        print(f"\033[92mFound version\033[0m: '{version["version_number"]}' with target '{version["game_versions"][-1]}'")

                    files.append(version)
                except IndexError:
                    if args.verbose:
                        print(f"\033[31mNo compatible version found\033[0m: '{mod["title"]}'")
                    incompatible.append(mod)
            else:
                print(f"\033[31mError when getting version for mod\033[0m '{mod["id"]}' with target '{template["target_game_version"]}': '{response.status_code}' | '{response.content}'")

    else:
        print(f"\033[31mError when getting mods\033[0m: '{response.status_code}' | '{response.content}'")

    if len(incompatible) > 0:
        print(f"\n{len(incompatible)} \033[31mmods are incompatible with\033[0m {template["target_game_version"]}:")
        for mod in incompatible:
            print(f"   - {mod["title"]} \033[90m({mod["id"]})\033[0m")

    print("\nThe following mods will be added:")
    for mod in files:
        print(f"\033[90m{mod["files"][0]["filename"]}\033[0m", end=", ")
    if os.path.exists(os.path.join(args.template, "overrides")):
        print("\nThe following overrides will be added:")
        for file in os.listdir(os.path.join(args.template, "overrides")):
            print(f"\033[90m{file}\033[0m", end=", ")
    print()

    if args.noconfirm == False:
        while True:
            user_choice = input("\n\033[93mDo you want to continue?\033[0m (Y/n): ")
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
            template["game"]: template["target_game_version"]
        },
        "files": files_formatted,
        "formatVersion": 1,
        "game": template["game"],
        "name": template["pack_name"],
        "versionId": template["pack_version"]
    }

    os.mkdir(os.path.join(os.getcwd(), ".tmp"))
    modrinth_index_file = open(os.path.join(os.getcwd(), ".tmp", "modrinth.index.json"), "w")
    modrinth_index_file.write(json.dumps(modrinth_index))
    if os.path.exists(os.path.join(args.template, "overrides")):
        shutil.copytree(os.path.join(args.template, "overrides"), os.path.join(os.getcwd(), ".tmp", "overrides"))

    shutil.make_archive(f"{template["pack_name"]}_{template["pack_version"]}.mrpack", "zip", os.path.join(os.getcwd(), ".tmp"))
    shutil.move(os.path.join(os.getcwd(), f"{template["pack_name"]}_{template["pack_version"]}.mrpack.zip"), os.path.join(os.getcwd(), f"{template["pack_name"]}_{template["pack_version"]}.mrpack"))

    shutil.rmtree(os.path.join(os.getcwd(), ".tmp"))

    print(f"\n\033[92mModrinth pack file written to\033[0m {template["pack_name"]}_{template["pack_version"]}.mrpack\n")
    template_file.close()
    modrinth_index_file.close()

elif args.create_template:
    modlist_file = open(args.create_template, "r") 
    modlist = json.load(modlist_file)

    print()
    pack_name = modlist_file.name.split("/")[-1] if args.noconfirm else input("\033[96mEnter pack name\033[0m: ")
    pack_version = "1.0.0" if args.noconfirm else input("\033[96mEnter pack version\033[0m: ")
    loader = "fabric" if args.noconfirm else input("\033[96mEnter mod loader\033[0m: ")
    game_version = "1.21.10" if args.noconfirm else input("\033[96mEnter target game version\033[0m: ")

    if args.noconfirm:
        print("\033[31mWARNING\033[0m: -y used, please change metadata in index.json before continuing.")

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

    os.mkdir(os.path.join(os.getcwd(), "template"))
    index_file = open(os.path.join(os.getcwd(), "template", "index.json"), "w")
    index_file.write(json.dumps(index))

else:
    parser.print_help()
