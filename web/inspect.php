<?php
require_once "./modules/auth.php";
require_once "./modules/csrf.php";
require_once "./modules/functions.php";

$n = 2000;
$err_n = 1000;
$log = get_recent_log($n);
$err_log = get_recent_log($n, true);
if ($err_log === null || $log === null) {
  http_response_code(500);
}

define("PAGE_TITLE", "監査");
?>
<?php include "./frames/header.php"; ?>
    <main>
      <script defer src="./assets/query.js"></script>
      <section class="query-test">
        <h2>クエリテスト</h2>
        <div>
          <label>
            キーワード：<input type="text" id="query-input" placeholder="キーワードを入力">
          </label><div class="buttons" id="query-buttons"></div>
        </div>
      </section>
<?php IF($err_log === null): ?>
      <section>
        <h2>エラー</h2>
        <p>エラーログの読み取りに失敗しました。</p>
      </section>
<?php ELSE: ?>
      <section>
        <h2>今月のエラーログ</h2>
<?php IF($err_log === false): ?>
        <p>今月のエラーログはありません。</p>
<?php ELSE: ?>
        <p>最大で末尾から <?= h($err_n) ?> 行を表示します。</p>
        <pre class="log"><?= h($err_log) ?></pre>
<?php ENDIF; ?>
      </section>
<?php ENDIF; ?>
<?php IF($log === null): ?>
      <section>
        <h2>エラー</h2>
        <p>ログの読み取りに失敗しました。</p>
      </section>
<?php ELSE: ?>
      <section>
        <h2>今日のログ</h2>
<?php IF($log === false): ?>
        <p>今日のログはありません。</p>
<?php ELSE: ?>
        <p>最大で末尾から <?= h($n) ?> 行を表示します。</p>
        <pre class="log"><?= h($log) ?></pre>
<?php ENDIF; ?>
      </section>
<?php ENDIF; ?>
    </main>
<?php include "./frames/footer.php"; ?>
