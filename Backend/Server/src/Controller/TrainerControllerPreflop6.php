<?php
declare (strict_types = 1);

namespace Controller;

use Database\Database;
use Model\FactorPreflop6\Benchmark;
use Model\FactorPreflop6\Result;
use Model\FactorPreflop6\Weight;

class TrainerControllerPreflop6
{

    public $minGames;
    public $intervals;
    public $numWeights;

    public function __construct()
    {
        Database::init();

        $this->minGames = 400;
        $this->intervals = 105;
        $this->numWeights = 6;
    }

    public function getWeights()
    {
        $weights = Weight::getWeights();
        $w = [];
        for ($i = 0; $i < $this->numWeights; ++$i) {
            foreach ($weights as $weight) {
                if ($weight->weight == $i) {
                    array_push($w, (double) $weight->val);
                }
            }
        }
        print(json_encode($w));
    }

    public function t()
    {
        for ($i = 1; $i <= 10; ++$i) {
            $this->populateBenchmark($i);
        }
    }

    public function getTrainingSet()
    {
        $weights = Weight::getWeights();
        $currentIteration = $weights[$this->numWeights - 1]->iteration + 1;
        $currentWeight = $weights[0]->weight + 1;
        if ($currentWeight > $this->numWeights - 1) {
            $currentWeight = 0;
        }

        $this->checkResultsExist($currentIteration, $currentWeight);

        $tests = Result::getIncompleteTests($currentIteration, $currentWeight);
        if (count($tests) == 0) {
            $bestResult = Result::getBestResult($currentIteration, $currentWeight);
            if ($bestResult->result > 300) {
                Weight::newWeight($currentIteration, $currentWeight, $bestResult->test_value);
            } else {
                $w = Weight::getWeight($currentIteration - 1, $currentWeight);
                Weight::newWeight($currentIteration, $currentWeight, $w->val);
            }

            $weights = Weight::getWeights();
            $currentIteration = $weights[$this->numWeights - 1]->iteration + 1;
            $currentWeight = $weights[0]->weight + 1;
            if ($currentWeight > $this->numWeights - 1) {
                $currentWeight = 0;
            }

            $this->checkResultsExist($currentIteration, $currentWeight);
            $tests = Result::getIncompleteTests($currentIteration, $currentWeight);
        }

        $test = Result::getIncompleteTest($currentIteration, $currentWeight);

        $obj = new \stdClass();
        $obj->iteration = $currentIteration;
        $obj->weight = $currentWeight;
        $obj->testValue = (double) $test->test_value;
        $obj->minGames = $test->min_games;

        $test->setAssigned();
        print(json_encode($obj));
    }

    public function submitTestResult()
    {
        Database::init();
        $test = json_decode(file_get_contents('php://input'));
        if (isset($test->minGames)) {
            $r = Result::getTest($test->iteration, $test->weight, $test->testValue);
            if ($r->result === null) {
                $tester = null;
                if (isset($test->tester)) {
                    $tester = $test->tester;
                }

                $r->setResult($test->result, $tester);
            }
        }

        $this->getTrainingSet();
    }

    public function getStatus()
    {
        $weights = Weight::getWeights();
        $currentIteration = $weights[$this->numWeights - 1]->iteration + 1;
        $currentWeight = $weights[0]->weight + 1;
        if ($currentWeight > $this->numWeights - 1) {
            $currentWeight = 0;
        }

        $obj = new \stdClass();
        $obj->iteration = $currentIteration;
        $obj->weight = $currentWeight;
        print(json_encode($obj));
    }

    public function getBenchmark($params)
    {
        $tester = $params["tester"];

        $benchmark = Benchmark::getUnassignedBenchmark();
        if ($benchmark == null) {
            print(json_encode(null));
        } else {
            $benchmark->setTester($tester);

            $toDouble = function ($str) {
                return (double) $str;
            };

            $weights1 = Weight::getIterationWeights($benchmark->iteration1);
            $weights1 = array_map($toDouble, $weights1);
            $weights2 = Weight::getIterationWeights($benchmark->iteration2);
            $weights2 = array_map($toDouble, $weights2);

            $obj = new \stdClass();
            $obj->iteration1 = $benchmark->iteration1;
            $obj->iteration2 = $benchmark->iteration2;
            $obj->weights1 = $weights1;
            $obj->weights2 = $weights2;
            $obj->min_games = $benchmark->min_games;
            print(json_encode($obj));
        }
    }

    public function submitBenchmark()
    {
        $test = json_decode(file_get_contents('php://input'));
        $benchmark = Benchmark::getBenchmark($test->iteration1, $test->iteration2);
        $benchmark->setResult($test->result);
    }

    private function populateBenchmark($iteration)
    {
        if (!Benchmark::haveBenchmarks($iteration)) {
            Benchmark::createBenchmarks($iteration);
        }
    }

    private function checkResultsExist($currentIteration, $currentWeight)
    {
        $results = Result::getTestResults($currentIteration, $currentWeight);
        if (count($results) == 0) {
            $weight = Weight::getWeight($currentIteration - 1, $currentWeight);
            Result::createNew($currentIteration, $currentWeight, $this->intervals, $this->minGames);
        }
    }
}
