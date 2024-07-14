import pandas as pd
import spacy


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
         print("Book not found, but you can provide 3 keywords and we'll find a similar book!")
         book_descr += str(input("First Keyword: ") + ", ")
         book_descr += str(input("Second Keyword: ") + ", ")
         book_descr += str(input("Third Keyword: ") + ", ")
         print(book_descr)
        # here i can add it to where you add in your own descriptions.
    #Need to make sure the book doesn't just find itself in case of repeats
         
    most_sim_val = 0
    most_sim_index = 0
    for index, books_words in enumerate(books["bibliography.subjects"]):
         if not book_descr == books_words:
              curr_val = compare_two_books(book_descr, books_words)
              if curr_val > most_sim_val:
                   most_sim_val = curr_val
                   most_sim_index = index

    return "The most similar book is " + books["bibliography.title"][most_sim_index]+ " by "+ books["bibliography.author.name"][most_sim_index] + " with a similarity score of " + str(most_sim_val)

print(find_most_similar_book("Crime and Punishmen"))
