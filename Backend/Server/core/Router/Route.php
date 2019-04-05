<?php
declare(strict_types=1);

namespace KeythKatz\Barrens\Router;

class Route
{

	private static $routes = [];

	/**
	 * Bind the GET verb and a path to an entry point.
	 * @param  string $path          Path to bind to.
	 * @param  string $entryClass    Class to use when route matches.
	 * @param  string $entryFunction Function in class to use when route matches.
	 */
	public static function get(string $path, string $entryClass, string $entryFunction): void
	{
		self::addRoute($path, $entryClass, $entryFunction, "GET");
	}

	/**
	 * Bind the POST verb and a path to an entry point.
	 * @param  string $path          Path to bind to.
	 * @param  string $entryClass    Class to use when route matches.
	 * @param  string $entryFunction Function in class to use when route matches.
	 */
	public static function post(string $path, string $entryClass, string $entryFunction): void
	{
		self::addRoute($path, $entryClass, $entryFunction, "POST");
	}

	/**
	 * Bind the PUT verb and a path to an entry point.
	 * @param  string $path          Path to bind to.
	 * @param  string $entryClass    Class to use when route matches.
	 * @param  string $entryFunction Function in class to use when route matches.
	 */
	public static function put(string $path, string $entryClass, string $entryFunction): void
	{
		self::addRoute($path, $entryClass, $entryFunction, "PUT");
	}

	/**
	 * Bind the PATCH verb and a path to an entry point.
	 * @param  string $path          Path to bind to.
	 * @param  string $entryClass    Class to use when route matches.
	 * @param  string $entryFunction Function in class to use when route matches.
	 */
	public static function patch(string $path, string $entryClass, string $entryFunction): void
	{
		self::addRoute($path, $entryClass, $entryFunction, "PATCH");
	}

	/**
	 * Bind the DELETE verb and a path to an entry point.
	 * @param  string $path          Path to bind to.
	 * @param  string $entryClass    Class to use when route matches.
	 * @param  string $entryFunction Function in class to use when route matches.
	 */
	public static function delete(string $path, string $entryClass, string $entryFunction): void
	{
		self::addRoute($path, $entryClass, $entryFunction, "DELETE");
	}

	/**
	 * Bind the HEAD verb and a path to an entry point.
	 * @param  string $path          Path to bind to.
	 * @param  string $entryClass    Class to use when route matches.
	 * @param  string $entryFunction Function in class to use when route matches.
	 */
	public static function head(string $path, string $entryClass, string $entryFunction): void
	{
		self::addRoute($path, $entryClass, $entryFunction, "HEAD");
	}

	/**
	 * Bind the OPTIONS verb and a path to an entry point.
	 * @param  string $path          Path to bind to.
	 * @param  string $entryClass    Class to use when route matches.
	 * @param  string $entryFunction Function in class to use when route matches.
	 */
	public static function options(string $path, string $entryClass, string $entryFunction): void
	{
		self::addRoute($path, $entryClass, $entryFunction, "OPTIONS");
	}

	/**
	 * Bind a path to an entry point when accessing via the console.
	 * @param  string $path          Path to bind to.
	 * @param  string $entryClass    Class to use when route matches.
	 * @param  string $entryFunction Function in class to use when route matches.
	 */
	public static function cli(string $path, string $entryClass, string $entryFunction): void
	{
		self::addRoute($path, $entryClass, $entryFunction, "CLI");
	}

	/**
	 * General method to bind any verb to a route
	 * @param  string $verb          Verb to bind to.
	 * @param  string $path          Path to bind to.
	 * @param  string $entryClass    Class to use when route matches.
	 * @param  string $entryFunction Function in class to use when route matches.
	 */
	public static function bind(string $verb, string $path, string $entryClass, string $entryFunction): void
	{
		self::addRoute($path, $entryClass, $entryFunction, $verb);
	}

	/**
	 * General method to bind multiple verbs at once to a route.
	 * @param  array  $verbs         Strings of verbs to bind to.
	 * @param  string $path          Path to bind to.
	 * @param  string $entryClass    Class to use when route matches.
	 * @param  string $entryFunction Function in class to use when route matches.
	 */
	public static function bindMultiple(array $verbs, string $path, string $entryClass, string $entryFunction): void
	{
		foreach ($verbs as $verb) {
			self::addRoute($path, $entryClass, $entryFunction, $verb);
		}
	}

	private static function addRoute(string $path, string $entryClass, string $entryFunction, string $method): void
	{
		$r = new \stdClass();
		$r->method = $method;
		$r->path = explode("/", $path);
		$r->entryClass = $entryClass;
		$r->entryFunction = $entryFunction;
		array_push(self::$routes, $r);
	}

	/**
	 * Handle routing once all routes have been set. Calls the appropriate function.
	 */
	public static function handleRoute(): void
	{	
		// Fetch path from request / CLI input
		if (isset($_SERVER['argc'])) {
			$rawPath = $_SERVER['argv'][1]; // CLI
		} else {
			$rawPath = $_SERVER['REQUEST_URI'];
		}

		// URL has query string, ignore those
		if (strstr($rawPath, "?")) {
			$rawPath = substr($rawPath, 0, strpos($rawPath, "?"));
		}

		$pathArray = explode("/", $rawPath);
		$parameters = array();

		$routes = self::$routes;

		if(empty($routes)){
			header("HTTP/1.0 404 Not Found");
			echo "Error 404 - Route Not Found.";
		}

		// Find matching route(s) by deleting non-matching routes from $routes
		$pathArraySize = count($pathArray);
		for ($i = 0; $i < $pathArraySize; ++$i) {
			foreach ($routes as $key => $route) {
				$savedPath = $route->path;
				if ($pathArray[$i] !== $savedPath[$i] || $pathArraySize !== count($savedPath)) {
					if (!self::isPlaceholder($savedPath[$i])) {
						unset($routes[$key]);
					} else {
						$paramName = str_replace(array("{","}"), "", $savedPath[$i]);
						// If parameter input is blank, treat it as null
						if ($pathArray[$i] == "") {
							$parameters[$paramName] = null;
						} else {
							$parameters[$paramName] = $pathArray[$i];
						}
					}
				}
			}
		}

		// If all routes deleted, throw a 404.
		if(empty($routes)){
			header("HTTP/1.0 404 Not Found");
			echo "Error 404 - Route Not Found.";
		} else {
			// Call appropriate entry by checking the method
			$found = false;
			foreach ($routes as $route) {
				if (!isset($_SERVER['argc'])) {
					if ($route->method === $_SERVER['REQUEST_METHOD'] && $_SERVER['REQUEST_METHOD'] !== "CLI") {
						$found = true;
						self::callFunction($route->entryClass, $route->entryFunction, $parameters);
						break;
					}
				} else {
					if ($route->method === "CLI") {
						$found = true;
						self::callFunction($route->entryClass, $route->entryFunction, $parameters);
						break;
					}
				}
			}
			if(!$found){
				header("HTTP/1.0 405 Method Not Allowed");
				echo "Error 405 - Method Not Allowed.";
			}
		}
	}

	private static function isPlaceholder(string $string): bool
	{
		return (preg_match("/{.+}/", $string) === 1);
	}

	private static function callFunction(string $entryClass, string $entryFunction, array $parameters = []): void
	{
		if (substr($entryClass, 0, 1) != "\\") { // Call non-namespaced class without leading slash
			$class = '\\' . $entryClass;
		} else {
			$class = $entryClass;
		}
		$o = new $class();

		if (empty($parameters)) {
			$o->{$entryFunction}();
		} else {
			$o->{$entryFunction}($parameters);
		}
	}
}