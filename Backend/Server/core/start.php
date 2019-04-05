<?php
declare(strict_types=1);

define("APP_PATH", __DIR__ . "/../src");

// Use Composer autoloader
require __DIR__ . "/../vendor/autoload.php";

// Load routes
require_once __DIR__ . "/../routes.php";

// User declared initialisation
require_once __DIR__ . "/../init_user.php";

// Load appropriate route
KeythKatz\Barrens\Router\Route::handleRoute();
