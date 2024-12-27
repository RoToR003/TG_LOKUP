# TG_LOKUP

**TG_LOKUP** is a Telegram identifier search tool designed to efficiently handle and search through a 9.3 GB database containing over 182 000 000 entries. It supports automatic component downloads and is cross-platform, running on Windows, Linux, and Termux.

## Features

- **Automatic Database Download**: Automatically fetches and extracts the required database on first launch.
- **Fast Search**: Optimized for rapid searches of Telegram identifiers.
- **Cross-Platform**: Works seamlessly on Windows, Linux, and Termux.
- **Dependency Management**: Automatically installs required dependencies.

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/RoToR003/TG_LOKUP.git
cd TG_LOKUP
```

### 2. Install Dependencies

#### For Windows

Run the `Windows.bat` script to automatically install all required components.

#### For Linux

```bash
chmod +x Linux.sh
./Linux.sh
```

#### For Termux

```bash
chmod +x Termux.sh
./Termux.sh
```

## Usage

### 1. Launch the Tool

#### On Windows

Run the `Windows.bat` script.

#### On Linux

```bash
python3 main.py
```

#### On Termux

```bash
python main.py
```

### 2. Perform a Search

Once the tool is running, input one or more Telegram identifiers separated by commas. The tool will process the database and display results in a readable format.

## Requirements

- **Python 3.7+**
- **pip** (for dependency installation)
- **Internet Connection** (to download the database and dependencies)

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## Author

- [RoToR003](https://github.com/RoToR003)

