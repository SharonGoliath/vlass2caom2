#!/bin/bash

if [[ ! -e ${PWD}/config.yml ]]
then
  cp /config.yml ${PWD}
fi

if [[ ! -e ${PWD}/state.yml ]]
then
  yesterday=$(date -d yesterday "+%d-%b-%Y %H:%M")
  echo "bookmarks:
  vlass_timestamp:
    last_record: ${yesterday}
" > ${PWD}/state.yml
fi

exec "${@}"
