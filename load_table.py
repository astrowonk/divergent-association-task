# sqlite database created dat.db
#
# make table with CREATE TABLE glove (word text primary key, data text not null);

import re
import sqlite3

model = "glove.840B.300d.txt"
dictionary = 'words.txt'
pattern = r"^[a-z][a-z-]*[a-z]$"

words = set()
## get dictionary into memory
with open(dictionary, "r") as f:
    for line in f:
        if re.match(pattern, line):
            words.add(line.rstrip("\n"))

#open connection and write to database line by line. Probably could open zip file directly with ZipFile though not sure coud work
# line by line.
con = sqlite3.connect('dat.db')
cur = con.cursor()
with open(model, "r") as f:
    i = 0
    for line in f:
        tokens = line.split(" ", maxsplit=1)
        word = tokens[0]
        if word in words:
            cur.execute("insert into glove (word, data) values (?, ?)",
                        (word, tokens[1].strip()))
    con.commit()
cur.close()
con.close()
