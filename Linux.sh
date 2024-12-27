#!/bin/bash

command_exists() {
  command -v "$1" &> /dev/null
}

update_packages() {
    echo "Updating package list..."
    sudo apt update -y
    echo "Upgrading all packages..."
    sudo apt upgrade -y
}

install_dependencies() {
    if ! command_exists python3; then
      echo "Python3 is not installed. Installing Python3..."
      sudo apt install -y python3
    else
      echo "Python3 is already installed. Checking for updates..."
      sudo apt upgrade -y python3
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
      sudo apt install -y unrar
    else
      echo "unrar is already installed. Checking for updates..."
      sudo apt upgrade -y unrar
    fi

    if ! command_exists bsdtar; then
      echo "bsdtar is not installed. Installing bsdtar..."
      sudo apt install -y bsdtar
    else
      echo "bsdtar is already installed. Checking for updates..."
      sudo apt upgrade -y bsdtar
    fi
}

chmod +x "$0"

echo "Running setup for Linux..."

update_packages

install_dependencies

echo "All dependencies are installed and up-to-date."

python3 main.py
