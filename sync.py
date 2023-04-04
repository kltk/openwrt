#!/usr/bin/env python3
from subprocess import run
import os
import yaml
import glob

__abs_file__ = os.path.abspath(__file__)
__abs_dir__ = os.path.dirname(__abs_file__)


def main():
  config = yaml.safe_load(open('./repos.yaml'))
  remotes = '.git/refs/remotes'

  for repo in config:
    print(f"repo add {repo['name']} {repo['url']} ")
    run(['git', 'remote', 'add', repo['name'], repo['url']])

  run(['git', 'fetch', '--all'])

  for path in (glob.glob(f'{remotes}/*/**/*', recursive=True)):
    p = os.path.relpath(path, remotes)
    repo = p.split('/')[0]
    branch = os.path.relpath(p, repo)
    if (not repo in ['origin']):
      print(repo, branch, p)
      branchmap = f'refs/remotes/{repo}/{branch}:refs/heads/{repo}/{branch}'
      run(['git', 'push', '--force', 'origin', branchmap])


main()
