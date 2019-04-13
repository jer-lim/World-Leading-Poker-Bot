<?php
declare (strict_types = 1);

namespace Controller;

use Database\Database;
use Model\Factor5\Result;
use Model\Factor5\Weight;

class TrainerController5
{

    public $minGames;
    public $intervals;
    public $numWeights;

    public function __construct()
    {
        Database::init();

        $this->minGames = 250;
        $this->intervals = 100;
        $this->numWeights = 4;
    }

    public function getWeights()
    {
        $weights = Weight::getWeights();
        $w = [];
        for ($i = 0; $i < $this->numWeights; ++$i) {
            foreach ($weights as $weight) {
                if ($weight->weight == $i) {
                    array_push($w, (float) $weight->val);
                }
            }
        }
        print(json_encode($w));
    }

    public function t()
    {
        $bestResult = Result::getBestResult(6, 0);
        print($bestResult->test_value);
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
            Weight::newWeight($currentIteration, $currentWeight, $bestResult->test_value);

            $weights = Weight::getWeights();
            $currentIteration = $weights[$this->numWeights - 1]->iteration + 1;
            $currentWeight = $weights[0]->weight + 1;
            if ($currentWeight > $this->numWeights - 1) {
                $currentWeight = 0;
            }

            $this->checkResultsExist($currentIteration, $currentWeight);
            $tests = Result::getIncompleteTests($currentIteration, $currentWeight);
        }

        //$testNum = rand(0, count($tests) - 1);
        //$test = $tests[$testNum];

        $test = Result::getIncompleteTest($currentIteration, $currentWeight);

        $obj = new \stdClass();
        $obj->iteration = $currentIteration;
        $obj->weight = $currentWeight;
        $obj->testValue = (float) $test->test_value;
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

    private function checkResultsExist($currentIteration, $currentWeight)
    {
        $results = Result::getTestResults($currentIteration, $currentWeight);
        if (count($results) == 0) {
            Result::createNew($currentIteration, $currentWeight, $this->intervals, $this->minGames);
        }
    }
}
