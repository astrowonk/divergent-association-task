# sqlite database created dat.db
#
# make table with CREATE TABLE glove (word text primary key, data text not null);

import re
import sqlite3
from tqdm import tqdm
from umap import UMAP
import numpy as np
import pandas as pd

from sqlalchemy import create_engine, text
#model =
dictionary = 'words.txt'
pattern = r"^[a-z][a-z-]*[a-z]$"


def write_glove_to_sql(model="glove.840B.300d.txt"):
    words = set()
    ## get dictionary into memory
    with open(dictionary, "r") as f:
        for line in tqdm(f):
            if re.match(pattern, line):
                words.add(line.rstrip("\n"))

    #open connection and write to database line by line. Probably could open zip file directly with ZipFile though not sure coud work
    # line by line.
    con = sqlite3.connect('dat.db')
    cur = con.cursor()
    with open(model, "r") as f:
        for line in f:
            tokens = line.split(" ", maxsplit=1)
            word = tokens[0]
            if word in words:
                # just adds two text colunms, will process the data column in dat.py
                cur.execute("insert into glove (word, data) values (?, ?)",
                            (word, tokens[1].strip()))
        con.commit()
    cur.close()
    con.close()


def shrink_glove_model_file(model='glove.840B.300d.txt'):
    '''This should shrink the 2GB+ glove text file to 270MB by matching with the hunspell dictionary'''
    words = set()

    #read in hunspell based dictionary
    with open(dictionary, "r") as f:
        for line in f:
            if re.match(pattern, line):
                words.add(line.rstrip("\n"))
    with open('new_model.txt', 'wt') as gf:
        with open(model, "r") as f:
            i = 0
            for line in tqdm(f):
                i = i + 1
                tokens = line.split(" ")
                #only write lines that match the Hunspell dictionary\
                if tokens[0] in words:
                    gf.write(line)


def create_umap_table_sql(model='new_model.txt',
                          random_state=42,
                          n_neighbors=15,
                          **kwargs):
    """This works but perhaps the word list needs to be filtered down even more.  Words like 'fifty-fith' occupy an outlier island of umap coords. """
    umap_model = UMAP(n_neighbors=n_neighbors, random_state=random_state)

    #reading vectors
    print("reading vectors and names from text file")
    names = np.genfromtxt('new_model.txt',
                          delimiter=' ',
                          usecols=0,
                          dtype='str')
    #grab everything but the words
    usecols = list(range(1, 301))

    vectors = np.genfromtxt(model, delimiter=' ', usecols=usecols)
    print("creating umap")
    transformed_data = umap_model.fit_transform(vectors, **kwargs)
    umap_df = pd.DataFrame(transformed_data, index=names,
                           columns=['A', 'B']).reset_index()
    dbc = create_engine("sqlite:///dat.db")
    print('uploading to sql')
    umap_df.rename({
        'index': 'word'
    }, axis=1).to_sql('umap', con=dbc, index=False, if_exists='replace')
    return umap_df