from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
import time
options = Options()
options.add_argument('-headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-application-cache')
options.add_argument('--disable-gpu')
options.add_argument('--disable-dev-shm-usage')

def fetchPlaylist(lurl):

    driver = webdriver.Firefox(options=options)
    driver.get(lurl)
    
    try:

        contents = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "contents"))
        )

        videos = driver.find_element(By.XPATH, "//*[@id=\"stats\"]/yt-formatted-string[1]/span[1]")
        playlist_views = driver.find_element(By.XPATH, "//*[@id=\"stats\"]/yt-formatted-string[2]")
        last_updated = driver.find_element(By.XPATH, "//*[@id=\"stats\"]/yt-formatted-string[3]/span[2]")
        by = driver.find_element(By.XPATH, '//*[@id=\"text\"]/a')
        channelurl = driver.find_element(By.XPATH, '//*[@id=\"video-owner\"]/ytd-video-owner-renderer/a').get_attribute('href')
        desc = driver.find_element(By.XPATH, "/html/body/ytd-app/div[1]/ytd-page-manager/ytd-browse/ytd-playlist-sidebar-renderer/div/ytd-playlist-sidebar-primary-info-renderer/ytd-expander/div/div/yt-formatted-string")
        
        playlistinfo = open('Playlist_%d.txt' % time.time(), 'w+')
        playlistinfo.writelines(
        f'''
        Total Videos : {videos.text}
        Views : {playlist_views.text}
        Last Updated : {last_updated.text}
        By :  {by.text}
        Channel URL : {channelurl}
        Description : {desc.text}
        '''
        )

        contentpack = contents.find_elements(By.ID, 'content')

        for content in contentpack:

            content.location_once_scrolled_into_view # to scroll to the video list item to load the thumbnail
            thumbnail = content.find_element(By.ID, 'img').get_attribute('src')
            video = content.find_element(By.ID, 'video-title')
            url = video.get_attribute("href")
            channelname = content.find_element(By.ID, 'channel-name').text
            length = content.find_element(By.ID, 'text')
            index = url[url.rindex('=')+1:]

            op = fetchVideo(url)
            
            playlistinfo.writelines(
            f'''
            Index : {index}
            Title : {video.text}
            Channel : {channelname}
            Views : {op[0]}
            Likes : {op[1]}                 
            Age : {op[2]}
            Length : {length.text}
            Subscribers : {op[3]}
            Comments : {op[4]}
            Description : {op[6]}
            Channel URL : {op[5]}
            Video URL : {url}
            Thumbnail : {thumbnail}
            '''
            )

        playlistinfo.close()
    finally:
        driver.quit()


def fetchVideo(turl):
    driver = webdriver.Firefox(options=options)
    driver.get(turl)
    
    try:

        driver.set_context("chrome") 
        win = driver.find_element(By.TAG_NAME, "body")
        win.send_keys(Keys.LEFT_CONTROL + "-") # zoom out to see premiered and livestreamed dates
        driver.set_context("content")
        
        contents = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[@id=\"info-contents\"]/ytd-video-primary-info-renderer"))
        )
        curl = contents.find_element(By.XPATH, '//*[@id=\"text\"]/a').get_attribute('href')
        views = contents.find_element(By.XPATH, "/html/body/ytd-app/div[1]/ytd-page-manager/ytd-watch-flexy/div[5]/div[1]/div/div[6]/div[2]/ytd-video-primary-info-renderer/div/div/div[1]/div[1]/ytd-video-view-count-renderer/span[1]")
        likes = contents.find_element(By.ID, "text").text        
        subs = contents.find_element(By.XPATH, "//*[@id=\"owner-sub-count\"]")        
        
        driver.execute_script("window.scroll(0, 500)") # to switch to comments
        driver.implicitly_wait(10) # to load comments section
        desc = driver.find_element(By.XPATH, '//*[@id=\"description\"]/yt-formatted-string').get_attribute("textContent")
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id=\"sections\"]'))
            )
            comm = contents.find_element(By.XPATH, "//*[@id=\"count\"]/yt-formatted-string/span[1]").text
        except:
            comm = '''Disabled''' # comments are turned off
        age = contents.find_element(By.XPATH, "//*[@id=\"info-strings\"]/yt-formatted-string")
        op = [views.text, likes, age.text, subs.text, comm, curl, desc]
        
    finally:
        driver.quit()
    return op

if __name__ == '__main__':
    print('Enter Youtube Playlist : ')
    fetchPlaylist(input())