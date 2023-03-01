# BlogPostArchiver
Mini web scraper for archiving blogspot/wordpress blog posts

## Requirements
Python3  
pip

## Set up the Virtual Environment
$ pip install venv  
$ python3 -m venv venv  
$ source venv/bin/activate  
$ pip install -r requirements.txt  

## Run the tool
Edit and save sample_article_links.txt with the URLs you want to archive. Each line should be a separate URL.  
$ python3 scrape.py  
