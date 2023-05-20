
server_pid=0

function start_server {
    echo "Starting server..."
    python3 ./src/server.py &
    server_pid=$!
    echo "Server started with pid $server_pid"
}

function stop_server {
    echo "Stopping server..."
    kill -9 $server_pid
    echo "Server stopped"
}

function is_success {
    if [ $? -eq 0 ]; then
        echo "Test passed"
    else
        echo "Test failed"
        stop_server
        exit 1
    fi
}

function run_test_subscribe {
    start_server
    echo "Running test subscriber..."
    pytest src/test.py::test_subscribe
    is_success
    stop_server
}

function run_test_unsubscribe {
    start_server
    echo "Running test unsubscribe..."
    pytest src/test.py::test_unsubscribe
    is_success
    stop_server
}

function run_test_publish {
    start_server
    echo "Running test publish..."
    pytest src/test.py::test_publish
    is_success
    stop_server
}

function run_test_list_topics {
    start_server
    echo "Running test list topics..."
    pytest src/test.py::test_list_topics
    is_success
    stop_server
}

function run_test_get_topic_status {
    start_server
    echo "Running test get topic status..."
    pytest src/test.py::test_get_topic_status
    is_success
    stop_server
}

function run_test_heartbeat {
    start_server
    echo "Running test heartbeat..."
    pytest src/test.py::test_heartbeat
    is_success
    stop_server
}

function run_test_cleanup_topic {
    start_server
    echo "Running test cleanup topic..."
    pytest src/test.py::test_cleanup_topic
    is_success
    stop_server
}


function run_all_tests {
    run_test_subscribe
    wait 1
    run_test_unsubscribe
    wait 1
    run_test_publish
    wait 1
    run_test_list_topics
    wait 1
    run_test_get_topic_status
    wait 1
    run_test_heartbeat
    wait 1
    run_test_cleanup_topic

    echo "============"
    echo "All tests passed"
}

run_all_tests