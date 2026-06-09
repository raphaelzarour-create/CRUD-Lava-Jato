# Requisitos do Sistema

## Requisitos funcionais

1. O sistema deve permitir login de usuario cadastrado.
2. O sistema deve manter clientes com cadastro, listagem, pesquisa, edicao, exclusao e visualizacao por tabela.
3. O sistema deve manter carros vinculados a clientes, com placa obrigatoria.
4. O sistema deve manter servicos com nome, descricao, preco, tempo estimado e status ativo/inativo.
5. O sistema deve criar ordens de servico com cliente, carro, status, forma de pagamento, observacoes e um ou mais servicos.
6. O sistema deve calcular automaticamente subtotal e total de ordens.
7. O sistema deve pesquisar ordens por cliente, placa, status e periodo.
8. O dashboard deve exibir total de clientes, total de carros, ordens abertas, ordens concluidas e faturamento.
9. O banco deve iniciar com usuario administrador e dados de exemplo.

## Requisitos nao funcionais

1. A aplicacao deve ser desktop e executar localmente.
2. A interface deve usar Qt Widgets/PySide6 e arquivos `.ui` editaveis no Qt Designer.
3. A persistencia deve usar SQLite por meio do modulo `sqlite3`.
4. As queries devem usar parametros para reduzir risco de SQL injection.
5. O codigo deve ser separado em camadas de banco, controllers, models e interface.
6. Erros devem ser tratados com mensagens amigaveis ao usuario.
7. O projeto deve instalar dependencias por `requirements.txt`.

## Validacoes obrigatorias

- Cliente sem nome nao pode ser salvo.
- Carro sem cliente ou placa nao pode ser salvo.
- Servico sem nome ou preco valido nao pode ser salvo.
- Ordem sem cliente, carro ou pelo menos um servico nao pode ser salva.

