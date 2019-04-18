<?php
declare (strict_types = 1);

namespace Model\Factor13;

/**
 * @property int id
 * @property int iteration
 * @property int weight
 * @property int val
 */
class Benchmark extends \Illuminate\Database\Eloquent\Model
{
    public $table = "benchmarks13";
    public $timestamps = false;
    //public $primaryKey = ;
    //protected $keyType = string;
    //public $incrementing = false;

    //public $id, $high, $low, $open, $close, $date;

    public static function haveBenchmarks($iteration)
    {
        return self::where("iteration1", $iteration)
            ->count() > 0;
    }

    public static function createBenchmarks($iteration)
    {
        if ($iteration > 0) {
            for ($i = 0; $i < $iteration; ++$i) {
                $b = new self();
                $b->iteration1 = $iteration;
                $b->iteration2 = $i;
                $b->save();
            }
        }
    }

    public static function getUnassignedBenchmark()
    {
        return self::where("assigned_tester", null)
            ->where("result", null)
            ->first();
    }

    public static function getBenchmark($iteration1, $iteration2)
    {
        return self::where("iteration1", $iteration1)
            ->where("iteration2", $iteration2)
            ->first();
    }

    public function setTester($tester)
    {
        $this->assigned_tester = $tester;
        $this->save();
    }

    public function setResult($result)
    {
        $this->result = $result;
        $this->save();
    }
}
