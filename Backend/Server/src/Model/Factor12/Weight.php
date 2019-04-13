<?php
declare (strict_types = 1);

namespace Model\Factor12;

/**
 * @property int id
 * @property int iteration
 * @property int weight
 * @property int val
 */
class Weight extends \Illuminate\Database\Eloquent\Model
{
    public $table = "weights";
    public $timestamps = false;
    //public $primaryKey = ;
    //protected $keyType = string;
    //public $incrementing = false;

    //public $id, $high, $low, $open, $close, $date;

    public static function getWeights()
    {
        return self::where("id", ">", 0)
            ->orderBy("iteration", "DESC")
            ->orderBy("weight", "DESC")
            ->limit(12)
            ->get();
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
