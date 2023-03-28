# Usage: in the terminal:
# $ python3 average.py [directory] [amount of files per month]
# Will return dictionary with data and list of skipped files
# Command ran for the paper:
# $ python3 average.py /net/corpora/twitter2/Tweets 10
# This resulted in 10 files per month per year being used as data

import os
import sys
import gzip
import json
import time

# Initialising variables used for the data
# The dictionary in which average tweet and average word length will be
data = {}
# Number of words, not in the paper but an interesting statistic to see
n_words = 0
# Number of tweets, also not in the paper for the same reason
n_tweets = 0
# Checked files, also not in the paper for the same reason
checked_files = []
# Skipped files, useful for checking if something went wrong
skipped_lines = []

# All code is being run in a try statement to catch a KeyboardInterrupt
# which allowed for stopping the program while still getting an output
try:
    # Time being measured as a nice to have during the coding, to know how long
    # the code is taking and how long the code took overall
    start = time.perf_counter()
    # Loop through all the directories and files in a designated directory
    for root, dirs, files in os.walk(sys.argv[1]):
        # Loop through all the files found that have matching extensions
        for file, i in zip(files, range(int(sys.argv[2]))):
            # If the file extension does not match the file gets skipped
            if file[-7:] != '.out.gz':
                continue
            # Initialising variables used in the rest of the code to store data
            # Number of words for a given file
            file_n_words = 0
            # Number of tweets for a given file
            file_n_tweets = 0
            # The total length of all the words of a file
            file_word_length = 0
            # Thetotal length of all the tweets of a file
            file_tweet_length = 0
            # Time statistic used to show elapsed time
            start_file = time.perf_counter()

            # Loop through all the lines of a file
            for line in gzip.open(root + '/' + file, 'rt'):
                # Deals with exceptions and loads in the text for a
                # given line/tweet
                try:
                    try:
                        json_data = json.loads(line)
                        text = \
                            json_data['data']['extended_tweet']['full_text'] \
                            .encode('utf-8')
                    except KeyError:
                        try:
                            json_data = json.loads(line)
                            text = \
                                json_data['extended_tweet']['full_text'] \
                                .encode('utf-8')
                        except KeyError:
                            try:
                                json_data = json.loads(line)
                                text = \
                                    json_data['data']['text'].encode('utf-8')
                            except KeyError:
                                json_data = json.loads(line)
                                text = json_data['text'].encode('utf-8')
                except json.decoder.JSONDecodeError:
                    skipped_lines.append(line)
                    break

                # Increments the variables after each line
                n_tweets += 1
                file_n_tweets += 1
                file_tweet_length += len(text)

                # Loops through all the words and increments the variables
                # per word
                for word in text.split():
                    n_words += 1
                    file_n_words += 1
                    file_word_length += len(word)

            # Checks whether no divisions with 0 happen
            if (file_n_words or file_n_tweets or
               file_word_length or file_tweet_length) != 0:
                # Handles saving the data on words into a dictionary
                if file[:4] in data:
                    if file[4:6] in data[file[:4]]:
                        if 'Average word is' in data[file[:4]][file[4:6]]:
                            data[file[:4]][file[4:6]]['Average word is'] = \
                                (data[file[:4]][file[4:6]]['Average word is']
                                 + (file_word_length / file_n_words)) / 2
                        else:
                            data[file[:4]][file[4:6]]['Average word is'] = \
                                file_word_length / file_n_words
                    else:
                        data[file[:4]][file[4:6]] = {}
                        data[file[:4]][file[4:6]]['Average word is'] = \
                            file_word_length / file_n_words
                else:
                    data[file[:4]] = {}
                    data[file[:4]][file[4:6]] = {}
                    data[file[:4]][file[4:6]]['Average word is'] = \
                        file_word_length / file_n_words

                # Handles saving the data on tweets into a dictionary
                if file[:4] in data:
                    if file[4:6] in data[file[:4]]:
                        if 'Average tweet is' in data[file[:4]][file[4:6]]:
                            data[file[:4]][file[4:6]]['Average tweet is'] = \
                                (data[file[:4]][file[4:6]]['Average tweet is']
                                 + (file_tweet_length / file_n_tweets)) / 2
                        else:
                            data[file[:4]][file[4:6]]['Average tweet is'] = \
                                file_tweet_length / file_n_tweets
                    else:
                        data[file[:4]][file[4:6]] = {}
                        data[file[:4]][file[4:6]]['Average tweet is'] = \
                            file_tweet_length / file_n_tweets
                else:
                    data[file[:4]] = {}
                    data[file[:4]][file[4:6]] = {}
                    data[file[:4]][file[4:6]]['Average tweet is'] = \
                        file_tweet_length / file_n_tweets

            # Appends the file to checked_files once done with the file
            checked_files.append(file)

            # Status message printed when running the code
            print('Files checked:', len(checked_files), '/',
                  179 * int(sys.argv[2]), '-',
                  round((len(checked_files) /
                         (179 * int(sys.argv[2]))) * 100, 2), '%', '-',
                  round(time.perf_counter() - start, 2), 'seconds elapsed')

    # Rounding the values for presentation
    for year in data:
        for month in data[year]:
            for value in data[year][month]:
                data[year][month][value] = round(data[year][month][value], 2)

    # Storing the data into a file
    with open('output.txt', 'w') as outfile:
        print(data, file=outfile)
        print(skipped_lines, file=outfile)

    print(f'Took {time.perf_counter() - start:.2f} seconds')
    print(f'Checked {n_words} words and {n_tweets} tweets')

# Handles the exception when the code is interrupted so that the data does not
# get lost
except KeyboardInterrupt:
    for year in data:
        for month in data[year]:
            for value in data[year][month]:
                data[year][month][value] = round(data[year][month][value], 2)

    with open('output.txt', 'w') as outfile:
        print(data, file=outfile)
        print(skipped_lines, file=outfile)
