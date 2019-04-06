<?php
declare (strict_types = 1);

use KeythKatz\Barrens\Router\Route;

/**
 * Front facing:
 * Route::get([full path], [full class name to initialise], [function to call]);
 * RESTful verbs that can be used in place of get: get, post, put, patch, delete, head, options
 *
 * Command line:
 * Route::cli([full path], [full class name to initialise], [function to call]);
 *
 * Custom verbs:
 * Route::bind([verb], [full path], [full class name to initialise], [function to call]);
 * Route::bindMultiple([array of verbs], [full path], [full class name to initialise], [function to call]);
 *
 * Parameters:
 * In the path, you can use {paramName} to indicate a parameter. These will be passed as an array into the provided function.
 * Example: Route::get("/from/{from}/to/{to}", "\Example", "main") will pass ["from" => ..., "to" => ...] into \Example->main($params)
 */

Route::get("/", "\Controller\IndexController", "main");
Route::get("/weights", "\Controller\TrainerController", "getWeights");
Route::get("/test", "\Controller\TrainerController", "getTrainingSet");
Route::cli("/test", "\Controller\TrainerController", "getTrainingSet");
Route::post("/submit", "\Controller\TrainerController", "submitTestResult");
Route::get("/status", "\Controller\TrainerController", "getStatus");
