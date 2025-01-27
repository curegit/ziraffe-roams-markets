<?php
// HTMLメタ文字のエスケープ
function h($str) {
  return htmlspecialchars($str, ENT_QUOTES, "UTF-8");
}

// インラインスクリプトに安全な文字列かどうか
function is_safe_for_inline_script($str) {
  $match = preg_match("/<\/script(\/| |>)/i", $str);
  if ($match === false) {
    return false;
  }
  return $match ? false : true;
}

// リクエスト中に変わらないノンスを生成
function nonce() {
  static $cache = null;
  if ($cache === null) {
    $cache = hash("sha256", random_bytes(1024));
  }
  return $cache;
}

// サイトごとのクエリの組み立て方を返す
function queries() {
  static $cache = null;
  if ($cache === null) {
    $json_path = realpath(__DIR__."/../../data/queries.json");
    $res = file_get_contents($json_path);
    if ($res === false) {
      $cache = json_decode("{}", true);
    } else {
      $cache = json_decode($res, true);
    }
  }
  return $cache;
}

// データベースへの接続を開いて返す
function open_db() {
  $db_path = realpath(__DIR__."/../../data/nominium.db");
  $pdo = new PDO("sqlite:".$db_path);
  $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
  $pdo->setAttribute(PDO::ATTR_DEFAULT_FETCH_MODE, PDO::FETCH_ASSOC);
  $pdo->setAttribute(PDO::ATTR_EMULATE_PREPARES, false);
  return $pdo;
}

// PDO例外が整合性制約違反なら真 (ANSI SQL-92)
function is_integrity_constraint_violation($error) {
  $code = (int)($error->getCode());
  return 23000 <= $code && $code < 24000;
}

// ログファイルの内容を返す
function get_recent_log($n, $error = false) {
  $name = $error ? date("Y-m")."-error" : date("Y-m-d");
  $log_path = realpath(__DIR__."/../../logs/{$name}.log");
  if (file_exists($log_path) && filesize($log_path) > 0) {
    return `tail -n $n $log_path`;
  } else {
    return false;
  }
}
