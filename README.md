# Sistema-de-Estoque
Trabalho da matéria Programação e Plataformas de Alto Desempenho, da Universidade Veiga de Almeida. Disciplina guiado pelo professor Thiago Alberto Ramos Gabriel
# Controle de Estoque Concorrente em Python

Um script interativo de terminal que simula um sistema de controle de estoque utilizando **Concorrência, Multithreading e Memória Compartilhada** em Python. O projeto demonstra na prática o clássico problema do produtor-consumidor com sincronização baseada em Locks.

## Funcionalidades

* **Simulação em Tempo Real:** Threads independentes agindo como fornecedores (adicionando estoque) e clientes (consumindo estoque) simultaneamente.
* **Interface no Terminal:** Saída colorida (via ANSI escape codes) com painéis de relatórios periódicos e barras de progresso simuladas para o nível de estoque.
* **Thread Safety:** Uso rigoroso de `threading.Lock` para garantir que as operações de leitura e escrita no dicionário de estoque e nos contadores globais sejam seguras (evitando *race conditions*).
* **Alertas de Estoque:** Avisos visuais quando o estoque atinge níveis críticos ou se esgota, e alertas caso um cliente tente comprar e não haja disponibilidade.

## Conceitos Demonstrados

Este projeto é uma excelente referência para entender como a concorrência funciona em Python:

1.  **`threading.Thread`**: Criação de threads produtoras (fornecedor), consumidoras (clientes) e observadoras (relatório).
2.  **Memória Compartilhada**: Uso de um dicionário global (`estoque`) e contadores acessados por múltiplas threads.
3.  **Sincronização com `Lock`**: 
    * Uso do bloco `with lock:` (Context Manager) para aquisição e liberação segura e automática.
    * Uso manual com `lock.acquire()` e `lock.release()` em blocos `try/finally`.
4.  **Concorrência vs I/O**: Isolamento da "Seção Crítica". Os `prints` são feitos fora do Lock para não prender recursos à toa durante operações de I/O.

## Como Executar

### Pré-requisitos
* **Python 3.x** instalado. 
* Nenhuma biblioteca externa é necessária (o código usa apenas a biblioteca padrão do Python: `threading`, `time`, `random`, `datetime`).

### Passo a passo
1. Clone este repositório:
   ```bash
   git clone [https://github.com/SEU_USUARIO/NOME_DO_REPOSITORIO.git](https://github.com/SEU_USUARIO/NOME_DO_REPOSITORIO.git)
