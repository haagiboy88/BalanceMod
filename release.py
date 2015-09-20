import os, sys, shutil, py2exe
from distutils.core import setup

class py2exefix(py2exe.build_exe.py2exe):
    # This hack removes tk85.dll from the list of dlls that don't get bundled, since it can be bundled.
    def copy_dlls(self, dlls):
        if 'tk85.dll' in self.dlls_in_exedir:
            self.dlls_in_exedir.remove('tk85.dll')
        # Add tcl85.dll to the list of dlls that don't get bundled, since it can't be.
        if 'tcl85.dll' not in self.dlls_in_exedir:
            self.dlls_in_exedir.append('tcl85.dll')
        py2exe.build_exe.py2exe.copy_dlls(self, dlls)

#Here is where you can set the name for the release zip file and for the install dir inside it.
version = "1.0"
installName = 'BalanceMod-' + version

#target is where we assemble our final install. dist is where py2exe produces exes and their dependencies
if os.path.isdir('target/'):
  shutil.rmtree('target/')
installDir = 'target/' + installName + '/'

#then build the option builder using normal py2exe
sys.argv.append('py2exe')
setup(
	windows = ['BalanceMod.py'],
	options = {
		'py2exe': {
			'includes': ['shutil', 'random', 'PIL', 'os', '_winreg', 'Tkinter', 'ConfigParser', 'string', 'binascii', 'subprocess'],
			'bundle_files': 1,
			'dll_excludes': ['w9xpopen.exe']
		}
	},
	zipfile = None,
	cmdclass = {'py2exe': py2exefix}
)

shutil.copytree('dist/', installDir)
shutil.copytree('gameFiles/', installDir + 'gameFiles/')
shutil.copytree('otherFiles/', installDir + 'otherFiles/')
shutil.copy('README.md', installDir + "/README.txt")

shutil.make_archive("target/" + installName, "zip", 'target', installName + "/")