# <routine-name>

> One-line purpose.

## Schedule

`<cron expr>` — when this fires.

## Inputs

- list of files / APIs / cookies this needs

## Outputs

- list of files / inbox seeds / log entries

## How to install

```
bash launchd/install.sh
launchctl print gui/$UID/com.tlx.<routine-name>
```

## How to uninstall

```
bash launchd/uninstall.sh
```

## Manual run

```
bash routine.sh           # production
bash routine.sh --dry-run # no writes
bash routine.sh --debug   # verbose
```

## Failure recovery

(what to do when `_log.jsonl` shows an error)
