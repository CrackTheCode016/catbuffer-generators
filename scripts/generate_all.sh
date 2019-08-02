#!/bin/bash

source "$(dirname $0)/../catbuffer/scripts/schema_lists.sh"
source "$(dirname $0)/../catbuffer/scripts/generate_batch.sh"

if [ "$#" -lt 1 ]; then
	echo "usage: script <builder> <nis2_root>"
	exit 1
fi

# "aggregate/aggregate" tracked by issue #26
delete=("aggregate/aggregate")
transaction_inputs_without_aggregate=(${transaction_inputs[@]}/${delete})

builder="$1"
if [ "$#" -lt 2 ]; then
	PYTHONPATH=".:${PYTHONPATH}" generate_batch ${transaction_inputs_without_aggregate} "catbuffer" ${builder}
else
	nis2_root="$2"
	rm -rf catbuffer/_generated/${builder}
	PYTHONPATH=".:${PYTHONPATH}" generate_batch ${transaction_inputs_without_aggregate} "catbuffer" ${builder}
	cp catbuffer/_generated/${builder}/* ${nis2_root}/sdk/src/builders/
fi
