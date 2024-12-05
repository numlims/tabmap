from tbl import tbl

# maketext returns table summary text
# is it prudent to pass the target or rather tbl?
def maketext(target:str) -> str:
    # start tbl
    t = tbl(target)

    out = ""
    
    tables = t.tables()
    tables.sort() # todo: removing the centraxx_ prefix afterwards for some tables undos the sorting
    # for each table
    for table in tables:
        out += t.tablesummary(table)

    return out

# makelatex returns table summary as latex
def makelatex(target:str) -> str:
    out = ""

    # latex head
    out += r"""\documentclass[12pt]{article}

% helvetica font
\usepackage[scaled]{helvet}
\usepackage[T1]{fontenc}
\renewcommand\familydefault{\sfdefault}

\usepackage[hidelinks]{hyperref}

\begin{document}

% no parindents
\setlength{\parindent}{0cm}"""
    out += "\n"

    # start tbl
    t = tbl(target)

    # get fks
    fks = t.fk()
    fkfromtc = t.fkfromtc(fks)
    fktotc = t.fktotc(fks)

    # columns by table
    columns = t.columns()

    tables = t.tables()
    tables.sort() # todo: removing the centraxx_ prefix afterwards for some tables undos the sorting
    # for each table
    for table in tables:
        # piece together the latex layout
        # see trytex/trylayout.tex for example

        # introduce phantomsection line, so that referencenes referring to labels in here land on this line, not in parent section
        out += "\\phantomsection\n"
        # the table name
        out += totex(table.upper())
        # two blanks
        out += "\\ \\ "
        
        # print fields that are not fk
        if table in columns:
            columns[table].sort()
        for column in columns[table]:
            if not (table in fkfromtc and column in fkfromtc[table]):
                # display name
                out += totex(column.lower())
                # label name
                out += "\\label{" + table + "." + column.lower() + "}" # todo shouldn't lowercase be guaranteed?
                # space
                out += " "
        # two line breaks
        out += "\\\\ \n"
        out += "\\\\ \n"

        # outgoing foreign keys from this table
        if table in fkfromtc:
            cols = list(fkfromtc[table].keys())
            cols.sort()
            # print("from")
            for column in cols:
                fk = fkfromtc[table][column][0]
                # introduce a phantom section on each line, so that incoming links land right here
                out += "\\phantomsection\n"
                # blanks at the beginning of line don't seem to work, use hspace
                out += "\\hspace*{2em}"
                # the column name
                out += totex(fk.fc.lower())
                # label for incoming links
                out += "\\label{" + table + "." + fk.fc.lower() + "}"
                # two blanks
                out += "\\ \\ "
                # the outgoing link
                tt = fk.tt.lower()
                tc = fk.tc.lower()
                out += "\\hyperref[" + tt + "." + tc + "]{"
                # the text in the outgoing link
                out += totex(tt + "." + tc)
                # closing of the link
                out += "}"
                # line break
                out += "\\\\ \n"
            out += "\\\\ \n"

        # incoming foreign keys to this table
        if table in fktotc and len(fktotc[table]) > 0:
            # sort
            a = list(fktotc[table].keys())
            a.sort()
            # print by to-field
            for column in a:
                # half of hspace
                out += "\\hspace*{1em}"
                # column name
                out += "to " + column.lower() + ":"
                # line break
                out += "\\\\ \n"
                
                # sort by from-table
                fktotc[table][column].sort(key=lambda x: x.ft)
                for fk in fktotc[table][column]:
                    # no phantom section needed, cause no incoming links to here?
                    # maybe doch? from where the column names are introduced to here?
                    
                    # hspace
                    out += "\\hspace*{2em}"
                    # from-table, from-column
                    ft = fk.ft.lower()
                    fc = fk.fc.lower()
                    # outgoing link
                    out += "\\hyperref[" + ft + "." + fc + "]{"
                    # link text
                    out += totex(ft + "." + fc)
                    # close link
                    out += "}"
                    # line break
                    out += "\\\\ \n"
            # line break
            out += "\\\\ \n"

        # line break
        out += "\\\\ \n"

    # document tail
    out += r"""
\end{document}
        """

    return out

# totex returns tex-usable string (escaped underscores in this case)
def totex(s):
    return s.replace("_", "\\_")
