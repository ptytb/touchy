set CL=/Zm2000
%comspec% /k "C:\Program Files (x86)\Microsoft Visual Studio\2017\BuildTools\VC\Auxiliary\Build\vcvars64.bat"
nuitka --jobs=1 --show-progress --show-scons --standalone --windows-disable-console --python-flag=no_site --output-dir=dist  --include-module=autoclass  --include-module=valid8  --include-module=mini_lambda --include-module=six --include-module=mido.backends.rtmidi --include-module=rtmidi touchy.py
