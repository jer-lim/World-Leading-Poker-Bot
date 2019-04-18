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

Route::get("/5/weights", "\Controller\TrainerController5", "getWeights");
Route::get("/5/test", "\Controller\TrainerController5", "getTrainingSet");
Route::cli("/5/test", "\Controller\TrainerController5", "getTrainingSet");
Route::post("/5/submit", "\Controller\TrainerController5", "submitTestResult");
Route::get("/5/status", "\Controller\TrainerController5", "getStatus");

Route::get("/12/weights", "\Controller\TrainerController12Two", "getWeights");
Route::get("/12/test", "\Controller\TrainerController12Two", "getTrainingSet");
Route::cli("/12/test", "\Controller\TrainerController12Two", "getTrainingSet");
Route::post("/12/submit", "\Controller\TrainerController12Two", "submitTestResult");
Route::get("/12/status", "\Controller\TrainerController12Two", "getStatus");

Route::get("/13/weights", "\Controller\TrainerController13", "getWeights");
Route::get("/13/test", "\Controller\TrainerController13", "getTrainingSet");
Route::cli("/13/test", "\Controller\TrainerController13", "getTrainingSet");
Route::post("/13/submit", "\Controller\TrainerController13", "submitTestResult");
Route::get("/13/status", "\Controller\TrainerController13", "getStatus");
Route::get("/13/benchmark/{tester}", "\Controller\TrainerController13", "getBenchmark");
Route::post("/13/benchmark", "\Controller\TrainerController13", "submitBenchmark");

Route::get("/preflop/6/weights", "\Controller\TrainerControllerPreflop6", "getWeights");
Route::get("/preflop/6/test", "\Controller\TrainerControllerPreflop6", "getTrainingSet");
Route::cli("/preflop/6/test", "\Controller\TrainerControllerPreflop6", "getTrainingSet");
Route::post("/preflop/6/submit", "\Controller\TrainerControllerPreflop6", "submitTestResult");
Route::get("/preflop/6/status", "\Controller\TrainerControllerPreflop6", "getStatus");
Route::get("/preflop/6/benchmark/{tester}", "\Controller\TrainerControllerPreflop6", "getBenchmark");
Route::post("/preflop/6/benchmark", "\Controller\TrainerControllerPreflop6", "submitBenchmark");

Route::get("/15/weights", "\Controller\TrainerController15", "getWeights");
Route::get("/15/test", "\Controller\TrainerController15", "getTrainingSet");
Route::cli("/15/test", "\Controller\TrainerController15", "getTrainingSet");
Route::post("/15/submit", "\Controller\TrainerController15", "submitTestResult");
Route::get("/15/status", "\Controller\TrainerController15", "getStatus");
Route::get("/15/benchmark/{tester}", "\Controller\TrainerController15", "getBenchmark");
Route::post("/15/benchmark", "\Controller\TrainerController15", "submitBenchmark");

Route::cli("/t", "\Controller\TrainerControllerPreflop6", "t");
