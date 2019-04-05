<?php
declare(strict_types=1);

if (!isset($argv[1]) && isset($argc)) {
	echo "Path should be passed as first parameter";
	exit();
}

define("BARRENS_CORE_PATH", __DIR__);
require BARRENS_CORE_PATH . "/start.php";

exit();