# per page

from selenium import webdriver as wd
# Page Controll Module
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time
from pprint import pprint

driver = wd.Chrome(executable_path='./chromedriver')
main_url = 'https://www.youtube.com/watch?v=9E1AD3GBMLE'

driver.get(main_url)


def init():
  ## 댓글 로드되는 시점 = scroll Y : 500
  driver.execute_script("window.scrollTo(1,500)")
  ## 동영상 정지

def scrollDown():
  # scrollDown
  ## 현재 페이지 Y 위치 window.pageYOffset
  ## 현재 스크롤 총 높이 document.documentElement.scrollHeight
  # scrollDown 중지
  ## 로딩서클이 나오지 않을 때 scrollDown 중지
  ## document.querySelector('#sections > #continuations > .style-scope.ytd-item-section-renderer')
  while(1):
    bottomOfScroll = driver.execute_script("return document.querySelector('#sections > #continuations > .style-scope.ytd-item-section-renderer')")
    if(bottomOfScroll):
      ActionChains(driver) \
        .key_down(Keys.PAGE_DOWN) \
        .perform()
    ## bottomOfPage인지 판별
    else:
      return 0
    time.sleep(1)

def reply():
  # 리플누르기(대댓글)
  ## 댓글 더보기 버튼 .more-button.style-scope.ytd-comment-replies-renderer
  replyList = driver.execute_script("return document.querySelectorAll('.more-button.style-scope.ytd-comment-replies-renderer').length")
  if(replyList):
    for num in range(0, replyList):
      driver.execute_script("return document.querySelectorAll('.more-button.style-scope.ytd-comment-replies-renderer')[%s].click()" %num)
  else:
    return 0

def crawl():
  # comment DOM
  ## a element of Comment : (#comments #contents .style-scope.ytd-item-section-renderer)
  ## 댓글 - 바디 : (a element of Comment) => #comment => #body
  ##    |_ 리플(리플의 리플은 부모 자식관계 아님) : (a element of Comment) => #replies => #contents => #loaded-replies
  commentList = driver.find_elements_by_css_selector('#comments #contents .style-scope.ytd-item-section-renderer')
  # 댓글-바디
  for li in commentList:
    ## 작성자가 적은 댓글 태그는 따로 달림
    name = li.find_element_by_css_selector('#comment #body #header #header-author #author-comment-badge').text
    if(name == ''):
      name = li.find_element_by_css_selector('#comment #body #header #header-author #author-text').text    
  # 댓글-리플
    # if()

init()
time.sleep(5)
scrollDown()
reply()
crawl()







# def crawling():
#     ## 크롤링
#     ## 끝나면 페이지내리기

# init()

