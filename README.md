# log-weave

Merge several already-sorted log files into one chronological stream without loading all lines into memory. Each line must start with a timezone-aware ISO 8601 timestamp; timestamps from different UTC offsets are compared as instants.

## Use

Requires Python 3.8+; no packages to install.

```sh
python log_weave.py app-a.log app-b.log > merged.log
python log_weave.py edge-west.log edge-east.log
```

Examples of accepted prefixes are `2026-10-02T09:12:34Z` and `2026-10-02T17:12:34+08:00`. Every input must be sorted oldest first. The tool checks ordering as it reads; if a later line is malformed or out of order, it exits with an error and may already have written earlier merged lines to standard output. It reads local files only and does not contact a network.

## License

MIT
