import os
import re
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict
import seaborn as sns
import pandas as pd

def main():
    # Diretório com os arquivos de saída
    results_dir = "../results/out/"

    # Estrutura para armazenar os dados
    # dados[tipo_mpi][tamanho_matriz][num_processos] = (exec_time, comm_time, comm_overhead)
    dados = defaultdict(lambda: defaultdict(dict))

    # Padrão para extrair informações do nome do arquivo
    # Exemplo: mpi_coletiva_10000_1proc_736545.out
    pattern = r"mpi_(.+?)_(\d+)_(\d+)proc_\d+\.out"

    # Ler todos os arquivos
    for filename in os.listdir(results_dir):
        if filename.endswith(".out"):
            match = re.match(pattern, filename)
            if match:
                tipo_mpi = match.group(1)
                tamanho_matriz = int(match.group(2))
                num_processos = int(match.group(3))
                
                # Ler o conteúdo do arquivo
                filepath = os.path.join(results_dir, filename)
                with open(filepath, 'r') as f:
                    content = f.read()
                    
                    # Extrair tempos
                    exec_time_match = re.search(r"Execution time: ([\d.]+)", content)
                    comm_time_match = re.search(r"Communication time: ([\d.]+)", content)
                    comm_overhead_match = re.search(r"Communication overhead: ([\d.]+)", content)
                    
                    if exec_time_match and comm_time_match:
                        exec_time = float(exec_time_match.group(1))
                        comm_time = float(comm_time_match.group(1))
                        comm_overhead = float(comm_overhead_match.group(1)) if comm_overhead_match else 0.0
                        
                        dados[tipo_mpi][tamanho_matriz][num_processos] = (exec_time, comm_time, comm_overhead)

    # Mapear nomes mais legíveis
    nome_tipos = {
        'coletiva': 'MPI Coletiva',
        'p2p_bloqueante': 'MPI P2P Bloqueante',
        'p2p_naobloqueante': 'MPI P2P Não-Bloqueante'
    }

    # Cores para cada número de processos
    cores = {1: 'blue', 2: 'green', 3: 'orange', 4: 'red'}
    marcadores = {1: 'o', 2: 's', 3: '^', 4: 'D'}

    # Criar um plot para cada tipo de MPI
    for tipo_mpi in sorted(dados.keys()):
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Plot 1: Tempo de Execução
        for num_proc in sorted(cores.keys()):
            tamanhos = []
            tempos_exec = []
            
            for tamanho in sorted(dados[tipo_mpi].keys()):
                if num_proc in dados[tipo_mpi][tamanho]:
                    tamanhos.append(tamanho)
                    tempos_exec.append(dados[tipo_mpi][tamanho][num_proc][0])
            
            if tamanhos:
                ax1.plot(tamanhos, tempos_exec, 
                        color=cores[num_proc], 
                        marker=marcadores[num_proc],
                        linewidth=2,
                        markersize=8,
                        label=f'{num_proc} processo(s)')
        
        ax1.set_xlabel('Tamanho da Matriz', fontsize=12)
        ax1.set_ylabel('Tempo de Execução (segundos)', fontsize=12)
        ax1.set_title(f'Tempo de Execução - {nome_tipos.get(tipo_mpi, tipo_mpi)}', fontsize=14, fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Tempo de Comunicação
        for num_proc in sorted(cores.keys()):
            tamanhos = []
            tempos_comm = []
            
            for tamanho in sorted(dados[tipo_mpi].keys()):
                if num_proc in dados[tipo_mpi][tamanho]:
                    tamanhos.append(tamanho)
                    tempos_comm.append(dados[tipo_mpi][tamanho][num_proc][1])
            
            if tamanhos:
                ax2.plot(tamanhos, tempos_comm, 
                        color=cores[num_proc], 
                        marker=marcadores[num_proc],
                        linewidth=2,
                        markersize=8,
                        label=f'{num_proc} processo(s)')
        
        ax2.set_xlabel('Tamanho da Matriz', fontsize=12)
        ax2.set_ylabel('Tempo de Comunicação (segundos)', fontsize=12)
        ax2.set_title(f'Tempo de Comunicação - {nome_tipos.get(tipo_mpi, tipo_mpi)}', fontsize=14, fontweight='bold')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Salvar figura
        output_filename = f'plot_{tipo_mpi}.png'
        plt.savefig(output_filename, dpi=300, bbox_inches='tight')
        print(f"Plot salvo: {output_filename}")
        
        plt.close()

    # Criar um plot comparativo entre os três tipos de MPI (apenas tempo de execução)
    fig, ax = plt.subplots(figsize=(14, 8))

    estilos_linha = {'coletiva': '-', 'p2p_bloqueante': '--', 'p2p_naobloqueante': '-.'}

    for tipo_mpi in sorted(dados.keys()):
        for num_proc in sorted(cores.keys()):
            tamanhos = []
            tempos_exec = []
            
            for tamanho in sorted(dados[tipo_mpi].keys()):
                if num_proc in dados[tipo_mpi][tamanho]:
                    tamanhos.append(tamanho)
                    tempos_exec.append(dados[tipo_mpi][tamanho][num_proc][0])
            
            if tamanhos:
                ax.plot(tamanhos, tempos_exec, 
                    color=cores[num_proc], 
                    linestyle=estilos_linha.get(tipo_mpi, '-'),
                    marker=marcadores[num_proc],
                    linewidth=2,
                    markersize=8,
                    label=f'{nome_tipos.get(tipo_mpi, tipo_mpi)} - {num_proc} proc')

    ax.set_xlabel('Tamanho da Matriz', fontsize=12)
    ax.set_ylabel('Tempo de Execução (segundos)', fontsize=12)
    ax.set_title('Comparação de Tempo de Execução entre Tipos de MPI', fontsize=14, fontweight='bold')
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('plot_comparativo_todos.png', dpi=300, bbox_inches='tight')
    print("Plot comparativo salvo: plot_comparativo_todos.png")
    plt.close()

    # Criar heatmaps de Communication Overhead para cada tipo de MPI
    print("\nGerando heatmaps de Communication Overhead...")

    for tipo_mpi in sorted(dados.keys()):
        # Preparar dados para o heatmap
        tamanhos = sorted(dados[tipo_mpi].keys())
        processos = sorted(set(num_proc for tamanho_data in dados[tipo_mpi].values() 
                            for num_proc in tamanho_data.keys()))
        
        # Criar matriz para o heatmap
        overhead_matrix = []
        for tamanho in tamanhos:
            row = []
            for num_proc in processos:
                if num_proc in dados[tipo_mpi][tamanho]:
                    overhead = dados[tipo_mpi][tamanho][num_proc][2]
                    row.append(overhead)
                else:
                    row.append(np.nan)
            overhead_matrix.append(row)
        
        # Criar DataFrame
        df = pd.DataFrame(overhead_matrix, 
                        index=[f'{t}' for t in tamanhos],
                        columns=[f'{p} proc' for p in processos])
        
        # Criar heatmap
        fig, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(df, annot=True, fmt='.2f', cmap='YlOrRd', 
                    cbar_kws={'label': 'Overhead (%)'}, 
                    linewidths=0.5, linecolor='gray',
                    vmin=0, ax=ax)
        
        ax.set_xlabel('Número de Processos', fontsize=12)
        ax.set_ylabel('Tamanho da Matriz', fontsize=12)
        ax.set_title(f'Communication Overhead (%) - {nome_tipos.get(tipo_mpi, tipo_mpi)}', 
                    fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        output_filename = f'heatmap_overhead_{tipo_mpi}.png'
        plt.savefig(output_filename, dpi=300, bbox_inches='tight')
        print(f"Heatmap salvo: {output_filename}")
        plt.close()

    # Criar heatmap comparativo (média de overhead por tipo de MPI e número de processos)
    print("\nGerando heatmap comparativo de overhead médio...")

    # Calcular médias
    media_overhead = defaultdict(lambda: defaultdict(list))
    for tipo_mpi in dados.keys():
        for tamanho in dados[tipo_mpi].keys():
            for num_proc in dados[tipo_mpi][tamanho].keys():
                overhead = dados[tipo_mpi][tamanho][num_proc][2]
                media_overhead[tipo_mpi][num_proc].append(overhead)

    # Criar matriz de médias
    tipos_ordenados = sorted(dados.keys())
    processos_ordenados = sorted(set(num_proc for tipo_data in media_overhead.values() 
                                    for num_proc in tipo_data.keys()))

    matriz_media = []
    for tipo_mpi in tipos_ordenados:
        row = []
        for num_proc in processos_ordenados:
            if num_proc in media_overhead[tipo_mpi] and media_overhead[tipo_mpi][num_proc]:
                media = np.mean(media_overhead[tipo_mpi][num_proc])
                row.append(media)
            else:
                row.append(np.nan)
        matriz_media.append(row)

    df_media = pd.DataFrame(matriz_media,
                        index=[nome_tipos.get(t, t) for t in tipos_ordenados],
                        columns=[f'{p} proc' for p in processos_ordenados])

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(df_media, annot=True, fmt='.2f', cmap='YlOrRd',
                cbar_kws={'label': 'Overhead Médio (%)'}, 
                linewidths=0.5, linecolor='gray',
                vmin=0, ax=ax)

    ax.set_xlabel('Número de Processos', fontsize=12)
    ax.set_ylabel('Tipo de MPI', fontsize=12)
    ax.set_title('Communication Overhead Médio (%) - Comparação entre Tipos de MPI', 
                fontsize=14, fontweight='bold')

    plt.tight_layout()
    plt.savefig('heatmap_overhead_comparativo.png', dpi=300, bbox_inches='tight')
    print("Heatmap comparativo salvo: heatmap_overhead_comparativo.png")
    plt.close()

    print("\nResumo dos dados coletados:")
    for tipo_mpi in sorted(dados.keys()):
        print(f"\n{nome_tipos.get(tipo_mpi, tipo_mpi)}:")
        for tamanho in sorted(dados[tipo_mpi].keys()):
            print(f"  Tamanho {tamanho}:", end="")
            for num_proc in sorted(dados[tipo_mpi][tamanho].keys()):
                exec_time, comm_time, comm_overhead = dados[tipo_mpi][tamanho][num_proc]
                print(f" {num_proc}proc={exec_time:.2f}s (overhead: {comm_overhead:.2f}%)", end="")
            print()


if __name__ == "__main__":
    main()
