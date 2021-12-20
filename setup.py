import sys, cx_Freeze

cx_Freeze.setup(
    name="Java City",
    version="0.1",
    description="The beautiful solution for your all of your Java Town problems",
    options={
        "build_exe": {
            "packages": ['os', 'sys', 'pyperclip', 'json', 're', 'pygame'],
            "include_files": ["colorpallete.json", "default color palletes", "JavaCity.png"]
        },
        "bdist_mac": {
            "iconfile": "JavaCity.icns",
            "bundle_name": "JavaCity"
        }
    },
    executables = [
        cx_Freeze.Executable("javaCity.py", base='Win32GUI' if sys.platform == 'win32' else None)
    ]
)

# python3 setup.py bdist_mac