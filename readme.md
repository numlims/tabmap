# tabmap: db table map

```
tabmap db_target --latex > tables.tex
lualatex tables.tex
```

## install

download tabmap whl from
[here](https://github.com/numlims/tabmap/releases). install whl with
pip:

```
pip install tabmap-<version>.whl
```

see [dbcq](https://github.com/numlims/dbcq?tab=readme-ov-file#db-connection) for database connection setup.

## notes

you can add notes for tables and columns via yaml like this:

```
tabmap db_target --latex --notes mynotes.yaml > tables.tex
```

see notes-exmpl.yaml for format.