Controlo de Produção 2.0.7.16 (02/06/2026)
===========================================

Features
--------
- Adiciona adaptações para processar logs da bancada BTF06.


Controlo de Produção 2.0.7.15 (20/05/2026)
===========================================

Features
--------
- Adiciona adaptações para ALTRA air lateral UAR260441.


Controlo de Produção 2.0.7.14 (14/05/2026)
===========================================

Changes
--------
- Altera suporte para logs BTF14. Permite validação e registo de TPLACA e FWVERSION.


Controlo de Produção 2.0.7.13 (23/04/2026)
===========================================

Features
--------
- Cria adaptações para permitir dois postos ou mais numa máquina, criando o parâmetro "allowed_workstations" que 
pode conter vários postos (separados por vírgulas). Quando esta variável está preenchida, ao fazer-se login, aparece um 
Dialog para o utilizador selecionar o posto que quer.


Controlo de Produção 2.0.7.12 (31/03/2026)
===========================================

Features
--------
- Adiciona suporte para logs AUTOMATIC_LABEL_CHECK_01.


Controlo de Produção 2.0.7.11 (10/02/2026)
===========================================

Features
--------
- Adiciona suporte para logs STARKTEST PC2 LOGS INVERTER.


Controlo de Produção 2.0.7.10 (05/01/2026)
===========================================

Changes
--------
- Na MIL07, permite que o utilizador processe uma ordem de fabrico do ano passado, desde que o mês corrente seja janeiro
ou fevereiro e a ordem de fabrico seja maior que 50.


Controlo de Produção 2.0.7.9 (18/11/2025)
===========================================

Changes
--------
- Separa parsers de mil07 e bt81.
- Adapta parser de mil07 para recolher "evaluated_at" de "date" em vez de "endtime" que agora vai estar vazio.
- Separa testes de mil07 e bt81, e adapta testes de mil07.


Controlo de Produção 2.0.7.8 (06/11/2025)
===========================================

Changes
--------
- Corrige formato de timestamp ao atualizar dados do utilizador em "__sync_user_handler" para versões antigas de python
que não permitim o valor 'Z'.


Controlo de Produção 2.0.7.7 (03/11/2025)
===========================================

Features
--------
- Adiciona suporte para logs LVS da ZIV.


Controlo de Produção 2.0.7.6 (29/10/2025)
===========================================

Features
--------
- Adiciona suporte para logs da DBOARD R5 FT30 Tester.


Controlo de Produção 2.0.7.5 (02/10/2025)
===========================================

Features
--------
- Cria SelectOrderDialog para selecionar ordem de fabrico.
- Cria nova constant para url de registo de logs mil07.
- Adiciona adaptações para selecionar ordem de fabrico quando é MIL07.

Changes
--------
- Elimina logica anterior de registo de logs MIL07.


Controlo de Produção 2.0.7.4 (01/10/2025)
===========================================

Changes
--------
- Adiciona digitos estáticos '020215102523' a serial_no_2 da gbt (BT81);
- Atualiza testes para refletir alteração realizada no ponto anterior.


Controlo de Produção 2.0.7.3 (30/09/2025)
===========================================

Changes
--------
- Logs da BT81 - Torna o serial_no_2 facultativo quando a unidade está NOK. Deixa obrigatório quando a unidade está OK.


Controlo de Produção 2.0.7.2 (26/09/2025)
===========================================

Changes
--------
- Atualiza parser parse_mil07_and_bt81 para recolher e enviar o serial_no_2 para os logs da BT81.
- Adiciona testes a TestParseMil07AndBT81 para logs da BT81 e recursos para esses mesmos testes.


Controlo de Produção 2.0.7.1 (24/09/2025)
===========================================

Features
--------
- Adiciona suporte para logs da BT81.


Controlo de Produção 2.0.7 (23/09/2025)
===========================================

Features
--------
- Adiciona suporte para logs da MIL07.


Controlo de Produção 2.0.6.1 (17/09/2025)
===========================================

Features
--------
- Adiciona validação para lote quando tool é ZURC. Procura pelo serial_number e pelo lote em conjunto (ambos podem 
repetir, mas não em conjunto).
- Atualiza o parser "parse_zurc" para devolver também o número do lote.


Controlo de Produção 2.0.6 (16/09/2025)
===========================================

Features
--------
- Adiciona suporte para logs da BTF14.


Controlo de Produção 2.0.5 (09/09/2025)
===========================================

Features
--------
- Adiciona suporte para logs da BTF 1177.


Controlo de Produção 2.0.4.1 (05/09/2025)
===========================================

Features
--------
- Implementa .dockerignore para compilar projeto para raspberry pi.


Controlo de Produção 2.0.4 (04/09/2025)
===========================================

Features
--------
- Adiciona suporte para logs da linha ZURC.

Bugfixes
--------
- Ajustada a construção de caminhos (paths) garantindo compatibilidade entre diferentes sistemas operativos.


ontrolo de Produção 2.0.3.3 (28/08/2025)
===========================================

Features
--------
- Adiciona feature que permite compilar o programa em Windows para executar em linux/Raspberry Pi.


Controlo de Produção 2.0.3.2 (28/07/2025)
===========================================

Bugfixes
--------
- Corrige erro de parsing do timestamp para máquinas m34 e m42, para a tool EOL ZIV.


Controlo de Produção 2.0.3.1 (28/07/2025)
===========================================

Bugfixes
--------
- Corrige erro de configurações do parser.


Controlo de Produção 2.0.3 (25/07/2025)
===========================================

Features
--------
- Adiciona suporte para logs do equipamento 'fcl0022' da linha ZIV.


Controlo de Produção 2.0.2 (22/07/2025)
===========================================

Features
--------
- Adiciona suporte para logs de equipamentos do Uartracker (ZIV).


Controlo de Produção 2.0.1 (18/06/2025)
===========================================

Changes
--------
- Atualiza formato de ficheiro log das bancadas de teste Stark.
