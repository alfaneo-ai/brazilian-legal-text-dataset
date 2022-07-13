#!/bin/bash

get_seeded_random()
{
  seed="$1"
  openssl enc -aes-256-ctr -pass pass:"$seed" -nosalt \
    </dev/zero 2>/dev/null
}

shuf -n 1000 -o corpus_dev.txt --random-source=<(get_seeded_random 42) corpus.txt

shuf -n 2000 -o corpus_train.txt --random-source=<(get_seeded_random 71) corpus.txt
