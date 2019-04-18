<?php
declare (strict_types = 1);

namespace Model\Factor13;

/**
 * @property int id
 * @property int iteration
 * @property int weight
 * @property int val
 */
class Weight extends \Illuminate\Database\Eloquent\Model
{
    public $table = "weights13";
    public $timestamps = false;
    private static $numWeights = 13;
    //public $primaryKey = ;
    //protected $keyType = string;
    //public $incrementing = false;

    //public $id, $high, $low, $open, $close, $date;

    public static function getWeights()
    {
        return self::where("id", ">", 0)
            ->orderBy("iteration", "DESC")
            ->orderBy("weight", "DESC")
            ->limit(self::$numWeights)
            ->get();
    }

    public static function getIterationWeights($iteration)
    {
        return self::where("iteration", $iteration)
            ->orderBy("weight", "ASC")
            ->pluck("val")
            ->toArray();
    }

    public static function getWeight($iteration, $weight)
    {
        return self::where("iteration", $iteration)
            ->where("weight", $weight)
            ->first();
    }

    public static function newWeight($iteration, $weight, $val)
    {
        $w = new self();
        $w->iteration = $iteration;
        $w->weight = $weight;
        $w->val = $val;
        $w->save();
    }
}
