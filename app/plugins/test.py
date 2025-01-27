import sys
import pprint
import traceback
import webbrowser
from modules.crawling import init_driver
from plugins.enabled import sites

def open_query(site, keyword):
	try:
		query = site.query(keyword)
	except Exception:
		raise RuntimeError(f"サイト「{site.name}」のクエリ関数は未定義です")
	else:
		success = webbrowser.open_new_tab(query)
		return success, query

def test_site(site, keyword, *, driver=None):
	if driver is None:
		driver = init_driver()
	documents = site.get(driver, keyword)
	items = site.extract(documents)
	return list(items)

def test_enabled_sites(keyword, *, driver=None):
	results = dict()
	if driver is None:
		driver = init_driver()
	for site in sites:
		try:
			if site.name in results:
				raise RuntimeError(f"サイト「{site.name}」が重複しています")
			result = test_site(site, keyword, driver=driver)
			pprint.pprint(result, stream=sys.stderr)
			results[site.name] = result
		except Exception as e:
			print(e, file=sys.stderr)
			print(traceback.format_exc(), file=sys.stderr)
	return results
