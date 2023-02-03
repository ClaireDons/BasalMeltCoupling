#!/bin/bash

# Get first job id
jid=$(sbatch ECE_BISI_basal1.slurm| cut -d ' ' -f4)
echo $jid

## Remainder jobs
for k in {2..3};
    do temp="${k}"
        jid=$(sbatch --dependency=afterok:${jid} ECE_BISI_basal${k}.slurm | cut -d ' ' -f4)
        echo $jid
    done

## Wait for last job to finish before exiting script
sentence=$(squeue -j $jid | tr -s ' ' | cut -d ' ' -f6)
echo $sentence

until [[ "$sentence" =~ .*"COMPLETI".* ]]
do
    sentence=$(squeue -j $jid | tr -s ' ' | cut -d ' ' -f6)
    echo $sentence
    sleep 10
done

echo "done"