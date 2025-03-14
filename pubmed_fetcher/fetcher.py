import requests
import xmltodict
import csv

# Ask the user for their search query
search_query = input("Enter your search query for PubMed: ")

# Encode the search query for use in the URL
pubmed_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={search_query}&retmode=xml"

# Open CSV file for writing
with open('pubmed_articles.csv', 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['Title', 'Authors', 'Affiliations', 'Non-Academic Authors']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
    # Write the header row
    writer.writeheader()

    print("Before making the API call")
    # Make the API call to PubMed
    response = requests.get(pubmed_url)

    if response.status_code == 200:
        data = xmltodict.parse(response.text)
        ids = data.get('eSearchResult', {}).get('IdList', {}).get('Id', [])

        if ids:
            article_ids = ",".join(ids)  # Combine all IDs into a comma-separated string
            fetch_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={article_ids}&retmode=xml"
            
            # Make the request to fetch full article details
            response = requests.get(fetch_url)
            
            if response.status_code == 200:
                data = xmltodict.parse(response.text)
                articles = data.get('PubmedArticleSet', {}).get('PubmedArticle', [])
                
                # Define keywords related to pharmaceutical/biotech
                non_academic_keywords = ['pharmaceutical', 'biotech', 'company', 'industry', 'corporation']

                # Process articles and write to CSV
                for article in articles:
                    title = article.get('MedlineCitation', {}).get('Article', {}).get('ArticleTitle', 'No title')
                    authors = article.get('MedlineCitation', {}).get('Article', {}).get('AuthorList', {}).get('Author', [])
                    if isinstance(authors, str):  # If authors are a string, convert to list
                        authors = [authors]
                    
                    author_names = []
                    non_academic_authors = []
                    affiliations = []

                    for author in authors:
                        if isinstance(author, dict):
                            name = f"{author.get('LastName', '')} {author.get('ForeName', '')}"
                            affiliation = author.get('Affiliation', '')
                        else:
                            name = author  # If it's a string, take it directly
                            affiliation = ''
                        author_names.append(name)
                        affiliations.append(affiliation)

                        # Check for non-academic authors
                        if any(keyword.lower() in affiliation.lower() for keyword in non_academic_keywords):
                            non_academic_authors.append(name)

                    # Write row to CSV
                    writer.writerow({
                        'Title': title,
                        'Authors': ', '.join(author_names),
                        'Affiliations': ', '.join(affiliations),
                        'Non-Academic Authors': ', '.join(non_academic_authors)
                    })

    print("Data saved to pubmed_articles.csv")
