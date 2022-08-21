<?php
require_once "./modules/auth.php";
require_once "./modules/functions.php";

try {
  $pdo = open_db();
  $stmt = $pdo->query("SELECT * FROM item ORDER BY added DESC LIMIT 504");
  $items = $stmt->fetchAll();
  $error = false;
} catch (PDOException $e) {
  $error = $e->getMessage();
}

define("PAGE_TITLE", "ホーム");
?>
<?php include "./frames/header.php"; ?>
    <main>
<?php IF($error): ?>
      <section>
        <h2>エラー</h2>
        <p><?= h($error) ?></p>
      </section>
<?php ELSE: ?>
      <section>
        <div class="control">
          <div class="group">
            <label><input type="checkbox">自動更新</label>
            <select name="auto-update">
              <option value="15">15 秒</option>
              <option value="30">30 秒</option>
              <option value="60" selected>1 分</option>
              <option value="180">3 分</option>
              <option value="300">5 分</option>
            </select>
          </div>
        </div>
        <h2>新着アイテム</h2>
<?php IF($items): ?>
        <div class="items">
<?php FOREACH($items as $item): ?>
          <article class="item">
            <a href="<?= h($item["url"]) ?>">
              <div class="frame">
                <img class="image" src="<?= h($item["img"]) ?>">
                <div class="price">¥<?= h(number_format($item["price"])) ?></div>
              </div>
              <h3 class="title"><?= h($item["title"]) ?></h3>
            </a>
          </article>
<?php ENDFOREACH; ?>
        </div>
<?php ELSE: ?>
        <p>まだ何もインデックスされていません。</p>
<?php ENDIF; ?>
      </section>
<?php ENDIF; ?>
    </main>
<?php include "./frames/footer.php"; ?>
