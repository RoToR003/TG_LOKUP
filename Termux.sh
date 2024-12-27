#!/bin/bash

command_exists() {
  command -v "$1" &> /dev/null
}

update_packages() {
    echo "Updating package list..."
    pkg update -y
    echo "Upgrading all packages..."
    pkg upgrade -y
}

install_dependencies() {
    if ! command_exists python3; then
      echo "Python3 is not installed. Installing Python3..."
      pkg install -y python
    else
      echo "Python3 is already installed. Checking for updates..."
      pkg upgrade -y python
    fi

    echo "Checking Python packages..."
    REQUIRED_PACKAGES=("requests" "tqdm" "tabulate" "patool")

    for PACKAGE in "${REQUIRED_PACKAGES[@]}"; do
      if ! python3 -c "import $PACKAGE" &> /dev/null; then
        echo "$PACKAGE not found. Installing $PACKAGE..."
        pip3 install "$PACKAGE"
      else
        echo "$PACKAGE is already installed. Checking for updates..."
        pip3 install --upgrade "$PACKAGE"
      fi
    done

    if ! command_exists unrar; then
      echo "unrar is not installed. Installing unrar..."
      pkg install -y unrar
    else
      echo "unrar is already installed. Checking for updates..."
      pkg upgrade -y unrar
    fi

    if ! command_exists bsdtar; then
      echo "bsdtar is not installed. Installing bsdtar..."
      pkg install -y bsdtar
    else
      echo "bsdtar is already installed. Checking for updates..."
      pkg upgrade -y bsdtar
    fi
}

chmod +x "$0"

echo "Running setup for Termux..."

update_packages

install_dependencies

echo "All dependencies are installed and up-to-date."

python main.py
