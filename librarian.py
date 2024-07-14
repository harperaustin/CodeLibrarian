import pandas as pd
import spacy
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import time


nlp = spacy.load("en_core_web_md")
books = pd.read_csv('classics.csv')




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
    #print("\n Book 1: " + str(book1) + "\n")
    book2 = set(str(book2desc).lower().replace("-","").replace("fiction","").replace(",","").replace("genre", "").replace(";", "").replace(":", "").replace(")", "").replace("(", "").split())
    #print("\n Book 2: " + str(book2) + "\n")
    total = 0
    count = 0
    for desc1 in book1:
        d1 = nlp.vocab[desc1]
        if d1.has_vector:
            for desc2 in book2: 
                    d2 = nlp.vocab[desc2]
                    if d2.has_vector:
                        val = d1.similarity(d2)
                        if val > 0.5:
                             count += 1
                        total += val

    return (count / ((len(book1) + len(book2))/2))


    




def find_most_similar_book(book_title):
    have_book = False
    book_descr = ""
    for index, bk_title in enumerate(books["bibliography.title"]):
        if book_title.lower() == bk_title.lower():
            have_book = True 
            book_descr = books["bibliography.subjects"][index]
            break
    if not have_book:
         print("Book not in stored dataset, but you can provide 3 keywords and we'll find a similar book!")
         book_descr += str(input("First Keyword: ") + ", ")
         book_descr += str(input("Second Keyword: ") + ", ")
         book_descr += str(input("Third Keyword: ") + ", ")
         print(book_descr)
        # here i can add it to where you add in your own descriptions.
    #Need to make sure the book doesn't just find itself in case of repeats
         
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
    
    average = total / 1005

    return "The most similar book from the classics dataset is " + books["bibliography.title"][most_sim_index]+ " by "+ books["bibliography.author.name"][most_sim_index] + " with a similarity score of " + str(most_sim_val) + ". The average similarity score was " + str(average)

#print(find_most_similar_book("Normal People"))

def get_book_url(book_title):
     search_url = "https://www.goodreads.com/search?q=" + book_title.replace(' ', '+')
     response = requests.get(search_url, headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"})

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

     options = webdriver.ChromeOptions()
     options.headless = True
     driver = webdriver.Chrome(options=options)
     driver.get(book_url)
     time.sleep(5)
     page_source = driver.page_source
     driver.quit()

     
     
     page_content = BeautifulSoup(page_source, 'html.parser')
     other_readers_section = page_content.find('div', class_='BookPage__relatedTopContent')

     if not other_readers_section:
          print("The other readers enjoyed section was NOT found.")
          return None
     else:
          print("Other readers enjoyed section found.")
     
     first_rec = other_readers_section.find('div', class_="BookCard")
     if not first_rec:
          print("No Recs found")
          return None
     else:
          print("Found some recs")

     first_rec_title = first_rec.find('div', class_="BookCard__title")
     first_rec_author = first_rec.find('div', class_="BookCard__authorName")
   

     
     
     rec_book_title = first_rec_title.get_text(strip=True)
     rec_book_author = first_rec_author.get_text(strip=True)
     print(rec_book_title + " by " + rec_book_author)
          
     

get_also_enjoyed_book(get_book_url("Normal People"))
