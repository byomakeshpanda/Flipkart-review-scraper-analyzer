import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tqdm import tqdm
# Create a socket and start listening

#Getting the product URL
# productURL = input("Enter the product URL\n")

def get_data(productURL):
    main_product = requests.get(productURL)
    if (main_product.status_code)==200:
        soup = BeautifulSoup(main_product.text, 'html.parser')

    main_div = soup.find('div', class_='JOpGWq')
    links = main_div.find_all('a', recursive=False)
    link_urls = [link['href'] for link in links]
    partial_link=link_urls[-1]

    review_link = 'https://www.flipkart.com'+partial_link

    review_page = requests.get(review_link)
    if review_page.status_code==200:
        soup = BeautifulSoup(review_page.content, 'html.parser')
        div = soup.find('div', class_='_2MImiq _1Qnn1K')
        span = div.find('span')
        if span:
            span_text = span.text

    number_of_pages = int(span_text.split()[-1])

    nav = div.find('nav', class_='yFHi8N')
    link = nav.find('a')
    if link:
        href = link.get('href')

    review_page_1_gen_link = 'https://www.flipkart.com'+href

    file_name = soup.title.text[:15].lower().replace(' ','_')
    def get_filename():
        return file_name
    reviews_df = pd.DataFrame()
    driver = webdriver.Chrome() 
    for i in tqdm(range(1,min(50,number_of_pages)+1)):
        url = review_page_1_gen_link[:-1]+str(i)

        driver.get(url)
        elements = driver.find_elements(By.CSS_SELECTOR, 'div._27M-vq._2hwual')  
        for element in elements:
            try:
                WebDriverWait(driver, 15,poll_frequency=1).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'div._27M-vq._2hwual')))
                element.click()
            except Exception as e:
                print(f"Failed to click on element: {e}")
        #Clicking on all the read more
        span = driver.find_elements(By.CSS_SELECTOR, 'span._1BWGvX')
        for i in span:
            actions = ActionChains(driver)
            actions.move_to_element(i)
            actions.perform()
            i.click()
        #Get rating
        div = driver.find_elements(By.CSS_SELECTOR, 'div._3LWZlK._1BLPMq')
        ratings = []
        for i in div:
            ratings.append(i.text)
            #The data is unavailable only dummy page is present.
        if(len(ratings)==0):
            break
        #For title
        paragraph = driver.find_elements(By.CSS_SELECTOR, 'p._2-N8zT')
        titles = []
        for i in paragraph:
            titles.append(i.text)
        #For main review
        div = driver.find_elements(By.CSS_SELECTOR, 'div.t-ZTKy')
        main_reviews=[]
        for i in div:
            review = i.text
            main_reviews.append(review.replace('\n', ' ').strip())
        reviews_dict = {'ratings':ratings,'titles':titles,'reviews':main_reviews}
        temp_df = pd.DataFrame(reviews_dict)
        reviews_df = reviews_df._append(temp_df,ignore_index=True)
    driver.quit()
    return reviews_df,file_name

