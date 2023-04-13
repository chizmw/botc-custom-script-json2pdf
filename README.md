# json2pdf for Blood on The Clocktower

Yet Another Custom Script Generator for [Blood on the Clocktower][botc]

## Requirements

- `python` 3.11, or newer
- `poetry`
- `make` is strongly recommended, but you can skip it if you know what your doing

## Usage

### Sanity Check

The easiest way to get started is to generate a copy of the Trouble Brewing script:

```sh
make tb
```

Generated files are saved in the [`pdfs/`](pdfs/) directory.

### Single Script

To generate a PDF for a custom script, download the JSON, and use `make
process`. For example:

```sh
make process INPUT_FILE="scripts/No Roles Barred.json"
```

### All Scripts

To generate PDF files for all files in the [`scripts`](scripts/) directory you
can use:

```sh
make all-scripts
```

## Acknowledgements

Clearly I wouldn't be doing any of this without the existence of
[Blood on the Clocktower][botc], or the existence of [custom scripts][botc-scripts].

I always aspire to take something and make it better (for some value of better)
so after seeing the functional PDFs generated from the [script
tool][botc-scripts] and later the beauty of the [No Roles Barred][script-nrb] I
went on a personal quest to try to generate "beautiful" PDFs from the tool's
JSON.

I stumbled across [LectronPusher's generator][botc-generator] and thought, "I
could tweak this, and be done". I soon realised that life is too short to learn
[LaTeX][latex] and after a pause to ruminate I decided to pull the best parts
together and sprinkle some Chisel-magic into the mix.

For better or worse, this project is the result of that desire.

## Attribution

- `roles.json` and game icons
  - [LectronPusher/botc-custom-script-generator][botc-generator]
  - … which were originally from [bra1n's townsquare](https://github.com/bra1n/townsquare)
- other icons
  - [Sunrise](https://uxwing.com/sunrise-icon/)
  - [[D]emon](https://uxwing.com/d-alphabet-icon/)
  - [[M]inion](https://uxwing.com/m-alphabet-icon/)
- [Fira Sans font family](https://www.1001fonts.com/fira-sans-font.html)

<!-- markdown links -->

[botc]: https://bloodontheclocktower.com/
[botc-scripts]: https://script.bloodontheclocktower.com/
[botc-generator]: https://github.com/LectronPusher/botc-custom-script-generator
[latex]: https://www.latex-project.org/
[script-nrb]: https://botc-scripts.azurewebsites.net/script/258/1.0.1
