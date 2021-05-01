#!/usr/bin/env python3
'''
main.py
'''

import re

DICTKEY = "./data/dict.txt"
CORPUS = "./data/br-text.txt"
RAWCORPUS = "./data/sherlock.txt"

# Make dictionary for phon repr of words
def proc_dict(f):
    phon_dict = {}
    for line in f:
        groups = re.match(r'(\S*)\s*(.*)', line)
        phon_dict[groups[1]] = re.findall(r'\.(\S+) -w', groups[2])

    return phon_dict

# proc corpus details
def proc_corpus(corpus, phon_dict):
    corpus_orig = ''
    corpus_phon = ''
    corpus_phonwords = set()
    for line in corpus:
        corpus_orig += line
        for word in line.split():
            # avoid words that are just pronounced letters (i.e. abcs)
            if len(phon_dict[word]) == 1:
                corpus_phon += ' ' + phon_dict[word][0]
                corpus_phonwords.add(phon_dict[word][0])
            else:
                corpus_phon += ' _'
        corpus_phon += '\n'

    return corpus_orig, corpus_phon, corpus_phonwords

# proc non-phon corpus
def proc_rawcorpus(corpus):
    corpus_orig = ''
    corpus_words = set()
    for line in corpus:
        # remove web addresses
        line = re.sub(r"(?:http://|https://)?(?:www\.)?[a-z0-9$\-_.+!*'(),]*\.[a-z]{2,4}[a-z0-9$\-_.+!*'(),/]*", "", line, flags=re.I)
        line = re.sub(r"\t", " ", line)
        line = re.sub(r"[^a-z0-9\- \n]", "", line, flags=re.I)
        if line.strip():
            corpus_orig += line

            for word in line.split():
                corpus_words.add(word)

    return corpus_orig, corpus_words

# Make set of all phon characters
def proc_phon_chars(phon_words):
    phon_chars = set()
    for word in phon_words:
        for c in word:
            phon_chars.add(c)

    return phon_chars

# Find following characters of n-grams
def count(phon_word, count_dict, forward=True):
    phon_word = phon_word[::-1] if not forward else phon_word
    for i in range(1, len(phon_word) + 1):
        phon_add = '' if i == len(phon_word) else phon_word[i]
        if phon_word[:i] in count_dict:
            count_dict[phon_word[:i]].add(phon_add)
        else:
            count_dict[phon_word[:i]] = {phon_add}

# some testing
def test(corpus_orig, corpus_phon, count_dict_forward, count_dict_backward):
    line = 1
    print(corpus_orig.split('\n')[line])
    print(corpus_phon.split('\n')[line])
    l_phon = corpus_phon.split('\n')[line].split()
    for word in l_phon:
        #for i in range(1, len(word)):
        #    print('{:6s} {:d}'.format(word[:i],
        #                              len(count_dict_forward[word[:i]])))
        #rword = word[::-1]
        #for i in range(1, len(rword) + 1):
        #    print('{:6s} {:d}'.format(rword[:i],
        #                              len(count_dict_backward[rword[:i]])))

        print('{:6s}  post  pre  tot'.format(''))
        for i in range(1, len(word)):
            bound_word = word[:i] + '|' + word[i:]
            pre = len(count_dict_forward[word[:i]])
            post = len(count_dict_backward[word[:i-1:-1]])
            var_total = pre + post
            print('{:6s}  {:2d}    {:2d}   {:2d}'.format(bound_word, pre,
                                                         post, var_total))

        print('-'*5)

# raw corpus testing
def rawtest(rawcorpus, count_dict_forward, count_dict_backward):
    linenum = 27
    line = rawcorpus.split('\n')[linenum]
    print(line)

    for word in line.split():
        print('{:8s}  post  pre  tot'.format(''))
        for i in range(1, len(word)):
            bound_word = word[:i] + '|' + word[i:]
            pre = len(count_dict_forward[word[:i]])
            post = len(count_dict_backward[word[:i-1:-1]])
            var_total = pre + post
            print('{:8s}  {:2d}    {:2d}   {:2d}'.format(bound_word, pre,
                                                         post, var_total))

        print('-'*5)


# Main
def main():
    # read word->phonological data into dict
    with open(DICTKEY) as f:
        phon_dict = proc_dict(f)

    with open(CORPUS) as f:
        corpus_orig, corpus_phon, corpus_phonwords = proc_corpus(f, phon_dict)

    # get list of phonological characters
    phon_chars = proc_phon_chars(corpus_phonwords)

    # counts
    count_dict_forward = {}
    for i in corpus_phonwords:
        count(i, count_dict_forward, True)

    # TODO: count forward/backward in one loop

    count_dict_backward = {}
    for i in corpus_phonwords:
        count(i, count_dict_backward, False)

    test(corpus_orig, corpus_phon, count_dict_forward, count_dict_backward)

    # non-phon testing
    if True:
        with open(RAWCORPUS) as f:
            rawcorpus_orig, rawcorpus_words = proc_rawcorpus(f)

        # counts
        raw_count_dict_forward = {}
        for i in rawcorpus_words:
            count(i, raw_count_dict_forward, True)

        # TODO: count forward/backward in one loop

        raw_count_dict_backward = {}
        for i in rawcorpus_words:
            count(i, raw_count_dict_backward, False)

        rawtest(rawcorpus_orig, raw_count_dict_forward, raw_count_dict_backward)

if __name__ == "__main__":
    main()
