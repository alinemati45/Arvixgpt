from datetime import datetime, timedelta, timezone
import arxiv
import os
import requests
from PyPDF2 import PdfReader
from io import BytesIO
import time
import pandas as pd
import logging

# Set up logging

logging.basicConfig(filename='./logging_app/lapp.log', filemode='a',
                    format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - \
                    %(message)s - [%(threadName)s:%(thread)d] - [%(process)d] - [%(funcName)s]',
                    level=logging.INFO)

# Creating an object
logger = logging.getLogger()

# Setting the threshold of logger to DEBUG
logger.setLevel(logging.DEBUG)


# Function to sanitize a filename by removing invalid characters and replacing spaces with underscores.

# link : http://lukasschwab.me/arxiv.py/index.html


def sanitize_filename(filename):
    """
    Sanitize a filename by removing invalid characters and replacing spaces with underscores.

    :param filename: str, original filename
    :return: str, sanitized filename
    """
    # Characters that are not allowed in filenames
    invalid_chars = set(r'\/:*?"<>|')

    # Create a new string without invalid characters
    sanitized_filename = "".join(c for c in filename if c not in invalid_chars)

    # Replace spaces with underscores for readability and to avoid issues with command line operations
    sanitized_filename = sanitized_filename.replace(" ", "_")

    # Log sanitized filename
    logger.info(f"Sanitized filename: {sanitized_filename}")

    # Return sanitized filename
    return sanitized_filename


def create_directory(directory):
    """
    Create a directory if it does not exist.

    :param directory: str, directory path
    :return: None
    """
    # Use 'exist_ok=True' to make this operation idempotent i.e., running it multiple times doesn't have different effects
    os.makedirs(directory, exist_ok=True)


# Function to download a PDF from a given URL and extract text from it.


# Function to download a PDF from a given URL and extract text from it.

def download_article_pdf(result, url, delay=10):
    # print("Downloading article url...", url)
    """
    Download a PDF from a given URL, check the updated date and extract text from it.

    :param result: arxiv.Result, object containing information about an article
    :param url: str, url to download the PDF from
    :param delay: int, seconds to wait between requests
    :return: tuple(str, str), full_text and brief_text of the PDF along with its metadata
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-us,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'DNT': '1'
    }

    time.sleep(delay)  # wait for 'delay' seconds

    response = requests.get(url, headers=headers)
    # print("response: ", response)

    if response.status_code != 200:
        print(f"Error with status code: {response.status_code}")
        return None, None

    # Initialize a PDF reader object with the content of the response

    # Try and except block to handle the error
    try:
        pdf = PdfReader(BytesIO(response.content))
    except Exception as e:
        logger.error(f"Error while reading the PDF: {e}")
        return None, None

    # Initialize a PDF reader object with the content of the response

    # Build a string with metadata and content of the PDF document.
    # Multiline string literals are used for clarity and conciseness.
    full_text = f"""Title:\t{result.title}
Summary:
{result.summary}

PDF URL: \t{result.pdf_url}
Authors: \t{result.authors}

################################################################################################
Published: \t{result.published}
Updated: \t{result.updated}
Entry ID: \t{result.entry_id}
Short ID: \t{result.get_short_id()}

###############################PDF Content Will Start From Here:###############################
"""
    brief_text = f"""Title:\t{result.title}
Summary:
{result.summary}

PDF URL:\t{result.pdf_url}
Authors:\t{result.authors}
"""
    # Append the text of each page of the PDF to the full_text string
    for page in pdf.pages:
        full_text += page.extract_text()

    # Return the full text of the PDF along with its metadata
    return full_text, brief_text


def sanitize_article_text(text):
    """
    Sanitize the article text by removing the 'References' section.

    :param text: str, original article text
    :return: str, sanitized article text
    """
    # Check if text is None
    if text is None:
        return None  # or return an empty string "", or handle it in the way that makes most sense for your program

    # Find the start of the 'References' section, if it exists
    references_index = text.upper().find("REFERENCES")

    # If a 'References' section exists, remove everything from that point onwards
    if references_index != -1:
        text = text[:references_index]

    # Return the sanitized article text
    return text


def save_article(save_path, text):
    """
    Save the given text into a file at the specified path.

    :param save_path: str, file path to save the article
    :param text: str, text to be saved
    :return: None
    """
    # Open the file in write mode. If the file already exists, it will be overwritten.
    # The 'encoding' argument is used to specify the encoding of the file.
    # The 'errors' argument tells Python how to handle encoding errors.
    with open(save_path, "w", encoding="utf-8", errors="ignore") as f:
        # Write the text into the file
        f.write(text)


# Main function that searches for articles based on a keyword, downloads the PDFs,
# extracts and sanitizes text from the PDFs, and saves the text and PDFs to specified directories


def perform_search(keyword, maximum_number_articles_retrieve):
    # Perform a search on arXiv based on the provided keyword.
    """
    Perform a search on arXiv based on the provided keyword.
    Retrieve a maximum of n results sorted by the submission date in descending order.

    :param keyword: str, keyword for search
    :param n: int, number of maximum results
    :return: arxiv.Search, object containing the search results
    Https://arxiv.org/help/api/user-manual#detailed_examples
     link : http://lukasschwab.me/arxiv.py/index.html
    """
    print("Performing search...")
    result_article = arxiv.Search(
        query=keyword,  # search for electron in all fields
        max_results=maximum_number_articles_retrieve,  # maximum number of results
        sort_by=arxiv.SortCriterion.SubmittedDate,  # sort by submission date
        sort_order=arxiv.SortOrder.Descending,  # sort in descending order
    )

    with open("results.txt", "w") as file:
        for result in result_article.results():
            line = f"{result.title}\t{result.published}\n"
            print(f"{result.title}\t{result.published}")
            file.write(line)

    return result_article


counter = 1  # initialize counter outside of the function


def print_if_saved(result, filenames_dict):
    """
    Check if the files are already saved in the directories.
    If so, print a message indicating that the article is already saved.

    :param result: arxiv.Result, object containing information about an article
    :param filenames_dict: dict, dictionary containing filenames and saved filenames
    :return: bool, True if the files are already saved, False otherwise
    """
    global counter

    filename_text = filenames_dict['text']
    filename_pdf = filenames_dict['pdf']
    filename_brief = filenames_dict['brief']

    saved_filenames_txt = filenames_dict['saved_txt']
    saved_filenames_pdf = filenames_dict['saved_pdf']
    saved_filenames_brief = filenames_dict['saved_brief']

    found = False
    message = ""

    if filename_text in saved_filenames_txt:
        message = f"- Already Saved:{result.title} txt."
        found = True
    elif filename_pdf in saved_filenames_pdf:
        message = f"- Already Saved:{result.title} pdf."
        found = True
    elif filename_brief in saved_filenames_brief:
        message = f"- Already Saved:{result.title} brief."
        found = True

    if found:
        print(f"{counter}{message}")
        # logger.debug(f"{counter}{message}")
        counter += 1  # increment counter
        return True

    return False


def convert_article_to_dict(result, brief_text, full_text):
    """Convert article information to a dictionary.

    Args:
        result: A single article information retrieved from search.
        brief_text (str): Brief text information about the article.
        full_text (str): Full text information about the article.

    Returns:
        dict: A dictionary containing key-value pairs of article information.
    """
    return {
        "Article_ID": str(result.get_short_id()),
        "Title": result.title, "Summary": str(result.summary),
        "PDF_URL": result.pdf_url,
        "Authors": ", ".join(str(author) for author in result.authors),
        "Published": result.published,
        "Updated": result.updated,
        "Comment": str(result.comment),
        "Journal_Ref": str(result.journal_ref),
        "DOI": str(result.doi),
        "Primary_Category": str(result.primary_category),
        "Categories": str(result.categories),
        "Links": str(result.links),
        "arxiv_url": str(result.entry_id),
        "Brief_Text": str(brief_text),
        "Full_Text": str(full_text)
    }


def save_articles_to_csv(all_data):
    """Save articles information to a CSV file.

    Args:
        all_data: A list of dictionaries, where each dictionary contains the info of one article.
    """
    # Convert the list of data into a DataFrame
    df_new = pd.DataFrame(all_data)

    # Initialize df_old as an empty DataFrame
    df_old = pd.DataFrame()

    # If the "result.csv" file exists, read its contents into df_old DataFrame
    try:  # try to load old data
        df_old = pd.read_csv("./data/result.csv")
    except TypeError:  # if there is no old data, create a new file
        logger.error("old data is not loaded.")
    print("old data is loaded.")
    # logger.info("old data is loaded.")
    # logger.info("Saved articles information to ./data/result.csv")

    # Concatenate the new dataframe (df_new) with the old dataframe (df_old), with new data on top
    df_combined = pd.concat([df_new, df_old], ignore_index=True)

    # Save the combined dataframe to CSV file
    df_combined.to_csv("./data/result.csv", index=False, quoting=1)
    logger.info("Saved articles information to result.csv")


def sleep_time(i):  # to avoid getting blocked IP by arXiv
    if i == 0:  # first time
        print("We are about to start to retrieve articles from arXiv.")
        # logger.info("We are about to start to retrieve articles from arXiv.")
        return True
    else:  # after first time
        print("Sleeping for 10 seconds...to avoid getting blocked IP by arXiv.")
        # logger.info("Sleeping for 5 seconds...to avoid getting blocked IP by arXiv.")
        time.sleep(10)
        # print("Awake!")
        # logger.info("Awake!")


def create_dirs_and_get_files(directories):
    print("Creating directories if they do not exist...", directories)

    def check_and_create_directory(directory):
        if not os.path.exists(directory):
            os.makedirs(directory)
        return set(os.listdir(directory))

    return tuple(map(check_and_create_directory, directories))


def main(keyword, maximum_number_articles_retrieve, save_directory_txt, save_directory_pdf, save_directory_brief, start_date, end_date):
    # print("Performing search...", keyword) #############################################################################
    """################################################################################################################
    Main function to perform search, download articles, and save them.#################################################

    :param keyword: str, keyword for search
    :param n: int, number of maximum results
    :param save_directory_txt: str, directory path for text files
    :param save_directory_pdf: str, directory path for pdf files
    :param save_directory_brief: str, directory path for brief files
    :return: None
    """
    # Create directories for saving files if they do not exist

    directories = [save_directory_txt,
                   save_directory_pdf, save_directory_brief]
    saved_filenames_txt, saved_filenames_pdf, saved_filenames_brief = create_dirs_and_get_files(
        directories)

    # Perform a search on arXiv based on the provided keyword
    search = perform_search(keyword, maximum_number_articles_retrieve)
    print("Search is done.")

    # For each article in the search results
    for i, result in enumerate(search.results()):
        # Initialize DataFrame with the necessary columns
        # Sanitize the article's title to use it as a valid filename
        filename = sanitize_filename(result.title)

        # Get the updated date of the article and format it as "YYYY_MM_DD"
        datetime_obj = datetime.strptime(
            str(result.updated), "%Y-%m-%d %H:%M:%S%z").strftime("%Y_%m_%d")

        # Construct filenames for text, PDF, and brief formats
        filename_text = datetime_obj + "_" + filename + ".txt"
        filename_pdf = datetime_obj + "_" + filename + ".pdf"
        filename_brief = datetime_obj + "_" + filename + ".txt"

        # Construct a dictionary containing filenames and saved filenames
        filenames_dict = {
            'text': filename_text,
            'pdf': filename_pdf,
            'brief': filename_brief,
            'saved_txt': saved_filenames_txt,
            'saved_pdf': saved_filenames_pdf,
            'saved_brief': saved_filenames_brief
        }

        # If the files are already saved, print a message and move to the next article
        # If the files are not already saved
        if print_if_saved(result, filenames_dict) == True:
            continue
        # print("Checking if the article is published after the start date...")
        datetime_published = datetime.strptime(
            str(result.published), "%Y-%m-%d %H:%M:%S%z").strftime("%Y-%m-%d")
        datetime_start_date_last_week = datetime.strptime(
            str(start_date), "%Y-%m-%d %H:%M:%S.%f").strftime("%Y-%m-%d")

        datetime_start_date_end = datetime.strptime(
            str(end_date), "%Y-%m-%d %H:%M:%S.%f").strftime("%Y-%m-%d")

        # print("start_date", datetime_start_date_last_week)
        # print("end_date", end_date)
        # print("datetime_published", datetime_published)

        # end_date 2023-07-19 16:28:35.534394
        # start_date 2023-07-12
        # datetime_published 2023-07-09
        if datetime_published <= datetime_start_date_last_week and datetime_published >= datetime_start_date_end:
            print(
                f"The article {result.title} and {result.published} is published {datetime_published} before the {datetime_start_date_last_week} Skipping...")
            continue

        sleep_time(i)

        # Download the PDF content of the article and extract the text
        try:
            full_text, brief_text = download_article_pdf(
                result, result.pdf_url)
            if full_text is None and brief_text is None:
                print("The article is not downloaded. Skipping...")
                continue
        except TypeError:
            full_text, brief_text = None, None
            logger.info(
                'There is not more article to download. Please extend the date or check back later.')
            print(
                'There is not more article to download. Please extend the date or check back later.')
            return  # This will exit the current function immediately

        # Sanitize the article text by removing the 'References' section if present
        text = sanitize_article_text(full_text)

        # Define the path where the article text will be saved
        save_path = os.path.join(save_directory_txt, filename_text)

        # Save the article text to a file
        save_article(save_path, text)
        logger.info(
            f"{result.title}. Link: {result.pdf_url}. Date:{datetime_obj} ")

        # Download the PDF version of the paper
        paper = next(arxiv.Search(id_list=[result.get_short_id()]).results())
        paper.download_pdf(dirpath=str(save_directory_pdf),
                           filename=filename_pdf)
        logger.info(
            f"{result.title}. Link: {result.pdf_url}. Date:{datetime_obj} ")

        # Print a message to indicate that the article was saved successfully
        print(f"{result.title}. Link: {result.pdf_url}. Date:{datetime_obj} ")
        # Save brief_text to a text file
        save_path = os.path.join(save_directory_brief, filename_text)
        save_article(save_path, brief_text)
        logger.info(
            f"{result.title}. Link: {result.pdf_url}. Date:{datetime_obj} ")
        # Download the PDF content of the article and extract the text
        full_text, brief_text = download_article_pdf(result, result.pdf_url)
        # Convert the article to a dictionary and append to the list
        all_data.append(convert_article_to_dict(result, brief_text, full_text))
        logger.info(
            f"{result.title}. Link: {result.pdf_url}. Date:{datetime_obj} ")

    # Save the list of dictionaries to a CSV file
    if len(all_data) > 0:
        save_articles_to_csv(all_data)
    else:
        print("No new articles to save. You may want to extend the date.")
        logger.info("No new articles to save.")


all_data = []


def select_prefix():
    prefix_options = {
        'ti': 'ti',
        'au': 'au',
        'abs': 'abs',
        'co': 'co',
        'jr': 'jr',
        'cat': 'cat',
        'rn': 'rn',
        'id': 'id',
        'all': 'all'
    }
    print('''
Please select one or more prefix codes:
Explanation: prefix
Title: ti
Author: au
Abstract: abs
Comment: co
Journal Reference: jr
Subject Category: cat
Report Number: rn
Id (use id_list instead): id
All of the above: all
          ''')

    while True:
        user_selection = input(
            "Please enter one or more prefix codes (separated by a comma if more than one): ").split(',')
        # Remove any unnecessary whitespace
        user_selection = [option.strip() for option in user_selection]

        if 'all' in user_selection or not user_selection or not all(prefix in prefix_options.keys() for prefix in user_selection):
            user_selection = ""
            break
        else:
            break

    query_terms = input(
        "Please enter your query (if multiple words, separate them by comma): ").split(',')
    # Remove any unnecessary whitespace
    query_terms = [term.strip() for term in query_terms]

    if not query_terms:
        print("You must provide a query.")
        return

    if not user_selection or (len(user_selection) == 1 and user_selection[0] == ''):
        query = " AND ".join(query_terms)
    else:
        query = []
        for prefix in user_selection:
            prefix_terms = [prefix_options[prefix] + ":" + term if idx ==
                            0 else term for idx, term in enumerate(query_terms)]
            query.append(" AND ".join(prefix_terms))

        # If there are multiple query components, join them with " AND "
        if len(query) > 1:
            query = " AND ".join(query)
        else:
            query = query[0]

    return query


def get_time_frame():
    last_week = datetime.now() - timedelta(weeks=520)
    start_date = input(
        f"Please enter a start date in 'YYYY-MM-DD' format or press Enter to skip (Default is {last_week.strftime('%Y-%m-%d')}): ") or last_week
    if start_date != last_week:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        except ValueError:
            print(
                "Invalid date format. We will take one week before now as a start date! :)")
            start_date = last_week

    end_date = input(
        "Please enter an end date in 'YYYY-MM-DD' format or press Enter to skip (Default is today's date): ")
    if end_date:
        try:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            print("Invalid date format. We will take the current date as the end date.")
            end_date = datetime.now()
    else:
        end_date = datetime.now()
    # print("start data:", start_date, end_date)
    return start_date, end_date


if __name__ == "__main__":
    """
    Main function to get the keyword for the article search and define the directories where the articles will be saved.
    """

    # Define the keyword for the article search
    keyword = select_prefix()
    print(keyword)
    logging.info(f"Keyword for the article search: {keyword}")

    # Define the maximum number of articles to retrieve, API's limit is 300,000
try:
    maximum_number_articles_retrieve = int(input("Enter the maximum number of articles to retrieve (Default is 100 and Max = 250): ")) or 100
    maximum_number_articles_retrieve = min(maximum_number_articles_retrieve, 250)  # Limit to maximum of 250
except ValueError:
    maximum_number_articles_retrieve = 100
    logging.exception("Invalid input. The maximum number of articles to retrieve is set to 100.")


    # Get the time frame from the user
    start_date, end_date = get_time_frame()

    # Define the directories where the articles will be saved
    save_directory_pdf, save_directory_txt, save_directory_brief = (
        "savepdf", "savetxt", "savebrief")

    # Call the main function to perform the article search and save the articles
    main(keyword, maximum_number_articles_retrieve, save_directory_txt,
         save_directory_pdf, save_directory_brief, start_date, end_date)
    


#   File "ArXixLatestArticle.py", line 589, in <module>
#     main(keyword, maximum_number_articles_retrieve, save_directory_txt,
#   File "ArXixLatestArticle.py", line 393, in main
#     datetime_start_date_last_week = datetime.strptime(
#   File "C:\Users\nemat\miniconda3\envs\tensorflow\lib\_strptime.py", line 568, in _strptime_datetime
#     tt, fraction, gmtoff_fraction = _strptime(data_string, format)
#   File "C:\Users\nemat\miniconda3\envs\tensorflow\lib\_strptime.py", line 349, in _strptime
#     raise ValueError("time data %r does not match format %r" %
# ValueError: time data '2015-06-22 00:00:00' does not match format '%Y-%m-%d %H:%M:%S.%f'
