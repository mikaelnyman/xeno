# Xeno
Download script for bird sounds from xeno-canto.

## Installation on Ubuntu
Install required python packages:

```bash
pip install -r requirements.txt
```

Install required tools for host machine:

```bash
sudo apt-get install -y espeak ffmpeg
```

## Usage
Run the following script to download songs and calls of all birds observed in Finland:

```bash
python script.py
```

Each species have own `.mp3` file. There will be generated voices for species names.

Move files to the device you use and enjoy the playlist.
