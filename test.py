import spacy
import csv

# Replace the path with your actual file path
file_path = './savetxt/2023_06_03_Befriending_ChatGPT_and_other_superchatbots_An_AI-integrated_take-home_assessment_preserving_integrity.txt'

# Load the text from the file
with open(file_path, 'r', encoding='utf-8') as file:
    text = file.read().replace('\n', '')

# Load the English language model
nlp = spacy.load("en_core_web_sm")
doc = nlp(text)

# Create a list to store the sentences
sentences_list = []

# Iterate through the sentences and append them to the list
for sent in doc.sents:
    sentences_list.append(sent.text)

# Save the sentences to a CSV file
output_file_path = './output_sentences.csv'
with open(output_file_path, 'w', encoding='utf-8', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Sentences'])
    writer.writerows([[sentence] for sentence in sentences_list])

print("Sentences have been saved to the CSV file:", output_file_path)
