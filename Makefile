PYTHON ?= python3

install:
	$(PYTHON) -m pip install -e .

run:
	$(PYTHON) -m loto_cli_plus.cli $(ARGS)

lotofacil:
	$(PYTHON) -m loto_cli_plus.cli gerar 9 15 lotofacil \
		--historico history/lotofacil.csv \
		--stdout --out lotofacil_jogos.csv

megasena:
	$(PYTHON) -m loto_cli_plus.cli gerar 5 7 megasena \
		--historico history/megasena.csv \
		--stdout --out megasena_jogos.csv

quina:
	$(PYTHON) -m loto_cli_plus.cli gerar 5 7 quina \
		--stdout --out quina_jogos.csv

clean:
	rm -f *.csv
