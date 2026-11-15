#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$(realpath -- "$0")")"
if [[ $EUID == 0 ]]; then echo 'Normal kullanıcı olarak çalıştırın.'; exit 1; fi
sudo -v
if ! python -c 'import PySide6' 2>/dev/null; then
  echo 'PySide6 ve pacman-contrib kurulumu tam sistem güncellemesi gerektirir.'
  read -r -p 'Devam edilsin mi? [e/H] ' answer
  [[ "$answer" == [eEyY] ]] || exit 0
  sudo pacman -Syu --needed pyside6 pacman-contrib
fi
(while sleep 45; do sudo -n -v || exit; done) &
keeper=$!
trap 'kill "$keeper" 2>/dev/null || true' EXIT
python manager.py "$@"
