# 🎲 Loto CLI Plus

Ferramenta em **Python** para **gerar combinações de apostas** em loterias brasileiras (Mega-Sena, Lotofácil, Quina) com foco em **diversificação** e **cobertura combinatória**.

⚠️ **Aviso importante**:  
Este projeto **não prevê resultados de loteria**. Loterias oficiais são projetadas para serem aleatórias e justas. O objetivo aqui é **organizar melhor seus jogos** dentro de um orçamento, cobrindo mais combinações possíveis, equilibrando pares/ímpares e evitando padrões populares que aumentam a chance de dividir prêmios.  

---

## 📌 Objetivos
- **Explorar estatística e combinatória** aplicadas a loterias.  
- Gerar jogos que:
  - Cubram mais subconjuntos (*fechamento combinatório*).  
  - Sejam **equilibrados** em pares/ímpares e distribuídos em diferentes faixas de números.  
  - Evitem padrões populares (datas, sequências longas, somas médias).  
  - Tenham **baixa sobreposição** entre si (mais diversidade).  
- Permitir o uso opcional de um **histórico de sorteios** em CSV para análise.  

---

## 📂 Estrutura do projeto

```
loto-cli-plus/
├─ pyproject.toml        # Configuração do pacote (instalação via pip)
├─ README.md             # Este arquivo
├─ Makefile              # Comandos de atalho
└─ loto_cli_plus/        # Código-fonte principal
 ├─ init.py
 ├─ cli.py             # CLI (argparse + execução principal)
 ├─ history.py         # Leitura/análise de histórico de sorteios
 ├─ specs.py           # Presets por loteria (Mega, Lotofácil, Quina)
 ├─ rules.py           # Regras de par/ímpar, bins, modularidade
 ├─ pool.py            # Construção de pools estratificados
 ├─ metrics.py         # Métricas: cobertura, sobreposição, popularidade
 ├─ grasp.py           # Heurística GRASP + busca local
 └─ export.py          # Exportação para CSV
```

---

## 🚀 Instalação

Clone ou copie o repositório e instale em modo **editável**:

```bash
pip install -e .
```
Isso disponibiliza o comando loto-cli no seu sistema.

⸻

### 📂 Formato do histórico

Você pode fornecer um CSV com resultados passados, em dois formatos:

#### Formato 1 – colunas separadas

```
n1,n2,n3,n4,n5,n6
1,12,23,34,45,60
3,4,7,19,28,59
```

#### Formato 2 – coluna única

```
numbers
01 12 23 34 45 60
03,04,07,19,28,59
```

Para a Lotofácil, use 15 números por linha.
Para a Quina, use 5 números por linha.

⸻

🖥️ Uso da CLI

### Sintaxe

```sh
loto-cli gerar <qtd_jogos> <qtd_numeros> <loteria> [opções]
```

    - <qtd_jogos> → quantos jogos você quer gerar.
    - <qtd_numeros> → quantidade de dezenas por jogo (ex.: 6 na Mega, 15–20 na Lotofácil).
    - <loteria> → megasena | lotofacil | quina.


### Opções principais

	•	--historico arquivo.csv → usa histórico de sorteios (opcional).
	•	--reweight-bias → aplica leve peso se o histórico mostrar viés.
	•	--pool-size N → tamanho do pool (padrão definido por loteria).
	•	--bins N / --min-bins-hit N → espalhamento por faixas.
	•	--min-even N / --max-even N → mínimo/máximo de pares por jogo.
	•	--t-cover N → tamanho do subconjunto a ser coberto (fechamento).
	•	--lam-overlap X → peso contra sobreposição (default 0.6).
	•	--lam-pop X → peso contra popularidade (default 0.8).
	•	--out arquivo.csv → salva em CSV.
	•	--stdout → imprime no terminal.

⸻

### 📊 Exemplos de uso

#### 🔹 Lotofácil — 10 jogos de 16 dezenas com histórico:

```sh
loto-cli gerar 10 16 lotofacil --historico lotofacil_historico.csv --out lf_10x16.csv --stdout
```

#### 🔹 Mega-Sena — 8 jogos de 6 dezenas (sem histórico):

```sh
loto-cli gerar 8 6 megasena --stdout
```

#### 🔹 Quina — 20 jogos de 7 dezenas com ajustes:
```sh
loto-cli gerar 20 7 quina --lam-overlap 0.8 --lam-pop 0.6 --sample-candidates 800 --stdout
```


⸻

### 🛠️ Uso com Makefile

#### Para facilitar, use:

```sh
make lotofacil
make megasena
make quina
```

#### Ou rode com parâmetros customizados:

```sh
make run ARGS="gerar 12 15 lotofacil --stdout"
```


⸻

### ⚙️ Como funciona (em alto nível)
	1.	Pool inicial: números distribuídos por faixas (bins), opcionalmente ponderados por viés histórico.
	2.	Regras: bilhetes devem respeitar par/ímpar, espalhamento mínimo, diversidade modular.
	3.	Objetivo: maximizar cobertura de subconjuntos (t-cover) e minimizar sobreposição/popularidade.
	4.	Heurística GRASP: construção gulosidade+aleatoriedade → busca local com trocas.

⸻

### ⚠️ Aviso legal
	•	Loterias oficiais são jogos de azar.
	•	Este código é educacional: não garante ganhos.
	•	Use com responsabilidade.
