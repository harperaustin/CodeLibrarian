import pandas as pd
import spacy
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from openai import OpenAI
import random


nlp = spacy.load("en_core_web_md")
books = pd.read_csv('classics.csv')

#OPENAI API KEY HERE!!!!!!! 
############################################
client = OpenAI(api_key="YOUR-KEY-HERE!!!!")
############################################




def compare_two_books(book1desc, book2desc):
    """
    This function finds the similarity score between two books based on their description.

    Parameters:
    book1desc, book2desc: a string consisiting of key words that describe a books subject

    Returns:
    A similarity score based on the number of individual words that have a high similarity score
    and the number of total words in the descriptions.
    """
    book1 = set(str(book1desc).lower().replace("-","").replace("fiction","").replace(",","").replace("genre", "").replace(";", "").replace(":", "").replace(")", "").replace("(", "").split())
    book2 = set(str(book2desc).lower().replace("-","").replace("fiction","").replace(",","").replace("genre", "").replace(";", "").replace(":", "").replace(")", "").replace("(", "").split())

    total = 0
    count = 0
    for desc1 in book1:
        d1 = nlp.vocab[desc1]
        if d1.has_vector:
            for desc2 in book2: 
                    d2 = nlp.vocab[desc2]
                    if d2.has_vector:
                        val = d1.similarity(d2)
                        if val > 0.6:
                             count += 1
                        total += val
    return count



    




def find_most_similar_book(book_title):
    """
    This function finds the book in the data set with the highest similarity score with the inputted book.

    Parameters:
    book_title: the title of a book

    Returns:
    The title and the author of the book with the highest similarity score.
    """
    have_book = False
    book_descr = ""
    for index, bk_title in enumerate(books["bibliography.title"]):
        if book_title.lower() == bk_title.lower():
            have_book = True 
            book_descr = books["bibliography.subjects"][index]
            break
    if not have_book:
         print("Book not in the stored dataset, but you can provide 5 keywords and we'll find a similar book!")
         book_descr += str(input("First Keyword: ") + ", ")
         book_descr += str(input("Second Keyword: ") + ", ")
         book_descr += str(input("Third Keyword: ") + ", ")
         book_descr += str(input("Fourth Keyword: ") + ", ")
         book_descr += str(input("Fifth Keyword: "))
         
    most_sim_val = 0
    most_sim_index = 0
    total = 0
    for index, books_words in enumerate(books["bibliography.subjects"]):
         if not book_descr == books_words:
              curr_val = compare_two_books(book_descr, books_words)
              total += curr_val
              if curr_val > most_sim_val:
                   most_sim_val = curr_val
                   most_sim_index = index
     
    if most_sim_val == 0:
         print("The descriptions of the book had absolutely 0 similarities with the content of other books in the dataset. Make sure your spelling is correct.\n")
         return None
    
    average = total / 1005
    print("The most similar book from the classics dataset, based on NLP content similarities, is " + books["bibliography.title"][most_sim_index]+ " by "+ books["bibliography.author.name"][most_sim_index] + " with a similarity score of " + str(most_sim_val) + ". The average similarity score was " + str(average) + "\n")
    return books["bibliography.title"][most_sim_index]+ " by "+ books["bibliography.author.name"][most_sim_index]



def get_book_url(book_title):
     """
    This function finds the url of a book on GoodReads.

    Parameters:
    book_title: the title of a book

    Returns:
    The URL of the book.
    """
     search_url = "https://www.goodreads.com/search?q=" + book_title.replace(' ', '+')

     ### USER AGENT HERE!!!! ################################################################
     response = requests.get(search_url, headers={"User-Agent": "USER-AGENT HERE!!!!!"})
     ########################################################################################

     if response.status_code != 200:
          print("Failed to retrieve book search results.")
          return None
     
     page_content = BeautifulSoup(response.content, 'html.parser')
     first_result = page_content.find('a', class_='bookTitle')

     if first_result:
          book_url = "https://www.goodreads.com" + first_result['href']
          return book_url
     else:
          print("No results found, make sure your spelling is correct!")
          return None
     



def get_also_enjoyed_book(book_url):
     """
    This function finds a book that other readers enjoyed alongside the book in the given URL.

    Parameters:
    book_URL: A URL to the desired book on GoodReads

    Returns:
    The title and the author of the book that other readers enjoyed.
    """
     if type(book_url) != str:
          print("Invalid URL due to spelling, no book can be found.")
          return None
     options = webdriver.ChromeOptions()
     options.headless = True
     driver = webdriver.Chrome(options=options)
     driver.get(book_url)
     time.sleep(4)
     


     other_readers_section = driver.find_element(By.CLASS_NAME, 'BookPage__relatedTopContent')
     other_readers_section_scroll = driver.find_element(By.CLASS_NAME, 'BookPage__relatedTopContent')


     if not other_readers_section:
          return None
     else:
          driver.execute_script("arguments[0].scrollIntoView(true);", other_readers_section_scroll)
          time.sleep(4)
     
     first_rec = other_readers_section.find_element(By.CLASS_NAME, "BookCard")
     
     if not first_rec:
          return None
          
     first_rec_title = first_rec.find_element(By.CLASS_NAME,"BookCard__title")
     first_rec_author = first_rec.find_element(By.CLASS_NAME,"BookCard__authorName")
   
     rec_book_title = first_rec_title.text
     rec_book_author = first_rec_author.text
     print("After scraping the web, I've found that users that enjoyed your book ALSO enjoyed " + rec_book_title + " by " + rec_book_author + "\n")
     driver.quit()
     return rec_book_title + " by " + rec_book_author


def get_stat_diff(book_title):
    """
    This function finds the book in the data set with the lowest combined statistical difference in the 
    automated readability index and linsear write formula.

    Parameters:
    book_title: the title of a book

    Returns:
    The title and the author of the book with the lowest statisical difference score.
    """
    have_book = False
    book_read = 0
    book_lins = 0
    for index, bk_title in enumerate(books["bibliography.title"]):
        if book_title.lower() == bk_title.lower():
            have_book = True 
            book_read = books["metrics.difficulty.automated readability index"][index]
            book_lins = books["metrics.difficulty.linsear write formula"][index]
            break
        
    smallest_diff = 100
    closest_index = 0
    if not have_book:
          print("Book not in dataset, so a book with similar stats can't be calculated. A random book will be generated instead: ")
          new_index = random.randint(0,1005)
          print("The random book is " + books["bibliography.title"][new_index] +  " by " + books["bibliography.author.name"][new_index] + "\n_________________________________________")
          return books["bibliography.title"][new_index] +  " by " + books["bibliography.author.name"][new_index]

    else:
         for index in range(1006):
              curr_diff = (abs((books["metrics.difficulty.automated readability index"][index] - book_read)) + abs((books["metrics.difficulty.linsear write formula"][index] - book_lins)))
              if curr_diff < smallest_diff and curr_diff != 0:
                   closest_index = index
                   smallest_diff = curr_diff
         print("Based on the readability and difficulty of the book, you may also like " + books["bibliography.title"][closest_index] +  " by " + books["bibliography.author.name"][closest_index] + " with the smallest statistical difference of " + str(smallest_diff) + "\n_________________________________________")
         return books["bibliography.title"][closest_index] +  " by " + books["bibliography.author.name"][closest_index]
              
              



def book_librarian(book_name):
     """
    This function runs all 3 different book finding methods and outputs a detailed response
    detailing connections and similarities between the books.

    Parameters:
    book_name: the title of a book

    Returns:
    A paragraph suggesting and connecting books.
    """
     book1 = find_most_similar_book(book_name)
     book2 = get_also_enjoyed_book(get_book_url(book_name))
     book3 = get_stat_diff(book_name)

     if type(book1) != str or type(book2) != str:
          return "There were errors with your book search. Make sure your spelling is correct and you are entering a valid book."

     prompt = "You are knowledgable in books and literature. I really enjoyed the book " + book_name + " tell me, in 3 separate paragraphs for each book, why I would also like " + str(book1) + ", " + str(book2) + ", and " + str(book3)
     response = client.chat.completions.create(model="gpt-3.5-turbo-0125", messages=[{"role": "user", "content": prompt}] )
     return "Here are 3 more books that you may also enjoy:\n\n" + response.choices[0].message.content



def open_shop():
     """
    This function sets up the Code Librarian and user input to run this program.
    """
     print("\nWelcome to the Code Librarian, where you can find your next favorite book!\n")
     book = input("What is the title of a book that you enjoyed? ")
     print("\n Calculating your results...\n")
     print("\n\n" + book_librarian(book))
     print("\nYou can scroll up to see the methods used to find each of these books!\n")


open_shop()



