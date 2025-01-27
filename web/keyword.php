<?php
require_once "./modules/auth.php";
require_once "./modules/csrf.php";
require_once "./modules/functions.php";

try {
  $pdo = open_db();
  $stmt = $pdo->query("SELECT * FROM keyword ORDER BY priority DESC");
  $keywords = $stmt->fetchAll();
  $error = false;
} catch (PDOException $e) {
  http_response_code(500);
  $error = $e->getMessage();
}

define("PAGE_TITLE", "キーワード表示");
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
        <h2>登録中のキーワード</h2>
<?php IF($keywords): ?>
        <p>クロールされる順番で表示しています。</p>
        <script defer src="./assets/open.js"></script>
        <table>
          <thead>
            <tr>
              <th>キーワード</th>
              <th class="numeric">重要度</th>
              <th>クエリ</th>
            </tr>
          </thead>
          <tbody>
<?php FOREACH($keywords as $keyword_record): ?>
            <tr class="queryrow">
              <td class="querykeyword"><?= h($keyword_record["keyword"]) ?></td>
              <td class="queryimportance"><?= h($keyword_record["importance"])?></td>
              <td class="querylinks"></td>
            </tr>
<?php ENDFOREACH; ?>
          </tbody>
        </table>
<?php ELSE: ?>
        <p>キーワードが登録されていません。</p>
<?php ENDIF; ?>
      </section>
<?php ENDIF; ?>
    </main>
<?php include "./frames/footer.php"; ?>
