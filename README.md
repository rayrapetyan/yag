Ubuntu 18 setup

VBox: mount /ara in VB properties
install VB Guest Additions
sudo adduser $USER vboxsf

sudo ln -s /media/sf_ara/adventum_ark/ /ara/adventum_ark

sudo apt install -y python3-pip
pip3 install --upgrade pip

cd /media/sf_ara/devel/yag
sudo python3 -m pip install -e .





cd /ara/devel/yag; rm -rf build ; rm -rf dist ; rm -rf yag.egg-info; rm -rf /ara/devel/venv_python/py37/lib/python3.7/site-packages/yag*; python setup.py sdist

Install:
yag install neverhood --source="/ara/adventum_ark/images/neverhood/1.iso"

yag install machinarium --source="/ara/adventum_ark/images/machinarium/setup_machinarium_2844-a_(18752).exe"

yag install faust \
--source="/ara/adventum_ark/images/faust_the_seven_games_of_the_soul/1.iso,\
/ara/adventum_ark/images/faust_the_seven_games_of_the_soul/2.iso,\
/ara/adventum_ark/images/faust_the_seven_games_of_the_soul/3.iso,\
/ara/adventum_ark/images/faust_the_seven_games_of_the_soul/4.iso"

yag install brokensword25 --source="/ara/adventum_ark/images/broken_sword_25_the_return_of_the_templars/bs25-setup.exe"

yag install badmojo_redux --source="/ara/adventum_ark/images/bad_mojo_redux/1.iso"

yag install 11hour --source="/ara/adventum_ark/images/11th_hour/setup_the_11th_hour_1.0_(22303).exe"

yag install aceventura --source=/ara/adventum_ark/images/ace_ventura_pet_detective/1.iso

yag install goldengate --source="/ara/adventum_ark/images/golden_gate/1.iso"

Run:

python yag/cli.py run faust_the_seven_games_of_the_soul
python yag/cli.py run neverhood
python yag/cli.py run machinarium
python yag/cli.py run broken_sword_25_the_return_of_the_templars


Please, specify path(s) to the installer source (CD image, installer, URL etc):


- sudo allowed only in packages


Make sure your user is in sudoers group.
(thats shitty and looks insecure...) investigate jails
what about linux?
move all privileged ops to pkg deps of yag

/usr/local/etc/sudoers.d/{your_username}:

%wheel ALL=(ALL) ALL
your_username ALL=(ALL) NOPASSWD: ALL


0.
yag search machinar
Out:
machinarium/gog
machinarium/steam
machinarium/humble
1.
yag install machinarium/gog
    - gog/steam: use credentials stored in the vault based on installer distribution and download from remote party
    - or ask to select a local installer source
    - check installer hash:
        - for gog exec file - whole file
        - for iso images - unpack and check some file hash
    - install gog version
2.
yag install machinarium
    - ask which distrib to install (if multiple)
    - jump to 1.
3.
yag install path_to_installer
    - detect port automatically
    - jump to 1.
4.
yag run machinarium
 - runs already installed version (only one distribution can be installed at a time).
 - perform installaltion cycle - jump to 2. (if not installed)





host_os: [freebsd, linux]
port:
    name: [machinarium, golden_gate, skype]
    distrib: [gog, steam, humble, image, archive]
    version: [1.222, 6.0] (applies to apps, rarely to games)
    installer: [none, windows, linux, steam] (none applies when distrib is an archive, linux - sh file, windows - exe file)
        version: [none, 1.2222, 2.333] (applies to gog)
    runner: [none, wine, scummvm, dosbox, proton, steam] (none - runs natively)
        version: [1.223, 222.33, hq-devel, hq-stage]
        


host_os: freebsd
port:
    name: machinarium
    distrib: gog    
    installer: windows
        version: 1.22222
    runner: wine
        version: latest-stable

host_os: ubuntu
port:
    name: machinarium
    distrib: gog
    installer: linux
        version: 1.22222    
    runner: none

host_os: freebsd
port:
    name: AbilityCash
    distrib: archive
    version: 5.2
    installer: windows        
    runner: wine


- user defines port, distrib (e.g. user owns original CDs and doesn't want to buy a gog version) and path to installer\images
- user can't choose an invalid distrib for a given OS (e.g. steam versions are not supported on freebsd)
- role's main task picks a valid [installer, runner] pair for a [host_os, distrib]:
e.g.

machinarium:
host_os   distrib   installer   runner
freebsd   gog       windows     wine
linux     gog       linux       none

bioshock:
linux     steam     windows     steam

[windows, wine] for [freebsd, gog]
[linux, none] for [linux, gog]

bioshock:
[linux, steam] for [linux, steam]

 
app:
    source:
        path:
        type:
        installer:
            type:
            subtype:
            platform:
    path:
        main:
        data:
        tmp: