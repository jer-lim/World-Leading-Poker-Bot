<?php
declare (strict_types = 1);

namespace Model;

/**
 * @property int id
 * @property int iteration
 * @property int weight
 * @property float test_value
 * @property int result
 */
class Result extends \Illuminate\Database\Eloquent\Model
{
    public $table = "results";
    public $timestamps = false;
    //public $primaryKey = ;
    //protected $keyType = string;
    //public $incrementing = false;

    //public $id, $high, $low, $open, $close, $date;

    public static function getTestResults(int $iteration, int $weight)
    {
        return self::where("iteration", $iteration)
            ->where("weight", $weight)
            ->get();
    }

    public static function getIncompleteTests(int $iteration, int $weight)
    {
        return self::where("iteration", $iteration)
            ->where("weight", $weight)
            ->where("result", null)
            ->get();
    }

    public static function getBestResult(int $iteration, int $weight)
    {
        return self::where("iteration", $iteration)
            ->where("weight", $weight)
            ->orderBy("result", "DESC")
            ->limit(1)
            ->first();
    }

    public static function createNew(int $iteration, int $weight, int $intervals)
    {
        $interval = 1 / $intervals;
        for ($i = 0; $i < $intervals; ++$i) {
            $value = $i * $interval;
            $r = new self();
            $r->iteration = $iteration;
            $r->weight = $weight;
            $r->test_value = $value;
            $r->save();
        }
    }

    public static function getTest(int $iteration, int $weight, float $testValue)
    {
        return self::where("iteration", $iteration)
            ->where("weight", $weight)
            ->where("test_value", $testValue)
            ->first();
    }

    public function setResult(int $result)
    {
        $this->result = $result;
        $this->save();
    }
}
