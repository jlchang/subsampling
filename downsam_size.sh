#!/bin/bash -i

#$ -cwd
use Samtools

echo "determining reads in $1"
samtools view -F 0x4 $1 | cut -f 1 | sort | uniq | wc - 
samtools flagstat $1
