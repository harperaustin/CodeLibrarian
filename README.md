A book recommendation program that finds 3 new books (using 3 different techniques) based on 1 input book. Here are the techniques:
  1. Natural Language Processing: I use NLP with spaCy to compare the subject/topic words of a book and find the book in the dataset with most similar subject words.
  2. Web-Scraping: I web-scrape with Selenium to find books online that readers of the inputted book also enjoy.
  3. Statistical Analysis: I use the statistics in the dataset (like various readability scores) to find the book with the smallest statistical difference with the inputted book.

After the 3 books are fetched, I use the openai API to produce a detailed and personalized output explaining the connections and similarities between the inputted book and the 3 book recommendations.
