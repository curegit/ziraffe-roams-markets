import re
from urllib.parse import urlencode
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# サイトの識別子
name = "Mercari"

# 検索URLを生成する関数 (JavaScript)
queryjs = """
	((keyword) => {
		const params = new URLSearchParams({
			keyword: keyword,
			sort: "created_time",
			order: "desc",
			status: "on_sale"
		});
		return "https://jp.mercari.com/search?" + params.toString();
	})
"""

# 検索URLを生成する関数
def query(keyword):
	queries = {"keyword": keyword, "sort": "created_time", "order": "desc", "status": "on_sale"}
	return f"https://jp.mercari.com/search?{urlencode(queries)}"

# フェッチャーにさせる動作
def get(driver, keyword):
	driver.get(query(keyword))
	WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#search-result li figure + span, #search-result .merEmptyState")))
	container = driver.find_element(By.ID, "search-result")
	return container.get_attribute("innerHTML")

# フェッチしたデータの処理
def extract(documents):
	bs = BeautifulSoup(documents, "html.parser")
	for b in bs.select("li:has(a)"):
		path = b.select_one("a")["href"]
		match = re.search("/(m[0-9]+)", path)
		if match is None:
			# Shops
			match = re.search("/products/([A-Za-z0-9]+)", path)
			# 一部プラットフォーム
			if match is None:
				match = re.search("/shops/product/([A-Za-z0-9]+)", path)
			id = match.group(1)
			url = "https://mercari-shops.com/products/" + id
			title = b.select_one("figure + span").text
			thum = b.select_one("img")
			thumbnail = thum["src"]
			img = thumbnail.replace("/small/", "/large/")
			price_text = b.select_one(".merPrice > span + span").text
			price = int(price_text.replace(",", ""))
		else:
			id = match.group(1)
			url = "https://jp.mercari.com/item/" + id
			title = b.select_one("figure + span").text
			img = "https://static.mercdn.net/item/detail/orig/photos/" + id + "_1.jpg"
			thumbnail = "https://static.mercdn.net/c!/w=240/thumb/photos/" + id + "_1.jpg"
			price_text = b.select_one(".merPrice > span + span").text
			try:
				price = int(price_text.replace(",", ""))
			except ValueError:
				if len(price_text) <= 3:
					price = 0
				else:
					raise
		yield id, url, title, img, thumbnail, price
