import pandas as pd
import spacy
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import openai
from openai import OpenAI

nlp = spacy.load("en_core_web_md")
books = pd.read_csv('classics.csv')

openai.api_key = "sk-proj-eFxvJzr1GxiHXK3ZJTagT3BlbkFJOnZDF2hFc11ME7B9AgDF"
client = OpenAI(api_key="sk-proj-eFxvJzr1GxiHXK3ZJTagT3BlbkFJOnZDF2hFc11ME7B9AgDF")




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
                        if val > 0.6:
                             count += 1
                        total += val
    return count
    #return (count / ((len(book1) + len(book2))/2))


    




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

#print(find_most_similar_book("The Call of the Wild"))

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


def get_stat_diff(book_title):
     #use "metrics.difficulty.automated readability index" and "metrics.difficulty.linsear write formula"


     #first I need to find the index of the book. I alrady use this exact thing, so I can save redundant code somehow.
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
          print("Book not in data base, so a book with similar stats can't be calculated")
          #DO A RANDOM BOOK INSTEAD!!!!
    else:
         for index in range(1006):
              curr_diff = (abs((books["metrics.difficulty.automated readability index"][index] - book_read)) + abs((books["metrics.difficulty.linsear write formula"][index] - book_lins)))
              if curr_diff < smallest_diff and curr_diff != 0:
                   closest_index = index
                   smallest_diff = curr_diff

         print(books["bibliography.title"][closest_index] +  " by " + books["bibliography.author.name"][closest_index] + " with the smallest difference of " + str(smallest_diff))
              
              
#get_stat_diff("Crime and Punishment")
#client = OpenAI()

response = client.chat.completions.create(model="gpt-3.5-turbo-0125", messages=[{"role": "user", "content": "Tell me why Pride and Prejudice is a good book in 2 sentences."}] )

print(response.choices[0].message.content)

#get_also_enjoyed_book(get_book_url("The Call of the Wild"))
