import urllib.request
import re
from bs4 import BeautifulSoup

stock_CodeUrl = 'http://quote.eastmoney.com/stocklist.html'
def get_html_text():
    try:
        html=urllib.request.urlopen(stock_CodeUrl).read()
        html=html.decode('utf-8')
        return html
    except Exception  as ex :
        print('error',ex)
        return ''

if __name__=='__main__':
    text=get_html_text()
    print(text)
