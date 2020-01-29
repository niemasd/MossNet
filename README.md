# MossNet
MossNet is a Python package for performing network analyses on MOSS results.

## Installation
MossNet can be installed using `pip`:

```bash
sudo pip install mossnet
```

If you are using a machine on which you lack administrative powers, MossNet can be installed locally using `pip`:

```bash
pip install --user mossnet
```

## Usage
Example usage is as follows:

```python
from mossnet import build # load mossnet
moss_URLs = [...] # one URL for each MOSS report for each file for this assignment
mn = build(moss_URLs) # creates MossNet object
mn.export("html_output", style='html', verbose=True) # output HTML reports for each pair of students
mn.save("my_mossnet.pkl") # save MossNet object in "my_mossnet.pkl"
```

Full documentation can be found at [https://niemasd.github.io/MossNet/](https://niemasd.github.io/MossNet/), and more examples can be found in the [MossNet Wiki](https://github.com/niemasd/MossNet/wiki).
