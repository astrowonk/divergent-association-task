"""Compute score for Divergent Association Task,
a quick and simple measure of creativity
(Copyright 2021 Jay Olson; see LICENSE)"""

import re
import itertools
import numpy as np
import scipy.spatial.distance
from sqlalchemy import create_engine, text


class Model:
    """Create model to compute DAT"""
    def __init__(self,
                 model="dat.db",
                 dictionary="words.txt",
                 pattern="^[a-z][a-z-]*[a-z]$"):
        """Join model and words matching pattern in dictionary"""

        # Keep unique words matching pattern from file
        self.words = set()
        with open(dictionary, "r") as f:
            for line in f:
                if re.match(pattern, line):
                    self.words.add(line.rstrip("\n"))

        # Join words with model
        self.dbc = create_engine("sqlite:///dat.db")

    def get_vectors_from_sql(self, word):
        with self.dbc.connect() as conn:
            result = conn.execute(
                text(f"select word, data from glove where word = :word", ),
                {'word': word})
            _, data = result.fetchone()
            return np.array([float(x) for x in data.split(" ")])

    def validate(self, word):
        """Clean up word and find best candidate to use"""

        # Strip unwanted characters
        clean = re.sub(r"[^a-zA-Z- ]+", "", word).strip().lower()
        if len(clean) <= 1:
            return None  # Word too short

        # Generate candidates for possible compound words
        # "valid" -> ["valid"]
        # "cul de sac" -> ["cul-de-sac", "culdesac"]
        # "top-hat" -> ["top-hat", "tophat"]
        candidates = []
        if " " in clean:
            candidates.append(re.sub(r" +", "-", clean))
            candidates.append(re.sub(r" +", "", clean))
        else:
            candidates.append(clean)
            if "-" in clean:
                candidates.append(re.sub(r"-+", "", clean))
        for cand in candidates:
            if cand in self.words:
                return cand  # Return first word that is in model
        return None  # Could not find valid word

    def distance(self, word1, word2):
        """Compute cosine distance (0 to 2) between two words"""

        return scipy.spatial.distance.cosine(self.get_vectors_from_sql(word1),
                                             self.get_vectors_from_sql(word2))

    def dat(self, words, minimum=7):
        """Compute DAT score"""
        # Keep only valid unique words
        uniques = []
        for word in words:
            valid = self.validate(word)
            if valid and valid not in uniques:
                uniques.append(valid)

        # Keep subset of words
        if len(uniques) >= minimum:
            subset = uniques[:minimum]
        else:
            return None  # Not enough valid words

        # Compute distances between each pair of words
        distances = []
        for word1, word2 in itertools.combinations(subset, 2):
            dist = self.distance(word1, word2)
            distances.append(dist)

        # Compute the DAT score (average semantic distance multiplied by 100)
        return (sum(distances) / len(distances)) * 100
