# Manual do Usuario

## 1. Acesso

Execute `python main.py` dentro da pasta `lava_jato_qtdesign`.

Use:

- Usuario: `admin`
- Senha: `admin123`

## 2. Dashboard

A primeira tela apos o login mostra os indicadores principais do lava jato:

- total de clientes;
- total de carros;
- ordens abertas;
- ordens concluidas;
- faturamento de ordens concluidas.

## 3. Clientes

Abra o menu `Clientes`.

Para cadastrar:

1. Preencha pelo menos o nome.
2. Informe CPF/CNPJ, telefone, email, endereco e observacoes quando necessario.
3. Clique em `Salvar`.

Para editar, clique em uma linha da tabela, altere os campos e clique em `Salvar`.

Para excluir, selecione uma linha e clique em `Excluir`. Clientes vinculados a carros ou ordens nao podem ser excluidos.

## 4. Carros

Abra o menu `Carros`.

1. Selecione o cliente dono do veiculo.
2. Informe placa, marca, modelo, ano, cor, tipo e observacoes.
3. Clique em `Salvar`.

A placa e obrigatoria e nao pode repetir.

## 5. Servicos

Abra o menu `Servicos`.

1. Informe nome, preco e tempo estimado.
2. Marque se o servico esta ativo.
3. Clique em `Salvar`.

Servicos usados em ordens nao podem ser excluidos.

## 6. Ordem de Servico

Abra o menu `Ordem de Servico`.

1. Selecione cliente e carro.
2. Escolha um servico e quantidade.
3. Clique em `Adicionar`.
4. Repita para incluir outros servicos.
5. Selecione status e forma de pagamento.
6. Clique em `Salvar Ordem`.

O total e recalculado automaticamente sempre que itens sao adicionados ou removidos.

## 7. Pesquisa de Ordens

Abra o menu `Pesquisar Ordens`.

Use os filtros:

- cliente;
- placa;
- status;
- periodo.

Clique em uma ordem na tabela para ver os detalhes completos no painel lateral.

