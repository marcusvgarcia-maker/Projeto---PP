#!/usr/bin/env python3
"""Campanha conjunta de Lloyd: forte, fraca e perfilamento para Amdahl."""
import argparse
import csv
import hashlib
import json
import math
import os
import platform
import random
import re
import shutil
import signal
import subprocess
import sys
import time
from contextlib import ExitStack
from datetime import datetime, timedelta, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
FLAGS = ["-O2", "-std=c++17"]
NUMERO = r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?"
SAIDA = re.compile(
    rf"^N=(\d+)\s+K=(\d+)\s+it=(\d+)\s+checksum=({NUMERO})"
    rf"\s+tempo=({NUMERO})\s+s\s*$", re.MULTILINE)
CAMPOS = ["N", "K", "IT", "versao", "workers", "repeticao",
          "checksum", "tempo_s", "tempo_parede_s", "log"]
PERFIL_CAMPOS = ["N", "K", "IT", "repeticao", "checksum",
                 "atribuicao_s", "acumulacao_s", "total_s", "log"]
FONTES = [
    "sequencial/10_kmeans.cpp", "openmp/10_kmeans.cpp", "mpi/10_kmeans.cpp",
    "validacao/sequencial.cpp", "perfilamento/10_kmeans_amdahl.cpp",
    "scripts/medir_campanha_docker.py", "scripts/analisar_campanha_docker.py",
    "Makefile", "Dockerfile", "docker-compose.yml",
]


def agora():
    try:
        from zoneinfo import ZoneInfo
        return datetime.now(ZoneInfo("America/Sao_Paulo"))
    except (ImportError, KeyError):
        return datetime.now(timezone(timedelta(hours=-3)))


def inteiros(texto):
    try:
        valores = sorted(set(int(x) for x in texto.split(",")))
        if not valores or min(valores) < 1:
            raise ValueError()
        return valores
    except ValueError:
        raise argparse.ArgumentTypeError("Use inteiros positivos separados por virgula.")


def extrair_saida(texto, n, k, it):
    encontrados = SAIDA.findall(texto)
    if len(encontrados) != 1:
        raise ValueError("Esperada exatamente uma linha de resultado do K-means.")
    nn, kk, ii, checksum, tempo = encontrados[0]
    if (int(nn), int(kk), int(ii)) != (n, k, it):
        raise ValueError("A saida nao corresponde a entrada solicitada.")
    valor = float(tempo)
    if not math.isfinite(float(checksum)) or not math.isfinite(valor) or valor <= 0:
        raise ValueError("Checksum/tempo invalido; use entradas com tempo mensuravel.")
    return checksum, valor


def centroides(texto, k):
    valores = {}
    for linha in texto.splitlines():
        if not linha.startswith("CENTROIDE "):
            continue
        p = linha.split()
        if len(p) != 4:
            raise ValueError("Linha de centroide invalida.")
        j = int(p[1])
        xy = (float(p[2]), float(p[3]))
        if j in valores or not 0 <= j < k or not all(map(math.isfinite, xy)):
            raise ValueError("Centroide duplicado, nao finito ou fora do intervalo.")
        valores[j] = xy
    if set(valores) != set(range(k)):
        raise ValueError("Quantidade de centroides incorreta.")
    return valores


def ler(path):
    try:
        return Path(path).read_text().strip()
    except OSError:
        return None


def versao(comando):
    try:
        p = subprocess.run(comando, capture_output=True, text=True, timeout=15)
        return p.stdout.strip() if p.returncode == 0 else p.stderr.strip()
    except (OSError, subprocess.TimeoutExpired):
        return None


def git_atual():
    # A imagem oficial nao instala Git; as referencias podem ser lidas da montagem.
    pasta = RAIZ / ".git"
    head = ler(pasta / "HEAD")
    if head and head.startswith("ref: "):
        ref = head[5:]
        commit = ler(pasta / ref)
        if not commit:
            for linha in (ler(pasta / "packed-refs") or "").splitlines():
                campos = linha.split()
                if len(campos) == 2 and campos[1] == ref:
                    commit = campos[0]
                    break
        return {"branch": ref.removeprefix("refs/heads/"), "commit": commit}
    return {"branch": None, "commit": head}


class Executor:
    def __init__(self, pasta, timeout):
        self.pasta, self.timeout, self.contador = pasta, timeout, 0
        (pasta / "logs").mkdir()

    def executar(self, comando, etiqueta, env=None):
        self.contador += 1
        log = self.pasta / "logs" / f"{self.contador:04d}_{etiqueta}.txt"
        ambiente = dict(os.environ)
        ambiente.update({"LC_ALL": "C", "OMP_DYNAMIC": "FALSE",
                         "OMP_PROC_BIND": "FALSE", "OMP_NUM_THREADS": "1"})
        ambiente.pop("GOMP_CPU_AFFINITY", None)
        ambiente.update(env or {})
        inicio = time.perf_counter()
        p = subprocess.Popen(
            [str(x) for x in comando], cwd=RAIZ, env=ambiente,
            stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, start_new_session=True)
        expirou = False
        try:
            stdout, stderr = p.communicate(timeout=self.timeout)
        except subprocess.TimeoutExpired:
            expirou = True
            try:
                os.killpg(p.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            stdout, stderr = p.communicate()
        parede = time.perf_counter() - inicio
        log.write_text(
            "COMANDO: " + json.dumps([str(x) for x in comando]) +
            f"\nRETORNO: {p.returncode}\nTIMEOUT: {expirou}\n" +
            f"TEMPO_PAREDE_S: {parede:.9f}\n\nSTDOUT:\n{stdout}\nSTDERR:\n{stderr}",
            encoding="utf-8")
        if expirou or p.returncode:
            raise RuntimeError(f"Falha em {etiqueta}; consulte {log}.")
        return stdout, parede, str(log.relative_to(self.pasta))


def comando(modelo, workers, n, k, it):
    nomes = {"sequencial": "10_kmeans_base", "openmp": "10_kmeans_omp",
             "mpi": "10_kmeans_mpi", "perfil": "10_kmeans_amdahl"}
    cmd = [str(RAIZ / "build" / nomes[modelo]), str(n), str(k), str(it)]
    if modelo == "mpi":
        cmd = ["mpirun", "--oversubscribe", "--bind-to", "none",
               "-np", str(workers)] + cmd
    return cmd


def medir(executor, modelo, workers, n, k, it, repeticao, checksum, etiqueta):
    texto, parede, log = executor.executar(
        comando(modelo, workers, n, k, it), etiqueta,
        {"OMP_NUM_THREADS": str(workers if modelo == "openmp" else 1)})
    obtido, tempo = extrair_saida(texto, n, k, it)
    if obtido != checksum:
        raise ValueError(f"Checksum divergente: {modelo}, N={n}, workers={workers}.")
    return dict(N=n, K=k, IT=it, versao=modelo, workers=workers,
                repeticao=repeticao, checksum=obtido, tempo_s=tempo,
                tempo_parede_s=parede, log=log), texto


def abrir_csv(stack, arquivo, campos):
    f = stack.enter_context(arquivo.open("w", newline="", encoding="utf-8"))
    writer = csv.DictWriter(f, fieldnames=campos, lineterminator="\n")
    writer.writeheader()
    return writer, f


def coletar(args, pasta, meta):
    executor = Executor(pasta, args.timeout)
    alvos = ["baseline", "build/validacao_seq"]
    if "openmp" in args.modelos:
        alvos.append("openmp")
    if "mpi" in args.modelos:
        alvos.append("mpi")
    executor.executar(
        ["make", "-B", "CXXFLAGS=" + " ".join(FLAGS)] + alvos, "compilacao")
    executor.executar(
        ["g++"] + FLAGS + [RAIZ / "perfilamento/10_kmeans_amdahl.cpp",
                           "-o", RAIZ / "build/10_kmeans_amdahl"],
        "compilacao_perfilador")
    meta["fontes_sha256"] = {}
    for nome in FONTES:
        p = RAIZ / nome
        if p.is_file():
            meta["fontes_sha256"][nome] = hashlib.sha256(p.read_bytes()).hexdigest()
            destino = pasta / "fontes" / nome
            destino.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, destino)
    meta["validacoes_preexistentes_copiadas"] = []
    for nome in ("validacao_openmp.csv", "validacao_centroides_mpi.csv"):
        origem = RAIZ / "resultados" / nome
        if origem.is_file():
            destino = pasta / "validacoes_preexistentes" / nome
            destino.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(origem, destino)
            meta["validacoes_preexistentes_copiadas"].append(nome)
    referencias = {}
    tamanhos = set(args.tamanhos)
    if not args.sem_fraca:
        tamanhos.update(args.n_fraca * p for p in args.workers)
    for n in sorted(tamanhos):
        texto, _, _ = executor.executar(
            [RAIZ / "build/validacao_seq", str(n), str(args.k), str(args.it)],
            f"referencia_N{n}")
        referencias[n] = extrair_saida(texto, n, args.k, args.it)[0]
        if n in args.tamanhos:
            perf, _, _ = executor.executar(
                comando("perfil", 1, n, args.k, args.it) + ["--centroides"],
                f"validacao_perfilador_N{n}")
            if centroides(perf, args.k) != centroides(texto, args.k):
                raise ValueError(f"Perfilador alterou os centroides para N={n}.")
            if extrair_saida(perf, n, args.k, args.it)[0] != referencias[n]:
                raise ValueError("Checksum divergente no perfilador.")
    meta["checksums"] = {str(n): c for n, c in referencias.items()}
    meta["perfilador_centroides_validados"] = list(args.tamanhos)
    rng = random.Random(args.semente_ordem)
    configuracoes = [("sequencial", 1)] + [
        (m, p) for m in args.modelos if m != "sequencial" for p in args.workers]
    meta["configuracoes_fortes"] = [[n, m, p] for n in args.tamanhos
                                   for m, p in configuracoes]
    fracas = [(args.n_fraca * p, m, p)
              for m in args.modelos if m != "sequencial" for p in args.workers]
    meta["configuracoes_fracas"] = [] if args.sem_fraca else [list(x) for x in fracas]
    with ExitStack() as stack:
        forte, ff = abrir_csv(stack, pasta / "forte.csv", CAMPOS)
        fraca, fw = abrir_csv(stack, pasta / "fraca.csv", CAMPOS)
        perfil, fp = abrir_csv(stack, pasta / "perfilamento.csv", PERFIL_CAMPOS)
        for n in args.tamanhos:
            print(f"FORTE: N={n}", flush=True)
            for m, p in configuracoes:
                for aquecimento in range(args.aquecimentos):
                    medir(executor, m, p, n, args.k, args.it, 0, referencias[n],
                          f"forte_aquecimento_N{n}_{m}_P{p}_{aquecimento}")
            for r in range(1, args.repeticoes + 1):
                ordem = list(configuracoes)
                rng.shuffle(ordem)
                for m, p in ordem:
                    linha, _ = medir(executor, m, p, n, args.k, args.it, r,
                                     referencias[n], f"forte_N{n}_{m}_P{p}_R{r}")
                    forte.writerow(linha)
                    ff.flush()
                print(f"  rodada {r}/{args.repeticoes} concluida", flush=True)
        if not args.sem_fraca:
            print(f"FRACA: N/worker={args.n_fraca}", flush=True)
            for n, m, p in fracas:
                for aq in range(args.aquecimentos):
                    medir(executor, m, p, n, args.k, args.it, 0, referencias[n],
                          f"fraca_aquecimento_N{n}_{m}_P{p}_{aq}")
            for r in range(1, args.repeticoes + 1):
                ordem = list(fracas)
                rng.shuffle(ordem)
                for n, m, p in ordem:
                    linha, _ = medir(executor, m, p, n, args.k, args.it, r,
                                     referencias[n], f"fraca_N{n}_{m}_P{p}_R{r}")
                    fraca.writerow(linha)
                    fw.flush()
                print(f"  rodada {r}/{args.repeticoes} concluida", flush=True)
        for n in args.tamanhos:
            print(f"PERFILAMENTO: N={n}", flush=True)
            for aq in range(args.aquecimentos):
                medir(executor, "perfil", 1, n, args.k, args.it, 0, referencias[n],
                      f"perfil_aquecimento_N{n}_{aq}")
            for r in range(1, args.repeticoes + 1):
                linha, texto = medir(
                    executor, "perfil", 1, n, args.k, args.it, r, referencias[n],
                    f"perfil_N{n}_R{r}")
                valores = re.findall(
                    rf"^PERFIL atribuicao_s=({NUMERO}) acumulacao_s=({NUMERO}) "
                    rf"total_s=({NUMERO})\s*$", texto, re.MULTILINE)
                if len(valores) != 1:
                    raise ValueError("Saida de perfilamento invalida.")
                a, c, total = map(float, valores[0])
                if (not all(math.isfinite(v) for v in (a, c, total)) or
                        min(a, c) < 0 or total <= 0 or a + c > total * (1 + 1e-9)):
                    raise ValueError("Tempos de perfilamento inconsistentes.")
                perfil.writerow(dict(
                    N=n, K=args.k, IT=args.it, repeticao=r,
                    checksum=linha["checksum"], atribuicao_s=a, acumulacao_s=c,
                    total_s=total, log=linha["log"]))
                fp.flush()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--saida", help="Pasta NOVA para a campanha; padrao: resultados/campanha_docker_DATA.")
    p.add_argument("--tamanhos", type=inteiros, default=[100000, 1000000, 5000000])
    p.add_argument("--workers", type=inteiros, default=[1, 2, 4])
    p.add_argument("--modelos", default="sequencial,openmp,mpi")
    p.add_argument("--repeticoes", type=int, default=5)
    p.add_argument("--aquecimentos", type=int, default=1)
    p.add_argument("--n-fraca", type=int, default=1000000)
    p.add_argument("--k", type=int, default=8)
    p.add_argument("--it", type=int, default=20)
    p.add_argument("--timeout", type=float, default=180)
    p.add_argument("--semente-ordem", type=int, default=20261111)
    p.add_argument("--observacoes", default="", help="Condicoes reais de energia/carga concorrente.")
    p.add_argument("--sem-fraca", action="store_true")
    p.add_argument("--sem-analise", action="store_true")
    args = p.parse_args()
    args.modelos = list(dict.fromkeys(args.modelos.split(",")))
    if (not args.modelos or "sequencial" not in args.modelos or
            set(args.modelos) - {"sequencial", "openmp", "mpi"}):
        p.error("--modelos deve incluir sequencial e usar somente sequencial,openmp,mpi.")
    if (1 not in args.workers or args.repeticoes < 2 or args.aquecimentos < 0 or
            args.n_fraca < args.k or args.k < 1 or min(args.tamanhos) < args.k or
            args.it < 1 or args.timeout <= 0):
        p.error("Requer worker 1, repeticoes >= 2, aquecimentos >= 0, N >= K >= 1 e IT >= 1.")
    for nome in ["make", "g++"] + (["mpirun", "mpic++"] if "mpi" in args.modelos else []):
        if not shutil.which(nome):
            p.error(f"Ferramenta ausente: {nome}. Execute dentro do ambiente Docker preparado.")
    if not args.sem_analise:
        try:
            import matplotlib  # noqa: F401
        except ImportError:
            p.error("Matplotlib ausente: reconstrua a imagem que inclui python3-matplotlib.")
    disponiveis = len(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else os.cpu_count()
    if disponiveis is not None and max(args.workers) > disponiveis:
        p.error(f"Foram solicitados {max(args.workers)} workers para {disponiveis} CPUs disponiveis.")
    pasta = Path(args.saida) if args.saida else Path("resultados") / (
        "campanha_docker_" + agora().strftime("%Y%m%d_%H%M%S"))
    if not pasta.is_absolute():
        pasta = RAIZ / pasta
    if Path(str(pasta) + "_para_enviar.zip").exists():
        p.error("O ZIP correspondente ja existe; escolha outra pasta de saida.")
    try:
        pasta.mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        p.error(f"A pasta ja existe; escolha outra --saida: {pasta}")
    meta = {
        "inicio": agora().isoformat(), "estado": "em_andamento",
        "argumentos": vars(args), "git": git_atual(),
        "plataforma": platform.platform(), "python": sys.version,
        "cpu_count": os.cpu_count(),
        "afinidade_cpu": sorted(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else None,
        "os_release": ler("/etc/os-release"),
        "cpu_modelos": sorted({x.split(":", 1)[1].strip()
                              for x in (ler("/proc/cpuinfo") or "").splitlines()
                              if x.startswith("model name")}),
        "meminfo": {x.split(":", 1)[0]: x.split(":", 1)[1].strip()
                    for x in (ler("/proc/meminfo") or "").splitlines()
                    if x.startswith(("MemTotal:", "MemAvailable:"))},
        "cgroup": {nome: ler("/sys/fs/cgroup/" + nome)
                   for nome in ["cpu.max", "cpuset.cpus.effective", "memory.max"]},
        "g++": versao(["g++", "--version"]),
        "mpi": versao(["mpirun", "--version"]) if "mpi" in args.modelos else None,
        "flags": FLAGS, "OMP_DYNAMIC": "FALSE", "OMP_PROC_BIND": "FALSE",
        "ambiente_relevante_herdado": {nome: os.environ.get(nome) for nome in
            ("OMP_WAIT_POLICY", "GOMP_SPINCOUNT", "OMP_PLACES",
             "OMPI_ALLOW_RUN_AS_ROOT", "OMPI_ALLOW_RUN_AS_ROOT_CONFIRM")},
        "MPI_argumentos": ["--oversubscribe", "--bind-to", "none"],
        "escopo_tempo": "tempo_s = iteracoes reportadas pelo programa; exclui geracao e distribuicao inicial.",
        "escopo_parede": "tempo_parede_s = duracao externa do subprocesso, incluindo inicializacao e geracao.",
    }

    def salvar():
        (pasta / "metadados.json").write_text(
            json.dumps(meta, indent=2, ensure_ascii=False, allow_nan=False) + "\n",
            encoding="utf-8")

    salvar()
    print(f"CAMPANHA: {pasta}", flush=True)
    try:
        coletar(args, pasta, meta)
        meta["estado"] = "coleta_concluida"
        salvar()
        if not args.sem_analise:
            resultado = subprocess.run(
                [sys.executable, str(RAIZ / "scripts/analisar_campanha_docker.py"), str(pasta)],
                cwd=RAIZ, check=False)
            if resultado.returncode:
                raise RuntimeError("Coleta preservada; a analise falhou. Consulte a mensagem anterior.")
            meta["estado"] = "concluida"
        meta["fim"] = agora().isoformat()
        salvar()
        arquivo = shutil.make_archive(str(pasta) + "_para_enviar", "zip",
                                      root_dir=pasta.parent, base_dir=pasta.name)
        print(f"\nCOLETA CONCLUIDA: {pasta}\nARQUIVO PARA ENVIAR: {arquivo}", flush=True)
        return 0
    except (Exception, KeyboardInterrupt) as erro:
        meta["estado"] = "interrompida" if isinstance(erro, KeyboardInterrupt) else "falhou"
        meta["erro"] = str(erro)
        meta["fim"] = agora().isoformat()
        salvar()
        print(f"\nERRO: {erro}\nDados parciais preservados em: {pasta}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
