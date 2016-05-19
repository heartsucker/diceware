#!/bin/bash
set -e
set -u
set -o pipefail

echo_bold() {
  echo -e "\033[1;37m$@\033[0m"
}

get_script_dir() {
  declare src="${BASH_SOURCE[0]}"
  declare dir=''

  while [ -h "$src" ]; do
    dir="$(cd -P "$(dirname "$src")" && pwd)"
    src="$(readlink "$src")"
    [[ "$src" != /* ]] && src="$dir/$src"
  done
  cd -P "$(dirname "$src")" && pwd
}

script_dir="$(get_script_dir)"
declare -r script_dir

cd "$script_dir"

if ! hash virtualenv; then
  echo_bold 'Installing virtualenv with pip'
  pip install virtualenv
fi

declare -r venv_dir='venv'
declare -r python_version='python3'
declare -r python_bin="$(which "$python_version")"

if [ -z "$python_bin" ]; then
  echo "Unable to locate Python executable '$python_version'. PATH: $PATH" >&2
  exit 1
fi

echo_bold 'Setting up virtualenv'
rm -rf "$venv_dir"
virtualenv -p "$python_bin" "$venv_dir"
source "$venv_dir/bin/activate"
pip install -U -r requirements.txt
echo_bold 'Success'

echo_bold "To enable the virtualenv, run \`source $script_dir/$venv_dir/bin/activate\`"
echo_bold 'Remember: You need to do this for every terminal session!'
echo_bold 'To disable the virtualenv, run `deactivate`'
