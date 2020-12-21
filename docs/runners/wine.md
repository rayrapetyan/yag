
# Wine

Wine module manages wine envs (aka wine-prefixes) and runs wine-compatible apps. Configurable parameters are defined in `group_vars/all`:
`wine.bodega`: base folder for all wine environments
`wine.apps_folder`: base folder for apps within a wine env

## Input parameters:

- *recipe*: use to uniquely identify and describe your wine environment. Hash of all fields of this structure will be used as a wine-prefix. If you omit specifying recipe, your app will be installed under default wine prefix using following recipe:
```yaml
recipe:
 os_ver: win7
 os_arch: win32
 dll_overrides: none
 install_gecko: False
 install_mono: False
 deps: none
```
`deps` doesn't have any effect and changes only a hash of the structure so you end up creating a new wine env. This is useful when there are known incompatible dependencies (e.g. legacy `quicktime` or `directx`) so you just list them under `deps` using format of your choice and a new env will be created. Maybe in the future wine module will recognize certain deps and install them automatically, but for now it's just a "salt" for env hash.

```yaml
wine_recipe:  
 os_ver: win10 
 deps: 
   - directx9

- wine:  
    recipe: "{{ wine_recipe }}" 
    exec: "{{ app_folder }}/QTW/QuickTimeFullInstaller.exe"
```  
When you use a custom recipe for installation it's important also to pass the same recipe in your run script so both are using the same wine-prefix. So it's recommended to define custom wine recipes in app's `vars` folder.

- *exec*: executable to run (without arguments, see below)
```yaml
- wine:
    exec: "{{ app_folder }}/{{ executable }}"
```

- *args*: command line arguments
```yaml
- wine:  
   recipe: "{{ wine_recipe }}" 
   exec: "{{ app_folder }}/__redist/DirectX/DXSETUP.exe" 
   args: 
     - "/silent"
```

## Parameters for `run` scripts
- *virtual_desktop*: enable virtual desktop (mandatory for some apps).
```yaml
- wine:  
    exec: "{{ app_folder }}/Ace.exe" 
    virtual_desktop: "800x600"
```  

- *cdrom*: mount cdrom.
```yaml
- wine:
    recipe: "{{ wine_recipe }}"
    cdrom: 
      letter: "d" 
      target: "{{ app_folder }}" 
    exec: "{{ app_folder }}/GOLDENGA.EXE"
```

## Parameters for `install` scripts
- *registry*: make changes in Windows registry.
```yaml
- wine:  
    registry: 
      "HKEY_LOCAL_MACHINE\\Software\\Ion Storm\\Thief - Deadly Shadows": 
        - "ION_ROOT": "{{ wine_app_folder }}" 
        - "SaveGamePath": "{{ wine_app_folder }}\\\\SAVES"
    state: present
```
Make sure slashes are properly escaped.

- *state*:   can be `present` or `absent`. Check if appropriate wine env is present or not.
