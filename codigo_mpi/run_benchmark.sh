#!/bin/bash
# ==========================================
# SLURM Benchmark Script
# ==========================================
# Submete jobs SLURM para diferentes configurações
# de processos e tamanhos de matriz
# ==========================================

OUTPUT_FILE="results_full_fixed.csv"
EXECUTABLES=("mpi_coletiva" "mpi_p2p_bloqueante" "mpi_p2p_naobloqueante")
ALGO_NAMES=("Collective" "Point-to-Point" "Non-Blocking")

MATRIX_SIZES=(2000 4000 8000 10000 12000)

# Process counts from 1 to 4
PROCESS_COUNTS=$(seq 1 4)

# Caminho para o script SLURM
SLURM_SCRIPT="./run.slurm"

# ==========================================
# MAIN LOOP
# ==========================================
for n in "${MATRIX_SIZES[@]}"; do
    echo
    echo "==============================="
    echo " 🧮 Matrix size: $n x $n "
    echo "==============================="

    for np in $PROCESS_COUNTS; do
        echo "--- Submitting jobs with $np process(es) ---"

        for i in ${!EXECUTABLES[@]}; do
            exe=${EXECUTABLES[$i]}
            algo=${ALGO_NAMES[$i]}

            # Nome do job no SLURM
            JOB_NAME="${exe}_${n}_${np}proc"

            # Submete o job ao SLURM
            # --ntasks sobrescreve o valor no script
            # Passa tamanho da matriz e programa como argumentos
            JOB_ID=$(sbatch \
                --job-name="$JOB_NAME" \
                --ntasks=$np \
                --output="${JOB_NAME}_%j.out" \
                --error="${JOB_NAME}_%j.err" \
                $SLURM_SCRIPT $n $exe | awk '{print $4}')

            if [ -n "$JOB_ID" ]; then
                printf "✅ %-20s | %3d proc | n=%5d | Job ID: %s\n" "$algo" "$np" "$n" "$JOB_ID"
            else
                echo "⚠️  Erro ao submeter job: $algo | $np proc | n=$n"
            fi
        done
    done
done

echo
echo "✅ Todos os jobs foram submetidos!"
echo "📋 Use 'squeue -u $USER' para ver o status dos jobs"
echo "📄 Os resultados estarão nos arquivos .out de cada job"
