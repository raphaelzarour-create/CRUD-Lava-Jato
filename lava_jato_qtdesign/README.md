# CRUD Lava Jato - Python + PySide6 + SQLite

Sistema desktop para gerenciamento de lava jato, feito com Python 3, Qt Widgets/PySide6, interfaces `.ui` editaveis no Qt Designer e banco SQLite local.

## Como executar

No terminal:

```bash
cd lava_jato_qtdesign
pip install -r requirements.txt
python main.py
```

Login padrao:

- Usuario: `admin`
- Senha: `admin123`

O arquivo `database/lava_jato.db` ja acompanha dados iniciais. Para recriar o banco:

```bash
python scripts/seed.py
```

## Funcionalidades

- Login com senha armazenada por hash PBKDF2.
- Dashboard com indicadores de clientes, carros, ordens abertas, ordens concluidas e faturamento.
- CRUD completo de clientes, carros, servicos e ordens de servico.
- Ordem de servico com multiplos itens, quantidade e calculo automatico do total.
- Pesquisa de ordens por cliente, placa, status e periodo.
- Mensagens amigaveis com `QMessageBox`.
- Queries parametrizadas e camada de banco separada dos controllers.

## Estrutura

```text
lava_jato_qtdesign/
|-- main.py
|-- database/
|   |-- connection.py
|   |-- schema.sql
|   `-- lava_jato.db
|-- controllers/
|-- models/
|-- views/
|-- assets/
|-- docs/
|-- scripts/
|-- tests/
|-- requirements.txt
`-- README.md
```

## Validacao tecnica

```bash
python -m compileall .
python tests/smoke_test.py
```

## Versionar no GitHub

```bash
git init
git add .
git commit -m "Projeto CRUD Lava Jato"
git branch -M main
git remote add origin https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git
git push -u origin main
```

