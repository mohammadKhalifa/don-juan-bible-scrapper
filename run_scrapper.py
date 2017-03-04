import requests
from bs4 import BeautifulSoup
import pdfkit

main_url = 'http://www.sosuave.com/bible/bible.htm'

def add_chapter(chapter_name , html_str) :
    chapter_name = chapter_name.encode('ascii' , errors = 'ignore')
    html_str += '''
    <h1>
    {0}
    <br> <br>
    </h1>
    '''.format(chapter_name)
    return html_str


def add_topic(topic_name, topic_text, html_str):

    topic_name = topic_name.encode('ascii', errors='ignore')
    topic_text = topic_text.encode('ascii' , errors='ignore')
    print 'Processing {0}...'.format(topic_name)
    html_str += '''
    <h3>
    {0}
    </h3>
    <p>
    {1}
    <p>
    <hr>
    <br>
    '''.format(topic_name, topic_text)
    return html_str


def process_topic_link(url, html_str, ignore_comments=True):
    text = requests.get(url).text
    soup = BeautifulSoup(text, 'html.parser')
    hr_tags = soup.find_all('hr')

    if ignore_comments:
        hr_tags = hr_tags[:1]

    for hr_tag in hr_tags:
        td_tag = hr_tag.find_parent('td')
        all_fonts = td_tag.find_all('font')
        all_fonts[1].extract() # remove date posted
        all_fonts[-1].extract()  # remove IP address
        title = soup.find('title').text
        title = title[:title.find('-')]# remove 'Don juan Discussion Forum'

        html_str = add_topic(title , td_tag.text, html_str)
    return html_str


if __name__ == '__main__':

    text = requests.get(main_url).text
    soup = BeautifulSoup(text, 'html.parser')
	
    all_topics = ''
    all_topics += '''
    <html> <title>
    The Don Juan Bible
    </title>
    <style type="text/css">
    body {
        font-size: 26px
    }
    </style>
    <body>
    '''
    cnt =0
    for tr in soup.find_all('tr'):
        for fnt in tr.find_all('font'):
            if 'Chapter' in fnt.text:
                tr_sib = tr.find_next_sibling()
                p = tr_sib.find('p')
                if p:
                    # Process chapter
                    fnt.find_all('a')[-1].extract() # remove (get back to the top)
                    all_topics = add_chapter(fnt.text, all_topics)
                    for link in p.find_all('a'):
                        cnt += 1
                        all_topics = process_topic_link(link['href'], html_str=all_topics)

    all_topics += '''
    </body>
    </html>
    '''
    pdfkit.from_string(all_topics, 'DJ Bible.pdf')
    f = open('DJ Bible.html', 'w+')
    f.write(all_topics)

