#!/usr/bin/env python3

import sys
import time
import random
import signal
from html import escape as h
from queue import Queue
from modules import config as conf
from modules.web import save_queries
from modules.logging import Logger
from modules.database import connect
from modules.crawling import init_driver, Fetcher, Extractor
from modules.notification import NotificationController
from plugins.enabled import sites, hooks

# 開始時刻を記録する
start = time.time()

# ロギングを開始する
logger = Logger()
logger.log_line("プロセスを開始しました。")
logger.commit()

# 目標動作時間を受け取る
try:
	uptime = int(sys.argv[1])
except Exception as e:
	logger.log_exception(e, "動作時間を整数秒で与えてください。")
	logger.commit()
	raise

# タスクキューを作成する
fetch_queue = Queue(conf.parallel * 2)
documents_queue = Queue()

# 通知コントローラを用意する
nc = NotificationController(conf.max_notify_hourly, dry=(not conf.mail_enabled))
hook_ncs = [NotificationController(conf.max_notify_hourly) for h in hooks]

# サイトごとのクエリの組み立て方を保存する
save_queries(sites)

# 子プロセスが割り込みで終了しないようにする
signal.signal(signal.SIGINT, signal.SIG_IGN)

# フェッチャーを起動する
drivers = []
try:
	for i in range(conf.parallel):
		drivers.append(init_driver())
except Exception as e:
	try:
		logger.log_exception(e, "フェッチャーの起動に失敗しました。")
		logger.commit()
	except:
		pass
	for driver in drivers:
		try:
			driver.quit()
		except:
			pass
	raise
fetchers = [Fetcher(i, d, logger, fetch_queue, documents_queue, conf.wait, conf.max_rate, conf.patience, conf.backoff) for i, d in enumerate(drivers, 1)]
for fetcher in fetchers:
	fetcher.start()

# フェッチタスクのイテレータを用意する
fetch_table = []
def fetch_iterator():
	while True:
		count = 0
		for kid, keyword, probability in fetch_table:
			if random.random() < probability:
				for site in sites:
					count += 1
					yield site, kid, keyword
		if count == 0:
			yield None
fetch_iter = fetch_iterator()

# フェッチ結果から新規のアイテムについて通知する
def update(extractor, cursor, logger, least_one=False, timeout=15):
	# 新規のアイテムを取り出す
	mails = []
	hook_arg = []
	for site, keyword, notify, notify_code, item in extractor.pop_all_items(least_one=least_one, timeout=timeout):
		id, url, title, img, thumbnail, price = item
		cursor.execute("SELECT COUNT(*) AS count FROM item WHERE site = ? AND id = ?", (site.name, id))
		existence = bool(int(cursor.fetchone()["count"]))
		if not existence:
			cursor.execute("INSERT INTO item(site, id, url, title, img, thumbnail, price, notify) VALUES(?, ?, ?, ?, ?, ?, ?, ?)", (site.name, id, url, title, img, thumbnail, price, notify_code))
			if notify:
				subject = title
				plain = f"{title}\n¥{price:,} – {site.name}\nリンク: {url}\nイメージ: {img}\n"
				html = f"<html><head><title>{h(title)}</title></head><body><p><a href=\"{h(url)}\">{h(title)}</a></p><p>¥{price:,} – {h(site.name)}</p><a href=\"{h(img)}\"><img src=\"{h(thumbnail)}\"></a></body></html>\n"
				mails.append((subject, plain, html))
				hook_arg.append((site.name, id, keyword, title, url, img, thumbnail, price))
				logger.log_line(f"{site.name} で「{keyword}」についての新規発見：{title}")
	# 履歴を更新する
	for site, kid in extractor.pop_fresh():
		cursor.execute("SELECT COUNT(*) AS count FROM history WHERE site = ? AND keyword = ?", (site, kid))
		existence = bool(int(cursor.fetchone()["count"]))
		if not existence:
			cursor.execute("INSERT INTO history(site, keyword) VALUES(?, ?)", (site, kid))
	# メール通知を送信する
	if mails:
		try:
			count = nc.send(mails)
			logger.log_line(f"メール通知を {count} 件送信しました。")
		except Exception as e:
			logger.log_exception(e, f"メール通知の送信に失敗しました。")
	# 通知フックを実行する
	if hook_arg:
		for hook, hnc in zip(hooks, hook_ncs):
			try:
				count = hnc.run_hook(hook, hook_arg)
				logger.log_line(f"{count} 件について通知フック {hook.__name__} を実行しました。")
			except Exception as e:
				logger.log_exception(e, f"フックの実行中にエラーが発生しました。")

# 割り込みシグナルハンドラ
def interrupt(signum, frame):
	global interrupted
	first_interruption = not interrupted
	interrupted = True
	if first_interruption:
		logger.log_line("割り込みによる中断を受け取りました。")
		logger.log_line("中断を試みます。")
	else:
		logger.log_line("中断しています。")

class SigTermExit(BaseException):
	pass

# シャットダウンシグナルハンドラ
def terminate(signum, frame):
	global terminated
	first_termination = not terminated
	terminated = True
	if first_termination:
		raise SigTermExit()

# データベースに繋いで作業する
with connect() as connection:
	cursor = connection.cursor()
	# ここでのエラーはログに残るがプログラムも終了する
	try:
		# 存在しないサイトのフェッチ履歴を削除する
		holders = ", ".join(["?"] * len(sites))
		site_names = tuple([site.name for site in sites])
		cursor.execute(f"DELETE FROM history WHERE site NOT IN ({holders})", site_names)
		# 抽出器を用意して必要なら履歴を引き継ぐ
		extractor = Extractor(logger, documents_queue, conf.max_price, conf.cut, conf.enough)
		if conf.while_stopped:
			cursor.execute("SELECT * FROM history")
			for hr in cursor.fetchall():
				extractor.history.add((hr["site"], int(hr["keyword"])))
		# 割り込みによる中断を設定
		interrupted = False
		terminated = False
		signal.signal(signal.SIGINT, interrupt)
		signal.signal(signal.SIGTERM, terminate)
		logger.log_line("ループを開始します。")
		logger.commit()
		# 動作時間内なら続ける
		while not interrupted and time.time() - start < uptime:
			# キーワードを取り出してイテレータを更新する
			cursor.execute("SELECT * FROM keyword ORDER BY priority DESC")
			fetch_table = [(int(kr["id"]), kr["keyword"], float(kr["importance"])) for kr in cursor.fetchall()]
			# フェッチタスクをキューに入るだけ入れる
			for i in range(fetch_queue.maxsize - fetch_queue.qsize()):
				maybe_fetch = next(fetch_iter)
				if maybe_fetch is None:
					break
				fetch_queue.put(maybe_fetch)
			# フィルタを更新する
			cursor.execute("SELECT * FROM filter")
			extractor.set_filter_patterns([fr["pattern"] for fr in cursor.fetchall()])
			# 新規のアイテムについて通知する
			update(extractor, cursor, logger, least_one=True)
			# ログに書き込む
			logger.commit()
		# フェッチャーを終了させる
		for fetcher in fetchers:
			fetcher.complete = True
		for fetcher in fetchers:
			if fetch_queue.full:
				break
			fetch_queue.put(None, block=False)
		for fetcher in fetchers:
			fetcher.join(timeout=60)
		# バッファに残っているアイテムについて処理する
		update(extractor, cursor, logger)
	# 重いエラーが起きた場合
	except Exception as e:
		try:
			logger.log_exception(e, "重大なエラーが発生しました。")
			logger.commit()
		except:
			pass
		raise
	# SIGTERM
	except SigTermExit:
		logger.log_line("シャットダウンシグナルを受け取りました。迅速に終了します。")
		logger.commit()
	# リソース開放などの後始末を行う
	finally:
		# WebDriverを終了させる
		for driver in drivers:
			try:
				driver.quit()
			except Exception as e:
				logger.log_exception(e, "ブラウザの終了に失敗しました。")
			else:
				logger.log_line("ブラウザを正常に終了させました。")

# 終了を報告する
logger.log_line("プロセスを終了しました。")
logger.commit()

# 割り込み終了なら終了コードを特殊化
if terminated:
	sys.exit(143)
if interrupted:
	sys.exit(130)
