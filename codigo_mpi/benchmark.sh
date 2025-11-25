#!/bin/bash
# ==========================================
# MPI Matrix Multiplication Benchmark
# ==========================================
# Tests synchronous (P2P), asynchronous (Non-Blocking),
# and collective (Scatter/Gather) MPI algorithms
# across 1–160 processes with fixed matrix sizes.
# ==========================================

OUTPUT_FILE="results_full_fixed.csv"
EXECUTABLES=("mpi_coletiva" "mpi_p2p_bloqueante" "mpi_p2p_naobloqueante")
ALGO_NAMES=("Point-to-Point" "Non-Blocking" "Collective")

# Create or overwrite CSV header
echo "Algorithm,Processes,Matrix_Size,Execution_Time(s),Communication_Time(s),Communication_Overhead(%)" > $OUTPUT_FILE

# Fixed matrix sizes — enough to stress 44+ cores but not impossible
MATRIX_SIZES=(2000 4000 8000 10000 12000)

# Process counts from 1 to 160 (inclusive)
PROCESS_COUNTS=$(seq 1 4)

# ==========================================
# MAIN LOOP
# ==========================================
for n in "${MATRIX_SIZES[@]}"; do
    echo
    echo "==============================="
    echo " 🧮 Matrix size: $n x $n "
    echo "==============================="

    for np in $PROCESS_COUNTS; do
        echo "--- Running with $np process(es) ---"

        for i in ${!EXECUTABLES[@]}; do
            exe=${EXECUTABLES[$i]}
            algo=${ALGO_NAMES[$i]}

            # Ensure binary exists
            if [ ! -x "$exe" ]; then
                echo "⚠️  Skipping missing executable: $exe"
                continue
            fi

            # Run and capture output (suppress MPI noise)
            OUTPUT=$(mpirun -np $np ./$exe $n 2>/dev/null)

            # Extract times
            exec_time=$(echo "$OUTPUT" | grep "Execution time" | awk '{print $3}')
            comm_time=$(echo "$OUTPUT" | grep "Communication time" | awk '{print $3}')
            overhead=$(echo "$OUTPUT" | grep "overhead" | awk '{print $3}' | tr -d '%')

            # Log to CSV
            if [ -n "$exec_time" ]; then
                echo "$algo,$np,$n,$exec_time,${comm_time:-0},${overhead:-0}" >> $OUTPUT_FILE
                printf "✅ %-15s | %3d proc | n=%5d | time=%8.4fs\n" "$algo" "$np" "$n" "$exec_time"
            else
                echo "⚠️  $algo | $np proc | n=$n -> No valid timing output"
            fi
        done
    done
done

echo
echo "✅ Benchmark completed!"
echo "📄 Results saved in: $OUTPUT_FILE"
