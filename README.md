# Adapting a _Query by Example algorithm_ for MIDI files

The code in this repository can be run to:
- Segment MIDI files to create an index (`segment.py`)
- Run query by example with a created index and a given query MIDI (`query_file.py`)
- Create query MIDIs based on various strategies (`create_query_midis.py`)
- Run a set of created query MIDIs through the algorithm and calculate accuracy and performance metrics (`server.py` 
  and `query_client.py`). Some ready made queries exist in the folder mid/queries/
- Run a demo showing how the graph algorithm works (`jupyter notebook`, then open `demo.ipynb`. 
  Alternatively VS Code has extensions to run .ipynb notebooks)
- A script demonstrating everything in the project (`test_components.py`)
  
Running e.g. `segment.py -h` will give more information on how each script works.

## Installation

1. Install Python >= 3.7 first (if it's not already installed). Make sure python is on your `PATH`
2. Create a *virtual environment*, so the Python packages installed here don't
interfere with your system wide packages:
  
```
python -m venv venv
```
- *Activate* the virtual environment (this stays activated in the same command window):
```
venv\Scripts\activate.bat # windows (CMD)
venv\Scripts\activate.ps1 # windows (PowerShell) (might require admin privileges)
source venv/bin/activate  # UNIX-based
```

You can deactivate a virtual environment via `deactivate`. See [here](https://docs.python.org/3/library/venv.html) for
more info on virtual environments.
3. Ensure the 64-bit version of [Graphviz](https://www.graphviz.org/download/) is installed.
4. Ensure that the python package manager, `pip` is installed, and that `setuptools` is up to date:
```
python -m ensurepip
# if the above doesn't work, try to install pip through your package manager
# sudo apt install python3-pip
pip install --upgrade setuptools
```
5. If on linux, make sure `make` is installed (it should be, but it wasn't
   by default on Ubuntu for whatever reason). If you're on Debian/Ubuntu you 
   also need to `apt install python3-dev` (again this might already be installed)

6. If on Windows, install the package `pygraphviz` first (it can be quite fussy with libraries)
```
python -m pip install --global-option=build_ext --global-option="-IC:\Program Files\Graphviz\include" --global-option="-LC:\Program Files\Graphviz\lib" `
              pygraphviz
```
It might ask for Visual Studio be downloaded as well at this point.
   
7. Install the rest of the requirements:
```
pip install -r requirements.txt
```
8. Run the scripts above!

## Notes

- The demo.ipynb notebook may take some setup to run (for example, installing MuseScore).
The output of each cell should be visible anyway so that should be sufficient
- The output index from `segment.py` is contained in `mid\generated\<algorithm>` When running
`query_file.py`, the `dataset` is relative to this folder (so if running `query_file.py` with `--algorithm pitch_vector`
  the `dataset` argument should be a folder contained in `mid\generated\pitch_vector`)
- You can see what indexed datasets are able to be used with `server.py` with the switch `--list_indexes`
- Contact me if there are any other issues not listed here.