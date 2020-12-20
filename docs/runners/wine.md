
# Wine

Wine module manages wine envs (aka wine-prefixes) and runs wine-compatible apps.  All wine envs are located under `wine.bodega` folder (see `group_vars/all`).

## Input parameters:

- *recipe*: use to uniquely identify and describe your wine environment. Hash of this structure will be used as a   wine-prefix. If you omit specifying recipe, your app will be installed under default wine prefix using following recipe:
```yaml
recipe:
 bodega: WINE_BODEGA
 int_apps_folder: WINE_APPS_FOLDER
 ext_apps_folder: APPS_FOLDER
 os_ver: win7 
 deps: None
```
`WINE_BODEGA`: `~/yag//envs/wine` - root folder for all wine envs.  
`WINE_APPS_FOLDER`: `C:\apps`  
`APPS_FOLDER`: `~/yag/apps`  
You can redefine base values for all env vars in `group_vars/all`.
`deps` doesn't make any changes and affect only hash of the structure so you end up creating a new wine env. This is  useful when there are known incompatible dependencies (e.g. legacy `quicktime` or `directx`) so you just list them under  `deps` using format of your choice and a new env will be created.  Maybe in the future wine module will recognize certain deps and install them automatically, but for now it's just a "salt" for env hash.
```yaml
wine_recipe:  
 os_ver: win10 
 deps: 
   - directx9

- wine:  
    recipe: "{{ wine_recipe }}" 
    exec: "{{ app_folder }}/QTW/QuickTimeFullInstaller.exe"
```  
When you use a custom recipe for installation it's important also to pass the same recipe in your run script so both are using same wine-prefix. So it's recommended to define custom wine recipes in  app's `vars` folder.

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
    cdrom: letter: "d" 
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
