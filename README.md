# yag

Welcome to yag, a powerful Ansible-based package manager for FreeBSD and Linux!
It allows to install popular apps (mostly games) from any source (e.g. DRM distribution or original media images).

# Install

Make sure your user is in a sudoers group. Admin permissions are required only when installing system-wide packages 
(e.g. wine or p7zip) as part of the app setup.

## From OS packages

TODO

## From sources

### Prerequisites

You need Python 3.6+ and an appropriate pip installed in your system.

### Ubuntu 18.04 (Bionic Beaver):
```
sudo apt install -y python3-pip
pip3 install --upgrade pip
```
### FreeBSD 12

TODO

### Clone repo
```
cd /tmp
git clone https://github.com/rayrapetyan/yag.git
```

### Configuration
You can find configuration file in acme/group_vars/all.
Feel free to change any parameters there (e.g. root_folder). Warning: you'll not be able to change them again after
build!
```
root_folder: "{{ lookup('env','HOME') }}/yag"

apps_common:
  base_folder: "{{ root_folder }}/apps"
  data_folder: "{{ root_folder }}/data"
  conf_folder: "{{ root_folder }}/conf"

wine:
  bodega: "{{ root_folder }}/envs/wine"
  apps_folder: "C:\\apps"

scummvm:
  conf_path: "{{ apps_common.conf_folder }}/scummvm.ini"

dosbox:
  conf_path: "{{ apps_common.conf_folder }}/dosbox.conf"
```

### Build
```
cd yag
sudo python3 -m pip install -e .
```
Now you can start using yag.

# Usage

## Search app

`yag search machinar`

- outputs list of supported distributions and other app-related info, e.g.
```
machinarium (Machinarium, 2009):
    gog
    steam
    humble
```
## Install new app

`yag install machinarium --source="/images/machinarium/setup_machinarium_2844-a_(18752).exe"`

## Run installed app

`yag run machinarium`

# Adding a new port

First of all, create a new sub-folder in an appropriate folder in the acme tree structure. For example let's add support
for an old classic adventure game - "Golden Gate" which was distributed on 1CD. Make sure you have a valid image of 
original CD. Create a new folder `goldengate` in the `acme\ports\games` so you get a following data structure:
```
acme:
    games:
        goldengate:
            files:
                ...
            tasks:
                install_image.yml
                main.yml
                run.yml
            vars:
                main.yml
            info.yml
```
Start with `info.yml`. Please specify as much information as possible. This info will be used in the `yag search` output.
We'll put GOLDENGA.EXE into files (this is the latest available patch for this game).
main.yml is an entry point - here you'll receive all the input information about source (image or installer).
You should put your install\run playbook logic here. You are free to unleash a full power of the Ansible modules 
and playbook's language.

## Test new port

Checklist (preferably in different environments, e.g. Linux and FreeBSD):
- Make sure app installs. 
- Make sure app runs.
- For games, make sure "saves" are properly stored in a data folder.
