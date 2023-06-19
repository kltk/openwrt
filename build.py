#!/usr/bin/env python3
from pathlib import Path
import subprocess
import os
import yaml
import glob
import sys

__abs_file__ = os.path.abspath(__file__)
__abs_dir__ = os.path.dirname(__abs_file__)
profileDir = ""


def grouprun(*args, **kwargs):
  print(f"::group::", *args)
  ret = subprocess.run(*args, **kwargs, capture_output=True, text=True)
  print(ret.stdout)
  print(ret.stderr)
  print("::endgroup::")
  return ret


def loadYaml(name):
  paths = [
      os.path.join(__abs_dir__, "profiles/common", f"{name}.yml"),
      os.path.join(__abs_dir__, "profiles/common", f"{name}.yaml"),
      os.path.join(profileDir, f"{name}.yml"),
      os.path.join(profileDir, f"{name}.yaml"),
  ]
  for p in paths:
    if os.path.exists(p):
      print('load yaml from', p)
      return yaml.safe_load(open(p))


def download():
  grouprun(['make', 'download', '-j8'])


def compile():
  try:
    grouprun(['make', f'-j{len(os.sched_getaffinity(0))}'], check=True)
  except:
    grouprun(['make', '-j1', 'V=s'], check=True)


def upload():
  print()


def patch():
  print()


def loadProfile(profile):
  for inc in profile.get("include", []):
    data = loadYaml(inc)
    loadProfile(data)
    for k in {"target", "subtarget", "profile"}:
      if (data.get(k)):
        if (profile.get(k)):
          print(f"Duplicate tag found {k}, {inc}, {profile[k]} -> {data[k]}")
        profile[k] = data.get(k)
    for k in {"feeds", "packages", "modules", "diffconfig"}:
      if (data.get(k)):
        profile[k] += data[k]
  print("profle", profile)
  if (profile.get("include")):
    profile.pop("include")
  return profile


def genConfig(data):
  output = ""
  target = data.get("target")
  subtarget = data.get("subtarget")
  profile = data.get("profile")
  if (target and subtarget and profile):
    target = f"CONFIG_TARGET_{target}"
    subtarget = f"{target}_{subtarget}"
    profile = f"{subtarget}_DEVICE_{profile}"
    output += f"{target}=y\n"
    output += f"{subtarget}=y\n"
    output += f"{profile}=y\n"
  if (data.get("diffconfig")):
    output += f"{data['diffconfig']}\n"
  for package in data.get("packages", []):
    output += f"CONFIG_PACKAGE_{package}=y\n"
  for module in data.get("modules", []):
    output += f"CONFIG_PACKAGE_{module}=m\n"
  Path(".config").write_text(output)
  print("Configuration writen to .config")
  grouprun(['make', 'defconfig'])
  grouprun(['./scripts/diffconfig.sh'])
  grouprun(['cat', '.config'])


def setupFeeds(config):
  feeds = [Path("feeds.conf.default").read_text()]
  for f in config['feeds']:
    method = f.get("method", "src-git")
    branch = f.get("branch", "master")
    if "path" in f:
      method = f.get("method", "src-link")
      feeds.append(f'{method} {f["name"]} {f["path"]}')
    elif "revision" in f:
      feeds.append(f'{method} {f["name"]} {f["uri"]}^{f["revision"]}')
    elif "tag" in f:
      feeds.append(f'{method} {f["name"]} {f["uri"]};{f["tag"]}')
    else:
      feeds.append(f'{method} {f["name"]} {f["uri"]};{branch}')
  Path('feeds.conf').write_text('\n'.join(feeds))
  grouprun(['./scripts/feeds', "update", "-a"])
  grouprun(['./scripts/feeds', 'install', '-a'])
  grouprun(['./scripts/feeds', 'list'])


def loadAssets(assets):
  for asset in assets:
    if os.path.exists(asset["path"]):
      print(f"asset {asset['path']} exist")
      continue
    print(f"load asset to {asset['path']}")
    if asset.get("git"):
      grouprun(["git", "clone", asset["git"], asset["path"]])
      revision = asset.get("revision")
      os.chdir("openwrt")
      if revision:
        grouprun(["git", "checkout", '-b', revision, f"origin/{revision}"])
      grouprun(["git", "branch", "-v", "--all"])
      os.chdir("..")

    if asset.get("url"):
      grouprun(["curl", "-o", asset["path"], asset["url"]])

    if asset.get("link"):
      link = os.path.abspath(asset.get("link"))
      path = os.path.abspath(asset.get("path"))
      if not os.path.exists(link):
        grouprun(['mkdir', '-p', link])
      grouprun(["ln", "-s", link, path])


def main(profileName):
  defaultProfile = {
      "description": [],
      "feeds": [],
      "packages": [],
      "modules": [],
      "diffconfig": "",
  }

  global profileDir
  profileDir = os.path.join(__abs_dir__, "profiles", profileName)
  data = loadYaml("profile")
  loadAssets(data["assets"])
  os.chdir('openwrt')
  for index, step in enumerate(data["steps"]):
    print(f"build {profileName}#{index}")
    profile = loadProfile({**defaultProfile, **step})
    setupFeeds(profile)
    genConfig(profile)
    patch()
    download()
    compile()
    upload()


main(sys.argv[1])