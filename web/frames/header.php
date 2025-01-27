<?php
require_once "./modules/functions.php";

$nonce = nonce();
?>
<?php header("Content-Security-Policy: frame-ancestors 'none'; script-src 'self' 'nonce-{$nonce}'"); ?>
<?php header("Cache-Control: no-store"); ?>
<!DOCTYPE html>
<html lang="ja">
  <head>
    <meta charset="utf-8">
    <meta name="referrer" content="same-origin">
    <meta name="viewport" content="width=device-width">
    <meta name="application-name" content="Nominium">
<?php IF(defined("IS_HOME") && IS_HOME): ?>
    <title>Nominium</title>
<?php ELSE: ?>
    <title><?= h(PAGE_TITLE) ?> | Nominium</title>
<?php ENDIF; ?>
    <link href="./assets/style.css" rel="stylesheet">
    <link href="./assets/filter.css" rel="stylesheet">
    <link href="./assets/ziraffe.png" rel="icon">
    <link href="./assets/ziraffe-sq.png" rel="apple-touch-icon">
    <script nonce="<?= $nonce ?>">
      const queries = {};
<?php FOREACH(queries() as $name => $query): ?>
<?php IF(is_safe_for_inline_script($query) && is_safe_for_inline_script(json_encode($name))): ?>
      queries[<?= json_encode($name) ?>] = (<?= $query ?>);
<?php ENDIF; ?>
<?php ENDFOREACH; ?>
    </script>
  </head>
  <body>
    <header>
      <h1>Nominium – <?= h(PAGE_TITLE) ?></h1>
      <nav class="menu">
        <ul>
          <li><a href="./">ホーム</a></li>
          <li><a href="./keyword.php">キーワード</a></li>
          <li><a href="./register.php">登録</a></li>
          <li><a href="./delete.php">削除</a></li>
          <li><a href="./prioritize.php">重要度</a></li>
          <li><a href="./reorder.php">並べ替え</a></li>
          <li><a href="./filter.php">フィルタ</a></li>
          <li><a href="./inspect.php">監査</a></li>
<?php IF(isset($_SERVER["PHP_AUTH_USER"])): ?>
          <li><a href="./logout.php">ログアウト</a></li>
<?php ENDIF; ?>
        </ul>
      </nav>
    </header>
