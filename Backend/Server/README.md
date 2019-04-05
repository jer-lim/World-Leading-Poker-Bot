# barrens

This is supposed to be a super simple framework for PHP projects. 
It barely does anything and requires the minimum amount of setup that you
have probably already done before.

## Why Use It

You want a framework that does nothing and that you don't have to do a lot of setup for.

## Features
- Quick install
- Simple routing engine

## Requirements

- Apache2 (or implement your own URL rewriting)
- PHP 7.1 and above

## Setup

You'll need to have `AllowOverride All` for the install directory in your Apache config
and the `rewrite` Apache extension enabled.

If you haven't already, [install Composer](https://getcomposer.org/doc/00-intro.md).

Then run `php composer.phar install-project keythkatz/barrens ` to install it into
a folder `barrens` or `php composer.phar install-project keythkatz/barrens [install directory]` to install
it into a folder of your choice.

Point your domain to the `public/` folder.

At this point you should see a "Hey, it works!" message on your homepage.

### .htaccess, Images, CSS and JS

By default, URLs ending in an image format, `.css` and `.js` are not handled by the router, and are served by files in the `public/` directory.
You can modify the `public/.htaccess` file to add/remove extensions.

## Usage

### Your code

Your code (should) live in the `src/` folder.

### Routing

The router initialises an instance of the specified class, then calls the function provided.

To add a route, modify the `routes.php` file. An example has been provided.

In general, to add a route:
```
	Route::[verb]([full path], [full class name to initialise], [function to call]);
	// [verb] = get, post, put, patch, delete, head, options
```

Use `Route::cli(...)` for command line-only access.

#### Parameters

In the path, you can use `{paramName}` to indicate a parameter. These will be passed as an array into the provided function.
Example: `Route::get("/from/{from}/to/{to}", "\Example", "main")` will pass `["from" => ..., "to" => ...]` into `\Example->main($params)`.
