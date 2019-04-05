<?php
declare (strict_types = 1);

namespace Controller;

use Database\Database;
use Model\Result;
use Model\Weight;

class TrainerController
{

    public function getWeights()
    {
        Database::init();

        $weights = Weight::getWeights();
        $w = [];
        foreach ($weights as $weight) {
            array_push($w, (float) $weight->val);
        }
        print(json_encode($w));
    }

    public function getTrainingSet()
    {
        Database::init();

        $intervals = 100;
        $numWeights = 12;

        $weights = Weight::getWeights();
        $currentIteration = $weights[$numWeights - 1]->iteration + 1;
        $currentWeight = $weights[0]->weight + 1;
        if ($currentWeight > $numWeights - 1) {
            $currentWeight = 0;
        }

        $this->checkResultsExist($currentIteration, $currentWeight, $intervals);

        $tests = Result::getIncompleteTests($currentIteration, $currentWeight);
        if (count($tests) == 0) {
            $bestResult = Result::getBestResult($currentIteration, $currentWeight);
            Weight::newWeight($currentIteration, $currentWeight, $bestResult->test_value);

            $weights = Weight::getWeights();
            $currentIteration = $weights[$numWeights - 1]->iteration + 1;
            $currentWeight = $weights[0]->weight + 1;
            if ($currentWeight > $numWeights - 1) {
                $currentWeight = 0;
            }

            $this->checkResultsExist($currentIteration, $currentWeight, $intervals);
            $tests = Result::getIncompleteTests($currentIteration, $currentWeight);
        }

        $testNum = rand(0, count($tests) - 1);
        $test = $tests[$testNum];

        $obj = new \stdClass();
        $obj->iteration = $currentIteration;
        $obj->weight = $currentWeight;
        $obj->testValue = (float) $test->test_value;
        print(json_encode($obj));
    }

    public function submitTestResult()
    {
        Database::init();
        $test = json_decode(file_get_contents('php://input'));

        $r = Result::getTest($test->iteration, $test->weight, $test->testValue);
        if ($r->result === null) {
            $r->setResult($test->result);
        }

        $this->getTrainingSet();
    }

    private function checkResultsExist($currentIteration, $currentWeight, $intervals)
    {

        $results = Result::getTestResults($currentIteration, $currentWeight);
        if (count($results) == 0) {
            Result::createNew($currentIteration, $currentWeight, $intervals);
        }
    }
}
