from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '0.0.0.2'
DESCRIPTION = 'Search for updated article on arXiv.org'
LONG_DESCRIPTION = '''
This library would help you to search for updated article on arXiv.org.
Output is a list of articles with their title, authors, abstract, and link to the article.

Extraction data from arXiv.org is done by using arxiv library.:
    - Article_ID
    - Title
    - PDF_URL
    - Authors
    - Published
    - Updated
    - Comment
    - Journal_Ref
    - DOI
    - Primary_Category
    - Categories
    - Links
    - arxiv_url
    - Brief_Text
    - Full_Text

Output file format:
    - CSV file as result.csv
    - a folder with main pdf file
    - a floder with brief abstract:
        - Title
        - Summary
        - PDF_URL
        - Authors

'''

# Setting up
setup(
    name="ArXixLatestArticle",
    version=VERSION,
    author="Synthetic Dataset AI Team",
    author_email="<nematiusa@gmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),


    install_requires=['pandas', 'PyPDF2', 'requests'],
    keywords=['python', 'pandas', 'numpy', 'request', 'PyPDF2'],
    python_requires=">=3.7",

    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "License :: Free To Use But Restricted",

    ],
)
