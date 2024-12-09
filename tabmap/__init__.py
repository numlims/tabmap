import yaml
from tbl import tbl
from dip import dig

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
def makelatex(target:str, annotations:dict) -> str:
    out = ""

    # latex head
    out += r"""\documentclass[12pt]{article}

% helvetica font
\usepackage[scaled]{helvet}
\usepackage[T1]{fontenc}
\renewcommand\familydefault{\sfdefault}

% text color
\usepackage{xcolor}

% clickable links
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
        # if there's a note for this table, put it in
        note = dig(annotations, table + "/note")
        if note:
            out += "\\textit{// " + totex(note) + "}"
            # new line
            out += "\\\\ \n"
        # prefix table name with # so it's easier to search for it
        # is there color?
        color = dig(annotations, table + "/color")
        if color:
            out += "\\textcolor{" + color + "}{"
        out += "\\#" + totex(table.upper())
        # close color:
        if color:
            out += "}"
        # two blanks
        out += "\\ \\ "
        
        # print fields that are not fk
        # collect the notes of these fields
        notes = "\\textit{"
        hasnotes = False
        if table in columns:
            columns[table].sort()
        for column in columns[table]:
            if not (table in fkfromtc and column in fkfromtc[table]):
                # was there a color?
                color = dig(annotations, table + "/columns/" + column + "/color")
                if color:
                    out += "\\textcolor{" + color + "}{"
                # display name
                out += totex(column)
                # close color
                if color:
                    out += "}"
                # label name
                out += "\\label{" + table + "." + column + "}" # todo shouldn't lowercase be guaranteed?
                # space
                out += " "
                note = dig(annotations, table + "/columns/" + column + "/note")
                if note:
                    # wrap note in color?
                    if color:
                        out += "\\textcolor{" + color + "}{"
                    # note text
                    notes += "// " + totex(note)
                    # close color
                    if color:
                        out += "}"
                    # linebreak
                    notes += "\\\\"
                    hasnotes = True
        # close notes. do they take up a line when they are empty?
        notes += "}"
        # two line breaks
        out += "\\\\ \n"
        out += "\\\\ \n"
        if hasnotes:
            out += "\\hspace*{2em}" + notes
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
                # if there's a note, print it
                note = dig(annotations, table + "/columns/" + column + "/note")
                if note:
                    # indent
                    out += "\\hspace*{2em}"
                    # annotation text
                    out += "\\textit{// " + totex(note) + "}"
                    # line break
                    out += "\\\\"
                # blanks at the beginning of line don't seem to work, use hspace
                out += "\\hspace*{2em}"
                # is there color
                color = dig(annotations, table + "/columns/" + column + "/color")
                if color:
                    out += "\\textcolor{" + color + "}{"
                # the outgoing column name
                out += totex(fk.fc.lower())
                # close color
                if color:
                    out += "}"
                # label for incoming links
                out += "\\label{" + table + "." + fk.fc.lower() + "}"
                # two blanks
                out += "\\ \\ "
                # the outgoing link
                tt = fk.tt.lower()
                tc = fk.tc.lower()
                out += "\\hyperref[" + tt + "." + tc + "]{"
                # the text in the outgoing link
                out += colortabcol(annotations, tt, tc)
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
                    out += colortabcol(annotations, ft, fc)
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

# colortabcol gives seperate colors to table and field if given. if only one color is given, color the whole line this way
def colortabcol(annotations, table, column):
    out = ""
    tablecolor = dig(annotations, table + "/color")
    columncolor = dig(annotations, table + "/columns/" + column + "/color")
    
    # color the whole line if one of the colors is not given. is that cool?
    if (tablecolor and not columncolor) or (not tablecolor and columncolor):
        color = tablecolor
        if color is None:
            color = columncolor
        out += "\\textcolor{" + color + "}{"
        out += totex(table)
        out += "."
        out += totex(column)
        # close color
        out += "}"
        return out

    # different colors
    
    if tablecolor:
        out += "\\textcolor{" + tablecolor + "}{"
    # table name
    out += totex(table)
    # close color
    if tablecolor:
        out += "}"

    # seperating dot
    out += "."

    # different colors
    if columncolor:
        out += "\\textcolor{" + columncolor + "}{"
    # table name
    out += totex(column)
    # close color
    if columncolor:
        out += "}"

    return out

# totex returns tex-usable string (escaped underscores in this case)
def totex(s):
    return s.replace("_", "\\_")
