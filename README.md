
![screenshot](https://raw.github.com/ptytb/touchy/res/res/touchy.png)

### binaries

[Touchy for Windows 64-bit](https://github.com/ptytb/touchy/releases/download/v0.1/touchy-bin-win64.zip)

### install & run

```
pipenv install
py touchy.py
```

For building the binaries:

```
pipenv install --dev
build_exe.cmd
```


### virtual midi ports

Use [loopmidi](http://www.tobias-erichsen.de/software/loopmidi.html) to route MIDI output to [VCV Rack](https://github.com/VCVRack/Rack), VST plugins or whatever.
