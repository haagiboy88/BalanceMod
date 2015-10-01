#---------------------------------------------------
# release.py
#     This will compile BalanceMod for the end user.
#----------------------------------------------------

# Imports
import os, sys, shutil, py2exe, subprocess
from distutils.core import setup
from BalanceMod import *

# Configuration
version = str(BalanceMod.version)
installName = 'BalanceMod-' + version

class py2exefix(py2exe.build_exe.py2exe):
	# This hack removes tk85.dll from the list of dlls that don't get bundled, since it can be bundled
	def copy_dlls(self, dlls):
		if 'tk85.dll' in self.dlls_in_exedir:
			self.dlls_in_exedir.remove('tk85.dll')

		# Add tcl85.dll to the list of DLLs that don't get bundled, since it can't be
		if 'tcl85.dll' not in self.dlls_in_exedir:
			self.dlls_in_exedir.append('tcl85.dll')

		py2exe.build_exe.py2exe.copy_dlls(self, dlls)

# Target is where we assemble our final install; dist is where py2exe produces EXEs and their dependencies
if os.path.isdir('target/'):
	shutil.rmtree('target/')
installDir = 'target/' + installName + '/'

# Build BalanceMod using normal py2exe
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

# Remove the Tk demo files, this should always be safe
shutil.rmtree('dist/tcl/tk8.5/demos')
shutil.rmtree('dist/tcl/tk8.5/images')
shutil.rmtree('dist/tcl/tk8.5/msgs')

# Copy the files needed into the installation directory
shutil.copytree('dist/', installDir)
shutil.copytree('gameFiles/', installDir + 'gameFiles/')
shutil.copytree('otherFiles/', installDir + 'otherFiles/')
shutil.copy('README.md', installDir + "/README.txt")

# Make a ZIP file
print "Creating zip archive.."
shutil.make_archive("target/" + installName, "zip", 'target', installName + "/")
print "Generating builds image.."
subprocess.call("python DrawBuilds.py")
print "Done!"