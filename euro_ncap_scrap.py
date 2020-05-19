import psycopg2 as pg
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.selector import Selector
from selenium import webdriver
import time


url_cars = []
make = []
model = []
points = []
year = []


driver = webdriver.Chrome('./chromedriver.exe')
driver.get('https://www.euroncap.com/en/ratings-rewards/latest-safety-ratings/#?selectedMake=0&selectedMakeName=Select%20a%20make&selectedModel=0&selectedStar=&includeFullSafetyPackage=false&includeStandardSafetyPackage=true&selectedModelName=All&selectedProtocols=40302,34803,30636,26061,24370,1472,5910,5931,-1,14999&selectedClasses=1202,1199,1201,1196,1205,1203,1198,1179,40250,1197,1204,1180,34736&allClasses=true&allProtocols=true&allDriverAssistanceTechnologies=false&selectedDriverAssistanceTechnologies=&thirdRowFitment=false')
time.sleep(10)
url_cars = [ i.get_attribute('href') for i in driver.find_elements_by_xpath('//*[@class="rating-table-row ng-scope"]/div[1]/a')]
driver.close()


print(url_cars)
print("Collect URLs FINISHED")



class euro_ncap_spider(scrapy.Spider):

	name = "euro_ncap_spider"

	def start_requests(self):
				
		for url in url_cars:
			yield scrapy.Request(url=url, callback = self.parse)

	def parse(self, response):
		
		make.append(response.url.split('results/',1)[1].split('/')[0])
		model.append(response.url.split('results/',1)[1].split('/')[1])
		points.append(response.xpath('//*[@id="tab2-3"]/div[3]/div[1]/div[2]/div/div[2]/div/p[1]/span[2]/text()').extract()[0].split(' Pts')[0])
		year.append(response.xpath('//*[@class="specification-table table1"]/p[3]/span[2]/text()').extract()[0])
		yield None


process = CrawlerProcess()
process.crawl(euro_ncap_spider)
process.start()

con = None
sql_table = """ CREATE TABLE headimpact
				(
    				id SERIAL,
   					make varchar(20),
   					model varchar(20),
    				year smallint,
    				points real
				)"""

sql = """INSERT INTO headimpact(make,model,year,points)
		VALUES (%s,%s,%s,%s)"""

try:
	con = pg.connect(host="localhost", database="headimpact", user="postgres", password="postgres")
	cur = con.cursor()
	cur.execute(sql_table)
	cur.executemany(sql, zip(make,model,year,points))
	cur.close()
	con.commit()

finally:
	if con is not None: con.close() 

print("FINISH")