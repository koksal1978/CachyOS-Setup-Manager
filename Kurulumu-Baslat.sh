#!/usr/bin/env bash
set -e
cd -- "$(dirname -- "$(realpath -- "$0")")"
exec konsole --hold -e bash -c 'sudo -v && bash launch.sh'
