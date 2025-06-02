import requests
import random
import functools
import time

def execution_time_decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"Calling: {func.__name__}")
        start_time = time.perf_counter()
        val = func(*args, **kwargs)
        end_time = time.perf_counter()
        elapsed_time = end_time - start_timgie
        print(f"The Function {func.__name__} Took {elapsed_time} seconds to finish executing")
        return val
    return wrapper

#@execution_time_decorator 
def get_rhymes(word):
    baseurl = "https://api.datamuse.com/words"
    params_diction = {}
    params_diction["rel_rhy"] = word
    params_diction["max"] = "3"
    resp = requests.get(baseurl, params=params_diction)
    word_ds = resp.json()
    return [d['word'] for d in word_ds]

def get_random_rhyme(lst_of_rhyming_words):
    return random.choice(lst_of_rhyming_words) if lst_of_rhyming_words else None

def rhyme_sentence(sentence_to_be_rhymed, *words_to_be_changed):
    if len(words_to_be_changed) == 0: 
        return sentence_to_be_rhymed
        
    words_and_rhymes = {}
    for word in words_to_be_changed:
        rhymes = get_rhymes(word)
        if rhymes: 
            random_singular_rhyme = get_random_rhyme(rhymes)
            words_and_rhymes[word] = random_singular_rhyme

    words_in_sentence = sentence_to_be_rhymed.split(" ")
    words_of_rhymed_sentence = []
    for word in words_in_sentence:
        words_of_rhymed_sentence.append(words_and_rhymes.get(word, word))
    
    return ' '.join(words_of_rhymed_sentence)

def rhyme_paragraph(paragraph_to_be_rhymed, *words_to_be_changed):
    sentences_of_paragraph = paragraph_to_be_rhymed.split("\n")
    rhymed_sentences = []
    for sentence in sentences_of_paragraph:
        rhymed_sentence = rhyme_sentence(sentence, *words_to_be_changed)
        rhymed_sentences.append(rhymed_sentence)
    
    return "\n".join(rhymed_sentences)

rhymes = get_rhymes("funny")
print(f"Top 3 Rhymes: {rhymes}")
random_rhyme = get_random_rhyme(rhymes)
print(f"Randomly Chosen Rhyme: {random_rhyme}")

test_sentence = "The funny bunny ate honey in the sunny afternoon"
print(rhyme_sentence(test_sentence, "funny", "bunny", "honey", "sunny"))