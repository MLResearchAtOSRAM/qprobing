#!/bin/bash

# base name for xml generation
xml_base=build/tests/results

# run all the tests that do not use the JVM
pytest \
--cov=qprobing \
--cov-report=xml:build/tests/coverage.xml \
--junitxml=$xml_base.xml \
tests/qprobing \
-m "not uses_jvm"

# specify all the other tests
special_tests=(
    "analysis_runner"
    "analysis_evaluator_random"
    "analysis_evaluator_perfect"
    "experiment_runner_single"
    "experiment_runner_multiple"
)

# run them and append the coverage
for filename in ${special_tests[@]}
do
    xml_path=$xml_base-$filename.xml
    pytest \
    --cov-append \
    --cov=qprobing \
    --cov-report=xml:build/tests/coverage.xml \
    --junitxml=$xml_path \
    tests/qprobing/test_$filename.py \
    -m "uses_jvm"
done

# verify that all of the tests have passed
junitparser verify --glob build/tests/results**.xml

# merge the xml files for reporting
junitparser merge --glob build/tests/results**.xml build/tests/combined.xml
