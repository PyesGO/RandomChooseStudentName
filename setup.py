from cx_Freeze import setup, Executable

# from setuptools import setup
options = dict(
    build_exe=dict(optimize=2, zip_include_packages=["*"], zip_exclude_packages=None)
)
executables = [
    Executable(
        script="test.py",
        target_name="TEST",
        copyright="no copyright",
        base="Win32GUI",
    )
]

setup(name="TEST", executables=executables, options=options)
