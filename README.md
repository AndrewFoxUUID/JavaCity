The beautiful solution for your all of your Java Town problems<br>
@author Andrew Fox (class of 2023)<br>
@version 0.1 (12/19/21)

This simplified Java interpreter was built in pure Python using Pygame.
In order to generate an application, run 
`python3 setup.py bdist_mac` for mac (you might then have a codesign error, you will need to run `codesign --remove-signature JavaCity.app/Contents/MacOS/lib/Python`. if you do not have codesign, you will need to download the xcode cli dev kit)
`python3 setup.py bdist_msi` for windows
to generate a simple executable for any platform, run `python3 setup.py build`.
An executable will be in the generated directory that you can run directly.
everything will be created in the "build/" directory

To change the color pallete, edit colorpallete.json, some defaults are in the
"default color palletes" folder

a default Java file has been provided, aptly named "Test.java"

to just run the python, run `python javaCity.py`

Note: Arrays, Libraries, and Interfaces are not supported in JavaCity. It is also single class.