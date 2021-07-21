# Adapting a _Query by Example algorithm_ for MIDI files
This is the code portion of my final year project. The goal of this project was to
adapt an existing Query by Example (recognising a song through a song extract) / Melodic
similarity algorithm to work with a different musical format.

Specifically, I adapted Simonetta et al.'s graph  based algorithm (https://dl.acm.org/doi/pdf/10.1145/3243274.3243301)
which used musicXML files, to work with MIDI files. 

My implementation of this algorithm is not the same as Simonetta et al.'s; many of the 
differences come from the change of format from of musicXML (which is a cross-platform format for composition
software such as MuseScore and Sibelius) to MIDI (designed for communication between electronic instruments and 
computers/sequencers etc.). In addition, there are quite a lot of smaller changes. Therefore my implementation
is **not** intended as a "reference" implementation of the algorithm as described in the paper above or 
within its original thesis (http://tesi.cab.unipd.it/59666/1/thesis.pdf).

As a point of comparison, another QBE algorithm was implemented representing each music as a series of
vectors (https://ieeexplore.ieee.org/document/4518093). Locality Sensitive Hashing was used for fast
approximation of nearest neighbour search. 

The accuracy, memory usage and average query time of each algorithm was compared
using a single dataset of MIDI files (the [Nottingham Dataset](http://abc.sourceforge.net/NMD/), available as MIDIs 
[here](https://github.com/jukedeck/nottingham-dataset)), using different types of queries (e.g. some were taken
directly from the song, while others were made "noisy" by changing note lengths/pitches etc.)



### What the code does

The code in this repository can be run to:
- Segment MIDI files to create an index (`segment.py`)
- Run query by example with a created index and a given query MIDI (`query_file.py`)
- Create query MIDIs based on various strategies (`create_query_midis.py`)
- Run a set of created query MIDIs through the algorithm and calculate accuracy and performance metrics (`server.py` 
  and `query_client.py`).
- Run a demo showing how the graph algorithm works (`jupyter notebook`, then open `demo.ipynb`. 
  Alternatively VS Code has extensions to run .ipynb notebooks)
- A script demonstrating everything in the project (`test_components.py`) running in sequence
  
Running e.g. `segment.py -h` will give more information on how each script works 
(except) for `test_components.py` which doesn't take any arguments anyway

### Important note
As the project currently stands only *monophonic* MIDI files (i.e. where the melody track has only one note played
at any time) so please keep this in mind if you get any errors.

## Running the code

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
python -m pip install --global-option=build_ext --global-option="-IC:\Program Files\Graphviz\include" --global-option="-LC:\Program Files\Graphviz\lib" pygraphviz
```
It might ask for Visual Studio Build tools be downloaded as well (if its not already installed)
   
7. Install the rest of the requirements:
```
pip install -r requirements.txt
```
8. Run the scripts above!

9. (Optional) to use the dataset I used (nottingham), download it from 
   [here](https://github.com/jukedeck/nottingham-dataset) (the "MIDI" folder specifically) and extract the contents
   into the folder mid/nottingham.

## Notes

- The demo.ipynb notebook may take some setup to run (for example, installing MuseScore).
The output of each cell should be visible anyway so that should be sufficient
- The output index from `segment.py` is contained in `mid\generated\<algorithm>` When running
`query_file.py`, the `dataset` is relative to this folder (so if running `query_file.py` with `--algorithm pitch_vector`
  the `dataset` argument should be a folder contained in `mid\generated\pitch_vector`)
- You can see what indexed datasets are able to be used with `server.py` with the switch `--list_indexes`
- Contact me if there are any other issues not listed here. From trying to get this set up
on different systems with different Operating Systems, I've tried to note all the points where it wrong for me.

## Example commands

- Segmenting: `python segment.py -o test --algorithm pitch_vector --melody_track 0 --n_processes 2 mid\nottingham\*.mid`
- Creating queries `python create_query_midis.py --rng_seed 0 mid\nottingham 100 test_queries indexed --algorithm pitch_vector --melody_track 0`
- Query server `python server.py --graph_index none --pv_index test --pv_veclength 8`
- Query client `python query_client.py --melody_track 0 pitch_vector test_queries`
