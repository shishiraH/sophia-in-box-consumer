#!/bin/bash

set -euo pipefail


function trace() {
    {
        local tracing
        [[ "$-" = *"x"* ]] && tracing=true || tracing=false
        set +x
    } 2>/dev/null
    if [ "$tracing" != true ]; then
        # Bash's own trace mode is off, so explicitely write the message.
        echo "$@" >&2
    else
        # Restore trace
        set -x
    fi
}


function contains () {
  local e match="$1"
  shift
  for e; do [[ "$e" == "$match" ]] && return 0; done
  return 1
}


# Parse arguments.
operations=()
targets=()
tail=10
follow=false
while true; do
    case "${1:-}" in
    start)
        operations+=( start )
        shift
        ;;
    stop)
        operations+=( stop )
        shift
        ;;
    destroy)
        operations+=( destroy )
        shift
        ;;
    tests)
        operations+=( tests )
        shift
        ;;
    logs)
        operations+=( logs )
        shift
        ;;
    --)
        shift
        break
        ;;
    -h|--help)
        operations+=( usage )
        shift
        ;;
    -f|--follow)
        follow=true
        shift
        ;;
    -n|--lines)
        shift
        tail="${1:-10}"
        shift
        ;;
    *)
        break
        ;;
    esac
done
if ! [[ ${operations[@]:+${operations[@]}} ]]; then
    operations=( usage )
fi
if [ "$#" -gt 0 ]; then
    targets=( "$@" )
fi


function usage() {
    trace "$0 <command> [options ...]"
    trace "Commands:"
    trace "    start    Start services and wait for them to be ready"
    trace "    stop     Stop services"
    trace "    destroy  Stop services and clear state (e.g. remove volumes)"
    trace "    tests    Run tests"
    trace "    logs     Output logs. When used with -f, this command will "
    trace "             continue following logs even when a service restarts."
    trace "Options:"
    trace "    -f, --follow     Follow logs. [false]"
    trace "    -n, --lines      Number of lines to tail from logs [10]"
    trace "Multiple commands may be specifed, e.g:"
    trace "$0 start logs"
    trace "Unrecognised arguments are passed through to inner command"
}


function start() {
    trace "Starting Sophia In-A-Box"
    docker-compose build
    docker-compose up -d localstack
    for i in $(seq 1 120); do
        rc=0
        curl -X PUT --output /dev/null --silent --fail http://localhost:4572/raw-test || rc="$?"
        if [ "$rc" = 0 ]; then
            break
        fi
        sleep 1
        printf .
    done
    if [ "$rc" != 0 ]; then
        trace "Failed to create bucket"
        exit 1
    fi

    docker-compose up -d "${targets[@]:+${targets[@]}}"
    ./status.sh
}


function destroy() {
    trace "Destroying Sophia In-A-Box"
    docker-compose down -v "${targets[@]:+${targets[@]}}"
}


function stop() {
    trace "Stopping Sophia In-A-Box"
    docker-compose down "${targets[@]:+${targets[@]}}"
}


function tests() {
    trace "Running tests"
    docker-compose -f docker-compose.tests.yml build
    docker-compose -f docker-compose.tests.yml run test-kafka
}


function logs() {
    local rc options
    trace "Displaying logs"
    rc=0
    options=( "--tail" "$tail" )
    if [ "$follow" = true ]; then
        options+=( "--follow" )
    fi
    while [ "$rc" -le 128 ]; do
        docker-compose logs "${options[@]}" "${targets[@]:+${targets[@]}}" \
            || rc=$?
        trace "Log stream ended"
        if [ "$follow" != true ]; then
            break
        fi
    done
}


script_directory="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
cd "${script_directory}/"


if contains usage "${operations[@]}"; then
    usage
    exit 1
fi
if contains start "${operations[@]}"; then
    start
fi
if contains tests "${operations[@]}"; then
    tests
fi
if contains stop "${operations[@]}"; then
    stop
fi
if contains destroy "${operations[@]}"; then
    destroy
fi
if contains logs "${operations[@]}"; then
    logs
fi


trace "Exited cleanly."