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

    public static function getIncompleteTest(int $iteration, int $weight)
    {
        return self::where("iteration", $iteration)
            ->where("weight", $weight)
            ->where("result", null)
            ->orderBy("last_assigned", "ASC")
            ->orderBy("test_value", "ASC")
            ->first();
    }

    public static function getBestResult(int $iteration, int $weight)
    {
        return self::where("iteration", $iteration)
            ->where("weight", $weight)
            ->orderBy("result", "DESC")
            ->limit(1)
            ->first();
    }

    public static function createNew(int $iteration, int $weight, int $intervals, int $minGames)
    {
        $interval = 1 / $intervals;
        for ($i = 0; $i < $intervals + 1; ++$i) {
            $value = $i * $interval;
            $r = new self();
            $r->iteration = $iteration;
            $r->weight = $weight;
            $r->test_value = $value;
            $r->min_games = $minGames;
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

    public function setResult(int $result, $tester)
    {
        $this->result = $result;
        $this->tester = $tester;
        $this->save();
    }

    public function setAssigned()
    {
        $this->last_assigned = date("Y-m-d H:i:s");
        $this->save();
    }
}
