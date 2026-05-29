import threading
import time
import random
from datetime import datetime

# MEMORIA COMPARTILHADA — dicionario acessado por todas as threads
estoque = {
    "Arroz":    50,
    "Feijao":   30,
    "Macarrao": 40,
    "Oleo":     20,
    "Acucar":   25,
}

# Historico de operacoes tambem e memoria compartilhada
historico = []

# Contadores globais compartilhados
total_reposicoes = 0
total_vendas     = 0
total_alertas    = 0

# LOCK — unico mecanismo de sincronizacao do programa
# Protege: estoque, historico e contadores
lock = threading.Lock()

# Flag de controle (leitura simples, nao precisa de lock)
rodando = True

# CORES ANSI
class Cor:
    RESET   = "\033[0m"
    VERDE   = "\033[92m"
    AMARELO = "\033[93m"
    VERMELHO= "\033[91m"
    AZUL    = "\033[94m"
    CIANO   = "\033[96m"
    BRANCO  = "\033[97m"
    NEGRITO = "\033[1m"


def agora():
    return datetime.now().strftime("%H:%M:%S")


def imprimir_titulo():
    print(f"\n{Cor.CIANO}{Cor.NEGRITO}")
    print("╔══════════════════════════════════════════════════════════╗")
    print("║      CONTROLE DE ESTOQUE CONCORRENTE — Python            ║")
    print("║      Threads | Memoria Compartilhada | Lock              ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print(f"{Cor.RESET}")


def imprimir_estoque_inicial():
    print(f"{Cor.AZUL}{Cor.NEGRITO}ESTOQUE INICIAL:{Cor.RESET}")
    # Leitura segura da memoria compartilhada
    with lock:
        for produto, qtd in estoque.items():
            barra = "█" * (qtd // 5)
            print(f"  {produto:<12} | {barra:<12} {qtd:>3} unidades")
    print()

# THREAD 1: FORNECEDOR — repoe produtos na memoria compartilhada
def thread_fornecedor(nome: str, intervalo: float):
    """
    Repoe periodicamente produtos no estoque.
    Adquire o Lock antes de qualquer acesso ao dicionario.
    """
    global total_reposicoes

    while rodando:
        time.sleep(intervalo + random.uniform(0, 0.5))

        produto    = random.choice(list(estoque.keys()))
        quantidade = random.randint(5, 20)

        # == SECAO CRITICA: Lock adquirido ==
        lock.acquire()
        try:
            estoque[produto] += quantidade
            saldo = estoque[produto]
            total_reposicoes += 1
            historico.append({
                "tipo":      "REPOSICAO",
                "thread":    nome,
                "produto":   produto,
                "quantidade": quantidade,
                "saldo":     saldo,
                "hora":      agora(),
            })
        finally:
            lock.release()
        # == FIM DA SECAO CRITICA ==

        # Exibe fora do lock para nao segurar o recurso durante I/O
        print(
            f"{Cor.AMARELO}[{agora()}]{Cor.RESET} "
            f"[+] {Cor.VERDE}{Cor.NEGRITO}REPOSICAO {Cor.RESET}"
            f"| {nome:<12} | {produto:<12} | "
            f"+{quantidade:>2} un | saldo: {saldo:>3}"
        )

# THREAD 2/3/4: CLIENTE — consome produtos da memoria compartilhada
def thread_cliente(nome: str, intervalo: float):
    """
    Simula compras reduzindo o estoque.
    Usa 'with lock' para garantir acesso exclusivo.
    """
    global total_vendas, total_alertas

    while rodando:
        time.sleep(intervalo + random.uniform(0, 0.8))

        produto    = random.choice(list(estoque.keys()))
        quantidade = random.randint(1, 8)

        # == SECAO CRITICA: com 'with' o lock e liberado automaticamente ==
        with lock:
            if estoque[produto] >= quantidade:
                estoque[produto] -= quantidade
                saldo   = estoque[produto]
                sucesso = True
                total_vendas += 1
            else:
                saldo   = estoque[produto]
                sucesso = False
                total_alertas += 1

            historico.append({
                "tipo":       "VENDA"   if sucesso else "ALERTA",
                "thread":     nome,
                "produto":    produto,
                "quantidade": quantidade,
                "saldo":      saldo,
                "hora":       agora(),
            })
        # == FIM DA SECAO CRITICA ==

        if sucesso:
            aviso = ""
            if saldo <= 5:
                aviso = f" {Cor.AMARELO}<- ESTOQUE BAIXO!{Cor.RESET}"
            print(
                f"{Cor.AMARELO}[{agora()}]{Cor.RESET} "
                f"[-] {Cor.BRANCO}{Cor.NEGRITO}VENDA     {Cor.RESET}"
                f"| {nome:<12} | {produto:<12} | "
                f"-{quantidade:>2} un | saldo: {saldo:>3}{aviso}"
            )
        else:
            print(
                f"{Cor.AMARELO}[{agora()}]{Cor.RESET} "
                f"[!] {Cor.VERMELHO}{Cor.NEGRITO}ALERTA    {Cor.RESET}"
                f"| {nome:<12} | {produto:<12} | "
                f"-{quantidade:>2} un | saldo: {saldo:>3} "
                f"{Cor.VERMELHO}<- ESTOQUE INSUFICIENTE!{Cor.RESET}"
            )

# THREAD 5: RELATORIO — le a memoria compartilhada periodicamente
def thread_relatorio(intervalo: float):
    """
    Le o estado atual da memoria compartilhada (com Lock)
    e exibe um snapshot periodico.
    """
    contador = 0
    while rodando:
        time.sleep(intervalo)
        contador += 1

        # Leitura segura — adquire lock para copiar o estado atual
        with lock:
            snapshot  = dict(estoque)
            rep = total_reposicoes
            ven = total_vendas
            ale = total_alertas

        print(f"\n{Cor.CIANO}{'─'*60}")
        print(f"  RELATORIO #{contador}  |  {agora()}")
        print(f"  Reposicoes: {rep}  |  Vendas: {ven}  |  Alertas: {ale}")
        print(f"{'─'*60}{Cor.RESET}")
        for produto, qtd in snapshot.items():
            if qtd == 0:
                cor_qtd = Cor.VERMELHO
                status  = " <- ESGOTADO"
            elif qtd <= 5:
                cor_qtd = Cor.AMARELO
                status  = " <- CRITICO"
            else:
                cor_qtd = Cor.VERDE
                status  = ""
            barra = "█" * min(qtd // 5, 20)
            print(
                f"  {produto:<12} | {cor_qtd}{barra:<20}{Cor.RESET} "
                f"{cor_qtd}{qtd:>3} un{Cor.RESET}{status}"
            )
        print(f"{Cor.CIANO}{'─'*60}{Cor.RESET}\n")

# MAIN — cria e inicia todas as threads
def main():
    global rodando

    imprimir_titulo()
    imprimir_estoque_inicial()

    print(f"{Cor.AZUL}Iniciando threads...{Cor.RESET}\n")

    threads = [
        threading.Thread(target=thread_fornecedor, args=("Fornecedor-1", 1.5), daemon=True, name="Fornecedor-1"),
        threading.Thread(target=thread_cliente,    args=("Cliente-A",    0.8), daemon=True, name="Cliente-A"),
        threading.Thread(target=thread_cliente,    args=("Cliente-B",    1.0), daemon=True, name="Cliente-B"),
        threading.Thread(target=thread_cliente,    args=("Cliente-C",    1.2), daemon=True, name="Cliente-C"),
        threading.Thread(target=thread_relatorio,  args=(5.0,),               daemon=True, name="Relatorio"),
    ]

    print(f"{Cor.AMARELO}THREADS ATIVAS:{Cor.RESET}")
    for t in threads:
        tipo = "Produtora" if "Fornecedor" in t.name else \
               "Consumidora" if "Cliente" in t.name else "Relatorio"
        print(f"  * {t.name:<14} -> {tipo}")

    print(f"\n{Cor.AMARELO}SINCRONIZACAO:{Cor.RESET}")
    print(f"  [Lock] -> protege 'estoque', 'historico' e contadores (memoria compartilhada)")
    print(f"  [Sem Queue] -> threads escrevem e leem diretamente na memoria via Lock\n")
    print(f"{Cor.VERDE}{'═'*60}{Cor.RESET}")
    print(f"{Cor.BRANCO}  Pressione CTRL+C para encerrar{Cor.RESET}")
    print(f"{Cor.VERDE}{'═'*60}{Cor.RESET}\n")

    for t in threads:
        t.start()

    try:
        time.sleep(30)
    except KeyboardInterrupt:
        print(f"\n{Cor.AMARELO}Encerrando...{Cor.RESET}")

    rodando = False
    time.sleep(0.5)

    # Relatorio final lendo a memoria compartilhada
    with lock:
        snapshot_final = dict(estoque)
        rep, ven, ale  = total_reposicoes, total_vendas, total_alertas
        total_ops      = len(historico)

    print(f"\n{Cor.CIANO}{Cor.NEGRITO}{'═'*60}")
    print(f"  SIMULACAO ENCERRADA — RESULTADO FINAL")
    print(f"{'═'*60}{Cor.RESET}")
    print(f"  Reposicoes : {Cor.VERDE}{rep}{Cor.RESET}")
    print(f"  Vendas     : {Cor.BRANCO}{ven}{Cor.RESET}")
    print(f"  Alertas    : {Cor.VERMELHO}{ale}{Cor.RESET}")
    print(f"  Total ops  : {total_ops} (registradas no historico compartilhado)")
    print(f"\n  ESTOQUE FINAL:")
    for produto, qtd in snapshot_final.items():
        cor = Cor.VERDE if qtd > 10 else (Cor.AMARELO if qtd > 0 else Cor.VERMELHO)
        print(f"    {produto:<12} -> {cor}{qtd} unidades{Cor.RESET}")
    print(f"{Cor.CIANO}{'═'*60}{Cor.RESET}\n")

if __name__ == "__main__":
    main()