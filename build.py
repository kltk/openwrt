#!/usr/bin/env python3
from pathlib import Path
import subprocess
import os
import yaml
import glob
import sys
import logging
import shlex
import threading

class CommandExecutionException(Exception):
    def __init__(self, command: str, exit_code: int) -> None:
        super().__init__(f"command executed fail with exit-code={exit_code}: {command}")

_logger = logging.getLogger(__name__)

class TextReadLineThread(threading.Thread):
    def __init__(self, readline, callback, *args, **kargs) -> None:
        super().__init__(*args, **kargs)
        self.readline = readline
        self.callback = callback

    def run(self):
        for line in iter(self.readline, ""):
            if len(line) == 0:
                break
            self.callback(line)

def cmd_exec(command: str, ensure_success: bool=True) -> int:
    _logger.info("executing command: {}".format(command))

    cmd = shlex.split(command)

    process = subprocess.Popen(
        cmd,
        shell=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        )

    _logger.debug("started command")

    def log_warp(func):
        def _wrapper(line: str):
            return func("\t" + line.strip())
        return _wrapper

    read_stdout = TextReadLineThread(process.stdout.readline, log_warp(_logger.info))
    read_stderr = TextReadLineThread(process.stderr.readline, log_warp(_logger.warning))
    read_stdout.start()
    read_stderr.start()

    read_stdout.join()
    _logger.debug("stdout reading finish")
    read_stderr.join()
    _logger.debug("stderr reading finish")
    ret = process.wait()
    _logger.debug("process finish")

    _logger.info("executed command with exit-code={}".format(ret))
    if ensure_success and ret != 0:
        raise CommandExecutionException(command=command, exit_code=ret)
    return ret

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
  cmd_exec(f'make download -j8')


def compile():
  try:
    cmd_exec(f'make -j{len(os.sched_getaffinity(0))}')
  except:
    cmd_exec(f'make -j1 V=s')


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
  cmd_exec(f'make defconfig')
  cmd_exec(f'./scripts/diffconfig.sh')
  cmd_exec(f'cat .config')


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
  cmd_exec(f'./scripts/feeds update -a')
  cmd_exec(f'./scripts/feeds install -a')
  cmd_exec(f'./scripts/feeds list')


def loadAssets(assets):
  for asset in assets:
    if os.path.exists(asset["path"]):
      print(f"asset {asset['path']} exist")
      continue
    print(f"load asset to {asset['path']}")
    if asset.get("git"):
      cmd_exec(f'git clone {asset["git"]} {asset["path"]}')
      revision = asset.get("revision")
      os.chdir("openwrt")
      if revision:
        cmd_exec(f'git checkout -b {revision} origin/{revision}')
      cmd_exec(f'git branch -v --all')
      os.chdir("..")

    if asset.get("url"):
      cmd_exec(f'curl -o {asset["path"]} {asset["url"]}')

    if asset.get("link"):
      link = os.path.abspath(asset.get("link"))
      path = os.path.abspath(asset.get("path"))
      if not os.path.exists(link):
        cmd_exec(f'mkdir -p {link}')
      cmd_exec(f'ln -s {link} {path}')


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