<?php
/**
 * Quote form handler for Hostinger shared hosting (uses PHP mail()).
 *
 * Settings: TO_EMAIL receives the enquiries. FROM_EMAIL must be an address on a domain
 * hosted in this Hostinger account (create it in hPanel > Emails), otherwise mail may be
 * rejected as spam.
 */
const TO_EMAIL = 'sales@ambicapatterns.in';
const FROM_EMAIL = 'website@ambicapatterns.com';
const MAX_PER_HOUR = 5;

header('X-Content-Type-Options: nosniff');
header('Cache-Control: no-store');
$wantsJson = strpos($_SERVER['HTTP_ACCEPT'] ?? '', 'application/json') !== false;

function respond(bool $ok, string $error = ''): void
{
    global $wantsJson;
    if ($wantsJson) {
        http_response_code($ok ? 200 : 400);
        header('Content-Type: application/json; charset=utf-8');
        echo json_encode(['ok' => $ok, 'error' => $error]);
    } else {
        header('Location: ' . ($ok ? '/contact/thank-you/' : '/contact/?error=1#quote'), true, 303);
    }
    exit;
}

if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') {
    http_response_code(405);
    header('Allow: POST');
    exit;
}

// Spam traps: hidden field must stay empty, and humans take more than 3 seconds.
if (!empty($_POST['website'])) {
    respond(true);
}
$started = (int)($_POST['started'] ?? 0);
if ($started > 0 && (microtime(true) * 1000 - $started) < 3000) {
    respond(true);
}

function field(string $key, int $max, bool $multiline = false): string
{
    $v = trim((string)($_POST[$key] ?? ''));
    $v = str_replace("\0", '', $v);
    if (!$multiline) {
        $v = preg_replace('/[\r\n\t]+/', ' ', $v); // no header injection
    }
    return function_exists('mb_substr') ? mb_substr($v, 0, $max) : substr($v, 0, $max);
}

$name = field('name', 100);
$company = field('company', 120);
$email = field('email', 160);
$phone = field('phone', 30);
$product = field('product', 80);
$quantity = field('quantity', 40);
$message = field('message', 4000, true);

if ($name === '' || $phone === '' || $message === '' || !filter_var($email, FILTER_VALIDATE_EMAIL)) {
    respond(false, 'please fill in all required fields');
}

// Light per-IP rate limit.
$ip = $_SERVER['HTTP_X_FORWARDED_FOR'] ?? $_SERVER['REMOTE_ADDR'] ?? 'unknown';
$ip = trim(explode(',', $ip)[0]);
$file = sys_get_temp_dir() . '/ap_quote_' . md5($ip);
$hits = json_decode((string)@file_get_contents($file), true);
$hits = array_values(array_filter(is_array($hits) ? $hits : [], fn($t) => $t > time() - 3600));
if (count($hits) >= MAX_PER_HOUR) {
    respond(false, 'too many requests, please try again later');
}
$hits[] = time();
@file_put_contents($file, json_encode($hits));

$subject = 'Quote request: ' . ($product !== '' ? $product : 'pallets') . ' - ' . $name;
$lines = [
    'New quote request from ambicapatterns.com',
    '',
    "Name:      $name",
    "Company:   $company",
    "Email:     $email",
    "Phone:     $phone",
    "Pallet:    " . ($product !== '' ? "$product (https://ambicapatterns.com/contact/?product=$product)" : 'not specified'),
    "Quantity:  $quantity",
    '',
    'Message:',
    $message,
    '',
    '--',
    'Sent ' . date('d M Y H:i') . " from IP $ip",
];
$headers = [
    'From: Ambica Patterns Website <' . FROM_EMAIL . '>',
    'Reply-To: ' . $email,
    'MIME-Version: 1.0',
    'Content-Type: text/plain; charset=UTF-8',
];
$sent = mail(TO_EMAIL, '=?UTF-8?B?' . base64_encode($subject) . '?=', implode("\n", $lines), implode("\r\n", $headers), '-f' . FROM_EMAIL);
respond($sent, $sent ? '' : 'the mail server did not accept the message');
