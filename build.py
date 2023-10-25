#!/usr/bin/env python3
from pathlib import Path
import subprocess
import os
import yaml
import glob
import sys

__abs_file__ = os.path.abspath(__file__)
__abs_dir__ = os.path.dirname(__abs_file__)
profileDir = ''


def grouprun(*args, **kwargs):
  print('::group::', *args)
  ret = subprocess.run(*args, **kwargs, capture_output=True, text=True)
  print(ret.stdout)
  print(ret.stderr)
  ret.check_returncode()
  print('::endgroup::')
  return ret


def loadYaml(name):
  paths = [
      os.path.join(__abs_dir__, 'profiles/common', f'{name}.yml'),
      os.path.join(__abs_dir__, 'profiles/common', f'{name}.yaml'),
      os.path.join(profileDir, f'{name}.yml'),
      os.path.join(profileDir, f'{name}.yaml'),
  ]
  for p in paths:
    if os.path.exists(p):
      print('load yaml from', p)
      return yaml.safe_load(open(p))


def download():
  grouprun(['make', 'download', '-j8'])

def useExternalToolchain():
  path = os.path.join(__abs_dir__, '../toolchain.tar.xz')
  if os.path.exists(path):
    grouprun(['./scripts/ext-toolchain.sh', '--toolchain', path, '--overwrite-config', '--config qualcommax/ipq60xx'])
  else:
    grouprun(['pwd'])
    grouprun(['ls','-al',path])
    print(path)
    raise Exception

def compile():
  try:
    grouprun(['make', f'-j{len(os.sched_getaffinity(0))}'])
  except:
    grouprun(['make', '-j1', 'V=s'])


def upload():
  print()


# 目录/补丁
def patch(profile):
  for (dir, patches) in profile.get('patch', {}).items():
    olddir=os.getcwd()
    os.chdir(dir)
    grouprun(['ls', '-al'])
    grouprun(['ls', '-al', '..'])
    for patch in patches:
      for p in glob.glob(f'{profileDir}/{patch}'):
        # grouprun(['git', 'am', '--quiet', f'{profileDir}/{patch}'])
        grouprun(['git', 'apply', '-p0', '--ignore-space-change', '--ignore-whitespace', p])
    grouprun(['git', 'diff'])
    os.chdir(olddir)


def genConfig(data):
  output = ''
  target = data.get('target')
  subtarget = data.get('subtarget')
  profile = data.get('profile')
  if (target and subtarget and profile):
    target = f'CONFIG_TARGET_{target}'
    subtarget = f'{target}_{subtarget}'
    profile = f'{subtarget}_DEVICE_{profile}'
    output += f'{target}=y\n'
    output += f'{subtarget}=y\n'
    output += f'{profile}=y\n'
  if (data.get('diffconfig')):
    output += f'{data["diffconfig"]}\n'
  for package in data.get('packages', []):
    output += f'CONFIG_PACKAGE_{package}=y\n'
  for module in data.get('modules', []):
    output += f'CONFIG_PACKAGE_{module}=m\n'
  Path('.config').write_text(output)
  print('Configuration writen to .config')
  grouprun(['cat', '.config'])
  grouprun(['make', 'defconfig'])
  grouprun(['./scripts/diffconfig.sh'])
  grouprun(['cat', '.config'])


def setupFeeds(config):
  feeds = [Path('feeds.conf.default').read_text()]
  for f in config['feeds']:
    method = f.get('method', 'src-git')
    branch = f.get('branch', 'master')
    if 'path' in f:
      method = f.get('method', 'src-link')
      feeds.append(f'{method} {f["name"]} {f["path"]}')
    elif 'revision' in f:
      feeds.append(f'{method} {f["name"]} {f["uri"]}^{f["revision"]}')
    elif 'tag' in f:
      feeds.append(f'{method} {f["name"]} {f["uri"]};{f["tag"]}')
    else:
      feeds.append(f'{method} {f["name"]} {f["uri"]};{branch}')
  Path('feeds.conf').write_text('\n'.join(feeds))
  grouprun(['./scripts/feeds', 'update', '-a'])
  grouprun(['./scripts/feeds', 'install', '-a'])
  grouprun(['./scripts/feeds', 'list'])


def loadAssets(assets):
  for asset in assets:
    if os.path.exists(asset['path']):
      print(f'asset {asset["path"]} exist')
      continue

    print(f'load asset to {asset["path"]}')
    if asset.get('git'):
      revision = asset.get('revision')
      depth = asset.get('depth')
      depth = ['--depth', depth] if depth else []
      grouprun(['git', 'clone', *depth, asset['git'], asset['path']])
      olddir=os.getcwd()
      os.chdir(asset['path'])
      print(f'dir: {os.getcwd()}')
      if revision:
        grouprun(['git', 'checkout', '-b', revision, f'origin/{revision}'])
      grouprun(['git', 'branch', '-v', '--all'])
      os.chdir(olddir)
      print(f'dir: {os.getcwd()}')

    if asset.get('url'):
      grouprun(['curl', '-o', asset['path'], asset['url']])

    if asset.get('link'):
      link = os.path.abspath(asset.get('link'))
      path = os.path.abspath(asset.get('path'))
      if not os.path.exists(link):
        grouprun(['mkdir', '-p', link])
      grouprun(['ln', '-s', link, path])


defaultProfile = {
    'description': [],
    'include': [],
    'assets': [],
    'feeds': [],
    'patch': {},
    'packages': [],
    'modules': [],
    'diffconfig': '',
}


def merge(a,b):
  ret = {**defaultProfile, **a}
  for k in {'target', 'subtarget', 'profile'}:
    if (b.get(k)):
      if(ret.get(k)):
        print(f'Duplicate tag found {k}')
      ret[k] = b[k]
  for k in {'include', 'assets', 'feeds', 'packages', 'modules', 'diffconfig'}:
    if (b.get(k)):
      ret[k] += b[k]
  if(b.get('patch')):
    for k in b['patch'].keys():
      if (ret['patch'].get(k)):
        ret['patch'][k] += b['patch'][k]
      else:
        ret['patch'][k] = b['patch'][k]
  return ret


def loadProfile(profile):
  ret = {'include':[], **profile}
  includes = ret.get('include', [])
  ret.pop('include')
  for inc in includes:
    data = loadYaml(inc)
    ret = merge(ret, loadProfile(data))
  return ret


def main(profileName):
  global profileDir
  profileDir = os.path.join(__abs_dir__, 'profiles', profileName)
  profile = loadYaml('profile')
  steps = profile['steps']
  profile.pop('steps')
  for index, step in enumerate(steps):
    profile = loadProfile(merge(profile, step))
    loadAssets(profile['assets'])
    os.chdir('openwrt')
    setupFeeds(profile)
    patch(profile)
    genConfig(profile)
    download()
    useExternalToolchain()
    compile()
    upload()
    os.chdir('..')


main(sys.argv[1])