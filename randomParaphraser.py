import random
import time
import requests
import functools
from concurrent.futures import ThreadPoolExecutor
import os
from multiprocessing import Pool, cpu_count
from typing import List, Dict

#Defining Some Constants
DATAMUSE_API_URL = "https://api.datamuse.com/words"
REQUEST_TIMEOUT = 10  # seconds
MAX_PARAPHRASES = 5  # Results to request
MAX_RETRIES = 2  # Max retry attempts if failure
MAX_WORKERS = 4  # For parallel processing



def execution_time_decorator(func):
    """Decorator to measure and log function execution time"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        try:
            print(f"Starting: {func.__name__}")
            result = func(*args, **kwargs)
            elapsed = time.perf_counter() - start_time
            print(f"Finished {func.__name__} in {elapsed:.2f}s")
            return result
        except Exception as e:
            print(f"Error in {func.__name__}: {str(e)}")
            raise
    return wrapper



#@execution_time_decorator
def get_paraphrases(word: str) -> List[str]:
    """
    Get semantic paraphrases from Datamuse API with retry logic
    Args:
        word: The word to find paraphrases for
    Returns:
        List of paraphrase words (empty list if failed)
    """
    params = {'ml': word, 'max': MAX_PARAPHRASES}  
    
    for attempt in range(MAX_RETRIES + 1):
        try:
            response = requests.get(
                DATAMUSE_API_URL,
                params=params,
                timeout=REQUEST_TIMEOUT
            )
            response.raise_for_status()
            return [item['word'] for item in response.json() if 'word' in item]
        
        except requests.exceptions.RequestException as e:
            if attempt == MAX_RETRIES:
                print(f"⚠️ Failed to paraphrase '{word}' (attempts: {attempt + 1})")
                return []
            time.sleep(1 * (attempt + 1))  
    
    return []



def batch_get_paraphrases(words: List[str]) -> Dict[str, List[str]]:
    """
    Get paraphrases for multiple words in parallel
    Args:
        words: List of words to paraphrase
    Returns:
        Dictionary mapping original words to their paraphrases
    """
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        results = dict(zip(words, executor.map(get_paraphrases, words)))
    return {word: paraphrases for word, paraphrases in results.items() if paraphrases}



def paraphrase_sentence(sentence: str, words_to_replace: List[str]) -> str:
    """
    Replace target words with random paraphrases while maintaining:
    - Original word if no paraphrase found
    - Proper spacing and punctuation
    """
    if not words_to_replace:
        return sentence
    
    # Get all paraphrases at once
    paraphrase_map = batch_get_paraphrases(words_to_replace)
    
    # Rebuild sentence with replacements
    output_words = []
    for word in sentence.split():
        # Check both original and lowercase version
        original_word = word.rstrip('.,!?;:')  # Remove trailing punctuation
        key = original_word if original_word in paraphrase_map else None
        
        if key:
            replacement = random.choice(paraphrase_map[key])
            # Preserve original capitalization and punctuation
            if word[0].isupper():
                replacement = replacement.capitalize()
            if word[-1] in '.,!?;:':
                replacement += word[-1]
            output_words.append(replacement)
        else:
            output_words.append(word)
    
    return ' '.join(output_words)



#@execution_time_decorator
def paraphrase_paragraph(paragraph: str, words_to_replace: List[str]) -> str:
    """Process each sentence in a paragraph while preserving structure"""
    sentences = [s.strip() for s in paragraph.split('.') if s.strip()]
    processed = [
        paraphrase_sentence(s, words_to_replace)
        for s in sentences
    ]
    return '. '.join(processed) + ('.' if paragraph.endswith('.') else '')



def paraphrase_document(input_path: str, output_path: str, words_to_replace: List[str]) -> None:
    """
    Process an entire document file with parallel paragraph processing
    Args:
        input_path: Path to input text file
        output_path: Path to save paraphrased document
        words_to_replace: List of target words to paraphrase
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    with open(input_path, 'r') as f:
        document = f.read()
    
    paragraphs = [p.strip() for p in document.split('\n\n') if p.strip()]
    
    with Pool(processes=min(cpu_count(), 4)) as pool:
        results = pool.starmap(
            paraphrase_paragraph,
            [(para, words_to_replace) for para in paragraphs]
        )
    
    paraphrased_doc = '\n\n'.join(results)
    
    with open(output_path, 'w') as f:
        f.write(paraphrased_doc)
    print(f"Successfully processed {len(paragraphs)} paragraphs to {output_path}")


def main():
    try:
        input_file = "document.txt"
        output_file = "paraphrased_document.txt"
        target_words = ["quick", "brown", "fox", "lazy", "dog"]
        
        if not os.path.exists(input_file):
            print(f"Error: Input file '{input_file}' not found")
            return
        
        print(f"Processing document with target words: {', '.join(target_words)}")
        paraphrase_document(input_file, output_file, target_words)
        print("Document processing complete!")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")

    #"""Example usage"""
    #test_text = (
    #    "The quick brown fox jumps over the lazy dog. "
    #    "This sentence contains all english letters."
    #)
    #target_words = ["quick", "brown", "fox", "lazy", "dog"]
    
    #print("Original:")
    #print(test_text)
    
    #print("\nParaphrased:")
    #result = paraphrase_paragraph(test_text, target_words)
    #print(result)

if __name__ == "__main__":
    main()