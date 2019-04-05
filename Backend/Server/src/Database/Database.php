<?php
declare (strict_types = 1);

namespace Database;

use Illuminate\Database\Capsule\Manager as Capsule;

class Database
{
    public static function init()
    {
        $capsule = new Capsule;

        $capsule->addConnection([
            'driver' => 'mysql',
            'host' => 'localhost',
            'database' => 'cs3243',
            'username' => '',
            'password' => '',
            'charset' => 'latin1',
            'collation' => 'latin1_swedish_ci',
            'prefix' => '',
        ]);

// Set the event dispatcher used by Eloquent models... (optional)
        //$capsule->setEventDispatcher(new Dispatcher(new Container));

// Make this Capsule instance available globally via static methods... (optional)
        $capsule->setAsGlobal();

// Setup the Eloquent ORM... (optional; unless you've used setEventDispatcher())
        $capsule->bootEloquent();
    }
}
