#!/usr/bin/env bash

function usage {
  echo "Usage: $(basename $0) [-hut] [-i interval]" 2>&1
  echo "Prints the status of all experiments and repetitions that are below the current directory."
  echo "  Options:"
  echo "   -h           Shows this message."
  echo "   -u           Only show the status of unfinished experiments to have a shorter output. Does not affect the final statistics line."
  echo "   -t           Query the status every i seconds until you force the command the quit using Ctrl+C."
  echo "   -i interval  If using the -t option, this is the interval in seconds between status updates. (Default: 5)"
}

is_show_finished=True
interval=5
is_trail=False

# handle arguments
while getopts ":huti:" arg; do
  case $arg in
    h) usage ; exit 1 ;;
    u) is_show_finished=False;;
    t) is_trail=True;;
    i) interval=$OPTARG;;
    ?) echo "Invalid option: -${OPTARG}."; usage ; exit 2 ;;
  esac
done
# get all arguments are given after the options handled by getopts
shift $(expr $OPTIND - 1 )
arguments=($@)

############################################

do_get_status=True
while [ $do_get_status = True ]; do

    if [ $is_trail = True ]; then
        clear
    fi

    # save statistics about how many scripts have a certain status
    declare -A statistics
    statistics[todo]=0
    statistics[running]=0
    statistics[finished]=0
    statistics[error]=0

    # identify all status files
    files=`find . -name *.status | sort -n`

    # go through them
    n_files=0
    for file in $files; do
        # read last 2 lines of status file, they have the format: "<date> <time>\n<status> <status_info>"
        status_message=$( tail -n 2 $file )

        # create array, which can be used to split a string based on spaces ' '
        status_message=($status_message)

        # get individual information from the status message
        date=${status_message[0]}
        time=${status_message[1]}
        status=${status_message[2]}
        status_info=
        for ((i=3; i<${#status_message[@]}; i+=1)); do
            status_info="$status_info ${status_message[$i]}"
        done

        # make status lowercase, for compatibility with older experiments where the status was capitalized
        status={"${status}" | tr 'A-Z' 'a-z'}

        # output status
        if [ "$is_show_finished" = False ]; then
            if ! [ "$status" = finished ]; then
                echo "$date $time $file - $status $status_info"
            fi
        else
            echo "$date $time $file - $status $status_info"
        fi

        # make status lowercase
        status={"${status}" | tr 'A-Z' 'a-z'}

        statistics[$status]=$((statistics[${status[0]}] + 1))

        ((n_files++))
    done

    # print statistics
    echo "total: ${n_files} | todo: ${statistics[todo]} | running: ${statistics[running]} | error: ${statistics[error]} | finished: ${statistics[finished]} "

    if [ $is_trail = False ]; then
        do_get_status=False
    else
        sleep $interval
    fi
done
