# augpath

Build output paths from input paths. `augpath` is a small command-line wrapper around `boltons.pathutils.augpath`.

In bioinformatics, format conversions, renames, and moves often start with the same shell task: derive an output filename from each input filename. In a GNU Parallel pipeline, that can mean a dense `sed` or `awk` expression just to swap an extension or change a directory. `augpath` gives those operations names and keeps paths flowing as text through the pipeline. It prints the resulting paths so the next command can use them.

## Install

From the project checkout, with [uv](https://docs.astral.sh/uv/) installed:

```sh
uv tool install .
augpath --help
```

If your shell can't find `augpath`, run `uv tool update-shell` and open a new terminal. To try it from the checkout, run `uv run augpath --help`.

## Examples

Treat `.fastq.gz` as a single extension when adding a suffix:

```sh
augpath --multidot --suffix _trimmed reads/sample.fastq.gz
# reads/sample_trimmed.fastq.gz
```

Keep the sample ID and input path, and insert a BAM path after field 2:

```sh
printf '%s\n' 'sample01|reads/sample01.sam' |
  augpath --delimiter '|' --field 2 --append --dpath alignments --ext .bam
# sample01|reads/sample01.sam|alignments/sample01.bam
```

Generate input/output pairs for GNU Parallel and convert SAM to BAM with `samtools`:

```sh
mkdir -p alignments
find reads -type f -name '*.sam' |
  augpath --append --dpath alignments --ext .bam |
  parallel --colsep '\t' samtools view -b -o '{2}' '{1}'
```

The last example assumes filenames contain neither tabs nor newlines and have unique basenames, since all outputs go into one directory.

By default, stdin and stdout use one record per line. Use `-0` for NUL-delimited records, such as input from `find -print0`. With `--field` or `--append`, the field separator defaults to a tab. Field numbers start at 1.

Generate shell completions with `augpath --print-completion zsh` or pass your shell name. See `augpath --help` for the available shells.
