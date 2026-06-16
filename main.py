from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import QFile, Qt, QDate
from PySide6.QtGui import QIcon
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import (
    QApplication,
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDialog,
    QDoubleSpinBox,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QWidget,
)

from controllers.auth_controller import AuthController
from controllers.carro_controller import CarroController
from controllers.cliente_controller import ClienteController
from controllers.ordem_controller import OrdemController
from controllers.servico_controller import ServicoController
from database.connection import initialize_database


BASE_DIR = Path(__file__).resolve().parent
VIEW_DIR = BASE_DIR / "views"
ASSET_DIR = BASE_DIR / "assets"
ICON_DIR = ASSET_DIR / "icons"


def money(value: float | int | None) -> str:
    value = float(value or 0)
    formatted = f"R$ {value:,.2f}"
    return formatted.replace(",", "X").replace(".", ",").replace("X", ".")


def date_text(value: object | None) -> str:
    if not value:
        return ""
    if hasattr(value, "strftime"):
        return value.strftime("%Y-%m-%d")
    return str(value)[:10]


def load_ui(file_name: str):
    path = VIEW_DIR / file_name
    if not path.exists():
        raise FileNotFoundError(f"Tela nao encontrada: {path}")

    ui_file = QFile(str(path))
    if not ui_file.open(QFile.ReadOnly):
        raise RuntimeError(f"Nao foi possivel abrir a tela: {path}")

    loader = QUiLoader()
    widget = loader.load(ui_file)
    ui_file.close()
    if widget is None:
        raise RuntimeError(f"Nao foi possivel carregar a tela: {path}")
    return widget


def apply_styles(app: QApplication) -> None:
    style_path = ASSET_DIR / "styles.qss"
    if style_path.exists():
        app.setStyleSheet(style_path.read_text(encoding="utf-8"))


def find(parent, name: str, widget_type=None):
    widget = parent.findChild(widget_type or QWidget, name)
    if widget is None:
        raise RuntimeError(f"Widget nao encontrado: {name}")
    return widget


def show_error(parent, message: str) -> None:
    QMessageBox.critical(parent, "Erro", message)


def show_info(parent, message: str) -> None:
    QMessageBox.information(parent, "Sucesso", message)


def confirm(parent, message: str) -> bool:
    result = QMessageBox.question(
        parent,
        "Confirmar",
        message,
        QMessageBox.Yes | QMessageBox.No,
        QMessageBox.No,
    )
    return result == QMessageBox.Yes


def setup_table(table: QTableWidget, headers: list[str]) -> None:
    table.setColumnCount(len(headers))
    table.setHorizontalHeaderLabels(headers)
    table.setSelectionBehavior(QAbstractItemView.SelectRows)
    table.setSelectionMode(QAbstractItemView.SingleSelection)
    table.setEditTriggers(QAbstractItemView.NoEditTriggers)
    table.verticalHeader().setVisible(False)
    table.horizontalHeader().setStretchLastSection(True)


def fill_table(table: QTableWidget, headers: list[str], rows: list[dict], keys: list[str]) -> None:
    setup_table(table, headers)
    table.setRowCount(0)
    for row_data in rows:
        row_index = table.rowCount()
        table.insertRow(row_index)
        for col_index, key in enumerate(keys):
            value = row_data.get(key, "")
            item = QTableWidgetItem("" if value is None else str(value))
            if col_index == 0:
                item.setData(Qt.UserRole, row_data.get("id"))
            table.setItem(row_index, col_index, item)
    table.resizeColumnsToContents()


def selected_id_from_table(table: QTableWidget) -> int | None:
    selected = table.selectionModel().selectedRows()
    if not selected:
        return None
    first_item = table.item(selected[0].row(), 0)
    if first_item is None:
        return None
    value = first_item.data(Qt.UserRole)
    return int(value) if value is not None else None


def set_combo_data(combo: QComboBox, value: int | str | None) -> None:
    for index in range(combo.count()):
        if combo.itemData(index) == value:
            combo.setCurrentIndex(index)
            return
    combo.setCurrentIndex(0 if combo.count() else -1)


class LoginWindow:
    def __init__(self) -> None:
        self.auth_controller = AuthController()
        self.window: QDialog = load_ui("login.ui")
        self.window.setWindowIcon(QIcon(str(ICON_DIR / "car-wash.svg")))
        self.main_window: MainWindow | None = None

        self.txt_usuario = find(self.window, "txtUsuario", QLineEdit)
        self.txt_senha = find(self.window, "txtSenha", QLineEdit)
        self.lbl_error = find(self.window, "lblErroLogin", QLabel)
        self.btn_login = find(self.window, "btnLogin", QPushButton)

        self.btn_login.clicked.connect(self.login)
        self.txt_senha.returnPressed.connect(self.login)
        self.lbl_error.setText("")

    def show(self) -> None:
        self.window.show()

    def login(self) -> None:
        user = self.auth_controller.authenticate(self.txt_usuario.text(), self.txt_senha.text())
        if not user:
            self.lbl_error.setText("Usuario ou senha invalidos.")
            return

        self.main_window = MainWindow(user)
        self.main_window.show()
        self.window.close()


class MainWindow:
    def __init__(self, user: dict) -> None:
        self.user = user
        self.window = load_ui("dashboard.ui")
        self.window.setWindowIcon(QIcon(str(ICON_DIR / "car-wash.svg")))

        self.cliente_controller = ClienteController()
        self.carro_controller = CarroController()
        self.servico_controller = ServicoController()
        self.ordem_controller = OrdemController()

        self.selected_cliente_id: int | None = None
        self.selected_carro_id: int | None = None
        self.selected_servico_id: int | None = None
        self.selected_ordem_id: int | None = None
        self.ordem_itens: list[dict] = []

        self.stack = find(self.window, "contentArea", QStackedWidget)
        self.dashboard_page = find(self.window, "dashboardHome", QWidget)
        self.pages = {
            "dashboard": self.dashboard_page,
            "clientes": load_ui("cliente.ui"),
            "carros": load_ui("carro.ui"),
            "servicos": load_ui("servico.ui"),
            "ordens": load_ui("ordem_servico.ui"),
            "listar_ordens": load_ui("listar_ordens.ui"),
        }
        for key, page in self.pages.items():
            if key != "dashboard":
                self.stack.addWidget(page)

        self._setup_sidebar()
        self._setup_dashboard()
        self._setup_clientes()
        self._setup_carros()
        self._setup_servicos()
        self._setup_ordens()
        self._setup_listagem_ordens()
        self.show_page("dashboard")

    def show(self) -> None:
        self.window.showMaximized()

    def page(self, name: str):
        return self.pages[name]

    def _setup_sidebar(self) -> None:
        button_icons = {
            "btnDashboard": "dashboard.svg",
            "btnClientes": "user.svg",
            "btnCarros": "car.svg",
            "btnServicos": "tool.svg",
            "btnOrdens": "clipboard.svg",
            "btnListarOrdens": "search.svg",
            "btnSair": "logout.svg",
        }
        for object_name, icon_name in button_icons.items():
            button = find(self.window, object_name, QPushButton)
            button.setIcon(QIcon(str(ICON_DIR / icon_name)))

        find(self.window, "btnDashboard", QPushButton).clicked.connect(lambda: self.show_page("dashboard"))
        find(self.window, "btnClientes", QPushButton).clicked.connect(lambda: self.show_page("clientes"))
        find(self.window, "btnCarros", QPushButton).clicked.connect(lambda: self.show_page("carros"))
        find(self.window, "btnServicos", QPushButton).clicked.connect(lambda: self.show_page("servicos"))
        find(self.window, "btnOrdens", QPushButton).clicked.connect(lambda: self.show_page("ordens"))
        find(self.window, "btnListarOrdens", QPushButton).clicked.connect(lambda: self.show_page("listar_ordens"))
        find(self.window, "btnSair", QPushButton).clicked.connect(self.window.close)

        find(self.window, "lblUsuarioLogado", QLabel).setText(
            f"{self.user.get('nome', 'Usuario')} - {self.user.get('perfil', '')}"
        )

    def show_page(self, name: str) -> None:
        page = self.page(name)
        self.stack.setCurrentWidget(page)
        if name == "dashboard":
            self.refresh_dashboard()
        elif name == "clientes":
            self.refresh_clientes()
        elif name == "carros":
            self.refresh_carros()
        elif name == "servicos":
            self.refresh_servicos()
        elif name == "ordens":
            self.refresh_order_form()
        elif name == "listar_ordens":
            self.refresh_listagem_ordens()

    def _setup_dashboard(self) -> None:
        self.dashboard_labels = {
            "total_clientes": find(self.window, "lblTotalClientes", QLabel),
            "total_carros": find(self.window, "lblTotalCarros", QLabel),
            "ordens_abertas": find(self.window, "lblOrdensAbertas", QLabel),
            "ordens_concluidas": find(self.window, "lblOrdensConcluidas", QLabel),
            "faturamento_total": find(self.window, "lblFaturamentoTotal", QLabel),
        }

    def refresh_dashboard(self) -> None:
        metrics = self.ordem_controller.dashboard_metrics()
        self.dashboard_labels["total_clientes"].setText(str(metrics["total_clientes"]))
        self.dashboard_labels["total_carros"].setText(str(metrics["total_carros"]))
        self.dashboard_labels["ordens_abertas"].setText(str(metrics["ordens_abertas"]))
        self.dashboard_labels["ordens_concluidas"].setText(str(metrics["ordens_concluidas"]))
        self.dashboard_labels["faturamento_total"].setText(money(metrics["faturamento_total"]))

    def _setup_clientes(self) -> None:
        page = self.page("clientes")
        self.txt_busca_cliente = find(page, "txtBuscaCliente", QLineEdit)
        self.txt_cliente_nome = find(page, "txtClienteNome", QLineEdit)
        self.txt_cliente_cpf = find(page, "txtClienteCpf", QLineEdit)
        self.txt_cliente_telefone = find(page, "txtClienteTelefone", QLineEdit)
        self.txt_cliente_email = find(page, "txtClienteEmail", QLineEdit)
        self.txt_cliente_endereco = find(page, "txtClienteEndereco", QTextEdit)
        self.txt_cliente_observacoes = find(page, "txtClienteObservacoes", QTextEdit)
        self.table_clientes = find(page, "tableClientes", QTableWidget)

        find(page, "btnBuscarCliente", QPushButton).clicked.connect(self.refresh_clientes)
        find(page, "btnNovoCliente", QPushButton).clicked.connect(self.clear_cliente_form)
        find(page, "btnSalvarCliente", QPushButton).clicked.connect(self.save_cliente)
        find(page, "btnExcluirCliente", QPushButton).clicked.connect(self.delete_cliente)
        self.txt_busca_cliente.returnPressed.connect(self.refresh_clientes)
        self.table_clientes.cellClicked.connect(lambda *_: self.load_selected_cliente())

    def clear_cliente_form(self) -> None:
        self.selected_cliente_id = None
        self.txt_cliente_nome.clear()
        self.txt_cliente_cpf.clear()
        self.txt_cliente_telefone.clear()
        self.txt_cliente_email.clear()
        self.txt_cliente_endereco.clear()
        self.txt_cliente_observacoes.clear()
        self.table_clientes.clearSelection()

    def cliente_form_data(self) -> dict:
        return {
            "nome": self.txt_cliente_nome.text(),
            "cpf_cnpj": self.txt_cliente_cpf.text(),
            "telefone": self.txt_cliente_telefone.text(),
            "email": self.txt_cliente_email.text(),
            "endereco": self.txt_cliente_endereco.toPlainText(),
            "observacoes": self.txt_cliente_observacoes.toPlainText(),
        }

    def refresh_clientes(self) -> None:
        rows = self.cliente_controller.list(self.txt_busca_cliente.text())
        fill_table(
            self.table_clientes,
            ["ID", "Nome", "CPF/CNPJ", "Telefone", "Email"],
            rows,
            ["id", "nome", "cpf_cnpj", "telefone", "email"],
        )

    def load_selected_cliente(self) -> None:
        cliente_id = selected_id_from_table(self.table_clientes)
        if cliente_id is None:
            return
        data = self.cliente_controller.get(cliente_id)
        if not data:
            return
        self.selected_cliente_id = cliente_id
        self.txt_cliente_nome.setText(data.get("nome", ""))
        self.txt_cliente_cpf.setText(data.get("cpf_cnpj", ""))
        self.txt_cliente_telefone.setText(data.get("telefone", ""))
        self.txt_cliente_email.setText(data.get("email", ""))
        self.txt_cliente_endereco.setPlainText(data.get("endereco", ""))
        self.txt_cliente_observacoes.setPlainText(data.get("observacoes", ""))

    def save_cliente(self) -> None:
        try:
            if self.selected_cliente_id:
                self.cliente_controller.update(self.selected_cliente_id, self.cliente_form_data())
                show_info(self.window, "Cliente atualizado com sucesso.")
            else:
                self.cliente_controller.create(self.cliente_form_data())
                show_info(self.window, "Cliente cadastrado com sucesso.")
            self.clear_cliente_form()
            self.refresh_clientes()
        except (ValueError, RuntimeError) as exc:
            show_error(self.window, str(exc))

    def delete_cliente(self) -> None:
        cliente_id = self.selected_cliente_id or selected_id_from_table(self.table_clientes)
        if cliente_id is None:
            show_error(self.window, "Selecione um cliente para excluir.")
            return
        if not confirm(self.window, "Deseja excluir o cliente selecionado?"):
            return
        try:
            self.cliente_controller.delete(cliente_id)
            self.clear_cliente_form()
            self.refresh_clientes()
            show_info(self.window, "Cliente excluido com sucesso.")
        except (ValueError, RuntimeError) as exc:
            show_error(self.window, str(exc))

    def _setup_carros(self) -> None:
        page = self.page("carros")
        self.txt_busca_carro = find(page, "txtBuscaCarro", QLineEdit)
        self.combo_carro_cliente = find(page, "comboCarroCliente", QComboBox)
        self.txt_carro_marca = find(page, "txtCarroMarca", QLineEdit)
        self.txt_carro_modelo = find(page, "txtCarroModelo", QLineEdit)
        self.spin_carro_ano = find(page, "spinCarroAno", QSpinBox)
        self.txt_carro_placa = find(page, "txtCarroPlaca", QLineEdit)
        self.txt_carro_cor = find(page, "txtCarroCor", QLineEdit)
        self.combo_carro_tipo = find(page, "comboCarroTipo", QComboBox)
        self.txt_carro_observacoes = find(page, "txtCarroObservacoes", QTextEdit)
        self.table_carros = find(page, "tableCarros", QTableWidget)

        find(page, "btnBuscarCarro", QPushButton).clicked.connect(self.refresh_carros)
        find(page, "btnNovoCarro", QPushButton).clicked.connect(self.clear_carro_form)
        find(page, "btnSalvarCarro", QPushButton).clicked.connect(self.save_carro)
        find(page, "btnExcluirCarro", QPushButton).clicked.connect(self.delete_carro)
        self.txt_busca_carro.returnPressed.connect(self.refresh_carros)
        self.table_carros.cellClicked.connect(lambda *_: self.load_selected_carro())

    def refresh_cliente_combo(self, combo: QComboBox, selected_id: int | None = None) -> None:
        combo.blockSignals(True)
        combo.clear()
        combo.addItem("Selecione...", 0)
        for cliente in self.cliente_controller.list():
            combo.addItem(cliente["nome"], cliente["id"])
        set_combo_data(combo, selected_id or 0)
        combo.blockSignals(False)

    def refresh_carro_combo(self, combo: QComboBox, cliente_id: int | None, selected_id: int | None = None) -> None:
        combo.blockSignals(True)
        combo.clear()
        combo.addItem("Selecione...", 0)
        if cliente_id:
            for carro in self.carro_controller.list_by_cliente(cliente_id):
                label = f"{carro.get('placa', '')} - {carro.get('marca', '')} {carro.get('modelo', '')}".strip()
                combo.addItem(label, carro["id"])
        set_combo_data(combo, selected_id or 0)
        combo.blockSignals(False)

    def refresh_servico_combo(self, combo: QComboBox, selected_id: int | None = None) -> None:
        combo.blockSignals(True)
        combo.clear()
        combo.addItem("Selecione...", 0)
        for servico in self.servico_controller.list(only_active=True):
            combo.addItem(f"{servico['nome']} - {money(servico['preco'])}", servico["id"])
        set_combo_data(combo, selected_id or 0)
        combo.blockSignals(False)

    def clear_carro_form(self) -> None:
        self.selected_carro_id = None
        self.refresh_cliente_combo(self.combo_carro_cliente)
        self.txt_carro_marca.clear()
        self.txt_carro_modelo.clear()
        self.spin_carro_ano.setValue(2026)
        self.txt_carro_placa.clear()
        self.txt_carro_cor.clear()
        self.combo_carro_tipo.setCurrentIndex(0)
        self.txt_carro_observacoes.clear()
        self.table_carros.clearSelection()

    def carro_form_data(self) -> dict:
        return {
            "cliente_id": self.combo_carro_cliente.currentData(),
            "marca": self.txt_carro_marca.text(),
            "modelo": self.txt_carro_modelo.text(),
            "ano": self.spin_carro_ano.value(),
            "placa": self.txt_carro_placa.text(),
            "cor": self.txt_carro_cor.text(),
            "tipo": self.combo_carro_tipo.currentText(),
            "observacoes": self.txt_carro_observacoes.toPlainText(),
        }

    def refresh_carros(self) -> None:
        self.refresh_cliente_combo(self.combo_carro_cliente, self.combo_carro_cliente.currentData())
        rows = self.carro_controller.list(self.txt_busca_carro.text())
        fill_table(
            self.table_carros,
            ["ID", "Cliente", "Placa", "Marca", "Modelo", "Ano", "Tipo"],
            rows,
            ["id", "cliente_nome", "placa", "marca", "modelo", "ano", "tipo"],
        )

    def load_selected_carro(self) -> None:
        carro_id = selected_id_from_table(self.table_carros)
        if carro_id is None:
            return
        data = self.carro_controller.get(carro_id)
        if not data:
            return
        self.selected_carro_id = carro_id
        self.refresh_cliente_combo(self.combo_carro_cliente, data.get("cliente_id"))
        self.txt_carro_marca.setText(data.get("marca", ""))
        self.txt_carro_modelo.setText(data.get("modelo", ""))
        self.spin_carro_ano.setValue(int(data.get("ano") or 2026))
        self.txt_carro_placa.setText(data.get("placa", ""))
        self.txt_carro_cor.setText(data.get("cor", ""))
        self.combo_carro_tipo.setCurrentText(data.get("tipo", "Carro"))
        self.txt_carro_observacoes.setPlainText(data.get("observacoes", ""))

    def save_carro(self) -> None:
        try:
            if self.selected_carro_id:
                self.carro_controller.update(self.selected_carro_id, self.carro_form_data())
                show_info(self.window, "Veiculo atualizado com sucesso.")
            else:
                self.carro_controller.create(self.carro_form_data())
                show_info(self.window, "Veiculo cadastrado com sucesso.")
            self.clear_carro_form()
            self.refresh_carros()
        except (ValueError, RuntimeError) as exc:
            show_error(self.window, str(exc))

    def delete_carro(self) -> None:
        carro_id = self.selected_carro_id or selected_id_from_table(self.table_carros)
        if carro_id is None:
            show_error(self.window, "Selecione um veiculo para excluir.")
            return
        if not confirm(self.window, "Deseja excluir o veiculo selecionado?"):
            return
        try:
            self.carro_controller.delete(carro_id)
            self.clear_carro_form()
            self.refresh_carros()
            show_info(self.window, "Veiculo excluido com sucesso.")
        except (ValueError, RuntimeError) as exc:
            show_error(self.window, str(exc))

    def _setup_servicos(self) -> None:
        page = self.page("servicos")
        self.txt_busca_servico = find(page, "txtBuscaServico", QLineEdit)
        self.txt_servico_nome = find(page, "txtServicoNome", QLineEdit)
        self.txt_servico_descricao = find(page, "txtServicoDescricao", QTextEdit)
        self.spin_servico_preco = find(page, "spinServicoPreco", QDoubleSpinBox)
        self.spin_servico_tempo = find(page, "spinServicoTempo", QSpinBox)
        self.chk_servico_ativo = find(page, "chkServicoAtivo", QCheckBox)
        self.table_servicos = find(page, "tableServicos", QTableWidget)

        find(page, "btnBuscarServico", QPushButton).clicked.connect(self.refresh_servicos)
        find(page, "btnNovoServico", QPushButton).clicked.connect(self.clear_servico_form)
        find(page, "btnSalvarServico", QPushButton).clicked.connect(self.save_servico)
        find(page, "btnExcluirServico", QPushButton).clicked.connect(self.delete_servico)
        self.txt_busca_servico.returnPressed.connect(self.refresh_servicos)
        self.table_servicos.cellClicked.connect(lambda *_: self.load_selected_servico())

    def clear_servico_form(self) -> None:
        self.selected_servico_id = None
        self.txt_servico_nome.clear()
        self.txt_servico_descricao.clear()
        self.spin_servico_preco.setValue(0)
        self.spin_servico_tempo.setValue(30)
        self.chk_servico_ativo.setChecked(True)
        self.table_servicos.clearSelection()

    def servico_form_data(self) -> dict:
        return {
            "nome": self.txt_servico_nome.text(),
            "descricao": self.txt_servico_descricao.toPlainText(),
            "preco": self.spin_servico_preco.value(),
            "tempo_estimado_minutos": self.spin_servico_tempo.value(),
            "ativo": self.chk_servico_ativo.isChecked(),
        }

    def refresh_servicos(self) -> None:
        rows = self.servico_controller.list(self.txt_busca_servico.text())
        formatted_rows = [
            {
                **row,
                "preco_fmt": money(row.get("preco")),
                "ativo_fmt": "Sim" if row.get("ativo") else "Nao",
            }
            for row in rows
        ]
        fill_table(
            self.table_servicos,
            ["ID", "Nome", "Preco", "Tempo (min)", "Ativo"],
            formatted_rows,
            ["id", "nome", "preco_fmt", "tempo_estimado_minutos", "ativo_fmt"],
        )

    def load_selected_servico(self) -> None:
        servico_id = selected_id_from_table(self.table_servicos)
        if servico_id is None:
            return
        data = self.servico_controller.get(servico_id)
        if not data:
            return
        self.selected_servico_id = servico_id
        self.txt_servico_nome.setText(data.get("nome", ""))
        self.txt_servico_descricao.setPlainText(data.get("descricao", ""))
        self.spin_servico_preco.setValue(float(data.get("preco") or 0))
        self.spin_servico_tempo.setValue(int(data.get("tempo_estimado_minutos") or 0))
        self.chk_servico_ativo.setChecked(bool(data.get("ativo")))

    def save_servico(self) -> None:
        try:
            if self.selected_servico_id:
                self.servico_controller.update(self.selected_servico_id, self.servico_form_data())
                show_info(self.window, "Servico atualizado com sucesso.")
            else:
                self.servico_controller.create(self.servico_form_data())
                show_info(self.window, "Servico cadastrado com sucesso.")
            self.clear_servico_form()
            self.refresh_servicos()
        except (ValueError, RuntimeError) as exc:
            show_error(self.window, str(exc))

    def delete_servico(self) -> None:
        servico_id = self.selected_servico_id or selected_id_from_table(self.table_servicos)
        if servico_id is None:
            show_error(self.window, "Selecione um servico para excluir.")
            return
        if not confirm(self.window, "Deseja excluir o servico selecionado?"):
            return
        try:
            self.servico_controller.delete(servico_id)
            self.clear_servico_form()
            self.refresh_servicos()
            show_info(self.window, "Servico excluido com sucesso.")
        except (ValueError, RuntimeError) as exc:
            show_error(self.window, str(exc))

    def _setup_ordens(self) -> None:
        page = self.page("ordens")
        self.combo_ordem_cliente = find(page, "comboOrdemCliente", QComboBox)
        self.combo_ordem_carro = find(page, "comboOrdemCarro", QComboBox)
        self.combo_ordem_servico = find(page, "comboOrdemServico", QComboBox)
        self.spin_ordem_quantidade = find(page, "spinOrdemQuantidade", QSpinBox)
        self.combo_ordem_status = find(page, "comboOrdemStatus", QComboBox)
        self.combo_ordem_pagamento = find(page, "comboOrdemPagamento", QComboBox)
        self.txt_ordem_observacoes = find(page, "txtOrdemObservacoes", QTextEdit)
        self.lbl_ordem_total = find(page, "lblOrdemTotal", QLabel)
        self.table_ordem_itens = find(page, "tableOrdemItens", QTableWidget)
        self.table_ordens = find(page, "tableOrdens", QTableWidget)

        self.combo_ordem_cliente.currentIndexChanged.connect(self.on_ordem_cliente_changed)
        find(page, "btnAdicionarItem", QPushButton).clicked.connect(self.add_ordem_item)
        find(page, "btnRemoverItem", QPushButton).clicked.connect(self.remove_ordem_item)
        find(page, "btnNovaOrdem", QPushButton).clicked.connect(self.clear_ordem_form)
        find(page, "btnSalvarOrdem", QPushButton).clicked.connect(self.save_ordem)
        find(page, "btnExcluirOrdem", QPushButton).clicked.connect(self.delete_ordem)
        self.table_ordens.cellClicked.connect(lambda *_: self.load_selected_ordem())

    def refresh_order_form(self) -> None:
        selected_cliente = self.combo_ordem_cliente.currentData() if hasattr(self, "combo_ordem_cliente") else None
        self.refresh_cliente_combo(self.combo_ordem_cliente, selected_cliente)
        self.refresh_servico_combo(self.combo_ordem_servico)
        self.on_ordem_cliente_changed()
        self.refresh_ordem_item_table()
        self.refresh_ordens_summary()

    def on_ordem_cliente_changed(self) -> None:
        cliente_id = self.combo_ordem_cliente.currentData()
        self.refresh_carro_combo(self.combo_ordem_carro, cliente_id)

    def clear_ordem_form(self) -> None:
        self.selected_ordem_id = None
        self.ordem_itens = []
        self.refresh_cliente_combo(self.combo_ordem_cliente)
        self.refresh_carro_combo(self.combo_ordem_carro, None)
        self.refresh_servico_combo(self.combo_ordem_servico)
        self.spin_ordem_quantidade.setValue(1)
        self.combo_ordem_status.setCurrentText("Aberta")
        self.combo_ordem_pagamento.setCurrentIndex(0)
        self.txt_ordem_observacoes.clear()
        self.refresh_ordem_item_table()
        self.table_ordens.clearSelection()

    def add_ordem_item(self) -> None:
        servico_id = int(self.combo_ordem_servico.currentData() or 0)
        quantidade = int(self.spin_ordem_quantidade.value())
        if servico_id <= 0:
            show_error(self.window, "Selecione um servico para adicionar.")
            return
        servico = self.servico_controller.get(servico_id)
        if not servico:
            show_error(self.window, "Servico selecionado nao foi encontrado.")
            return

        for item in self.ordem_itens:
            if item["servico_id"] == servico_id:
                item["quantidade"] += quantidade
                item["subtotal"] = round(item["quantidade"] * item["valor_unitario"], 2)
                self.refresh_ordem_item_table()
                return

        self.ordem_itens.append(
            {
                "servico_id": servico_id,
                "servico_nome": servico["nome"],
                "quantidade": quantidade,
                "valor_unitario": float(servico["preco"]),
                "subtotal": round(float(servico["preco"]) * quantidade, 2),
            }
        )
        self.refresh_ordem_item_table()

    def remove_ordem_item(self) -> None:
        selected = self.table_ordem_itens.selectionModel().selectedRows()
        if not selected:
            show_error(self.window, "Selecione um item da ordem para remover.")
            return
        row = selected[0].row()
        if 0 <= row < len(self.ordem_itens):
            self.ordem_itens.pop(row)
            self.refresh_ordem_item_table()

    def refresh_ordem_item_table(self) -> None:
        rows = [
            {
                **item,
                "valor_unitario_fmt": money(item["valor_unitario"]),
                "subtotal_fmt": money(item["subtotal"]),
            }
            for item in self.ordem_itens
        ]
        fill_table(
            self.table_ordem_itens,
            ["Servico", "Qtd", "Unitario", "Subtotal"],
            rows,
            ["servico_nome", "quantidade", "valor_unitario_fmt", "subtotal_fmt"],
        )
        total = sum(item["subtotal"] for item in self.ordem_itens)
        self.lbl_ordem_total.setText(money(total))

    def ordem_form_data(self) -> dict:
        return {
            "cliente_id": self.combo_ordem_cliente.currentData(),
            "carro_id": self.combo_ordem_carro.currentData(),
            "status": self.combo_ordem_status.currentText(),
            "forma_pagamento": self.combo_ordem_pagamento.currentText(),
            "observacoes": self.txt_ordem_observacoes.toPlainText(),
        }

    def refresh_ordens_summary(self) -> None:
        rows = self.ordem_controller.search()
        formatted_rows = [
            {
                **row,
                "data_fmt": date_text(row.get("data_abertura")),
                "valor_fmt": money(row.get("valor_total")),
            }
            for row in rows
        ]
        fill_table(
            self.table_ordens,
            ["ID", "Cliente", "Carro", "Placa", "Data", "Status", "Total"],
            formatted_rows,
            ["id", "cliente_nome", "carro_nome", "placa", "data_fmt", "status", "valor_fmt"],
        )

    def save_ordem(self) -> None:
        try:
            if self.selected_ordem_id:
                self.ordem_controller.update(self.selected_ordem_id, self.ordem_form_data(), self.ordem_itens)
                show_info(self.window, "Ordem atualizada com sucesso.")
            else:
                self.ordem_controller.create(self.ordem_form_data(), self.ordem_itens)
                show_info(self.window, "Ordem cadastrada com sucesso.")
            self.clear_ordem_form()
            self.refresh_ordens_summary()
            self.refresh_dashboard()
        except (ValueError, RuntimeError) as exc:
            show_error(self.window, str(exc))

    def load_selected_ordem(self) -> None:
        ordem_id = selected_id_from_table(self.table_ordens)
        if ordem_id is None:
            return
        data = self.ordem_controller.get_with_items(ordem_id)
        if not data:
            return

        self.selected_ordem_id = ordem_id
        self.refresh_cliente_combo(self.combo_ordem_cliente, data.get("cliente_id"))
        self.refresh_carro_combo(self.combo_ordem_carro, data.get("cliente_id"), data.get("carro_id"))
        self.refresh_servico_combo(self.combo_ordem_servico)
        self.combo_ordem_status.setCurrentText(data.get("status", "Aberta"))
        self.combo_ordem_pagamento.setCurrentText(data.get("forma_pagamento", "Pix") or "Pix")
        self.txt_ordem_observacoes.setPlainText(data.get("observacoes", ""))
        self.ordem_itens = [
            {
                "servico_id": item["servico_id"],
                "servico_nome": item["servico_nome"],
                "quantidade": item["quantidade"],
                "valor_unitario": float(item["valor_unitario"]),
                "subtotal": float(item["subtotal"]),
            }
            for item in data.get("itens", [])
        ]
        self.refresh_ordem_item_table()

    def delete_ordem(self) -> None:
        ordem_id = self.selected_ordem_id or selected_id_from_table(self.table_ordens)
        if ordem_id is None:
            show_error(self.window, "Selecione uma ordem para excluir.")
            return
        if not confirm(self.window, "Deseja excluir a ordem selecionada?"):
            return
        try:
            self.ordem_controller.delete(ordem_id)
            self.clear_ordem_form()
            self.refresh_ordens_summary()
            self.refresh_dashboard()
            show_info(self.window, "Ordem excluida com sucesso.")
        except RuntimeError as exc:
            show_error(self.window, str(exc))

    def _setup_listagem_ordens(self) -> None:
        page = self.page("listar_ordens")
        self.txt_filtro_cliente = find(page, "txtFiltroCliente", QLineEdit)
        self.txt_filtro_placa = find(page, "txtFiltroPlaca", QLineEdit)
        self.combo_filtro_status = find(page, "comboFiltroStatus", QComboBox)
        self.chk_filtro_periodo = find(page, "chkFiltroPeriodo", QCheckBox)
        self.date_filtro_inicio = find(page, "dateFiltroInicio", QDateEdit)
        self.date_filtro_fim = find(page, "dateFiltroFim", QDateEdit)
        self.table_listar_ordens = find(page, "tableListarOrdens", QTableWidget)
        self.txt_detalhes_ordem = find(page, "txtDetalhesOrdem", QTextEdit)

        today = QDate.currentDate()
        self.date_filtro_inicio.setDate(today.addMonths(-1))
        self.date_filtro_fim.setDate(today)

        find(page, "btnPesquisarOrdens", QPushButton).clicked.connect(self.refresh_listagem_ordens)
        find(page, "btnLimparFiltros", QPushButton).clicked.connect(self.clear_ordem_filters)
        self.table_listar_ordens.cellClicked.connect(lambda *_: self.show_order_details())

    def clear_ordem_filters(self) -> None:
        self.txt_filtro_cliente.clear()
        self.txt_filtro_placa.clear()
        self.combo_filtro_status.setCurrentIndex(0)
        self.chk_filtro_periodo.setChecked(False)
        self.txt_detalhes_ordem.clear()
        self.refresh_listagem_ordens()

    def refresh_listagem_ordens(self) -> None:
        filters = {
            "cliente": self.txt_filtro_cliente.text(),
            "placa": self.txt_filtro_placa.text(),
            "status": "" if self.combo_filtro_status.currentIndex() == 0 else self.combo_filtro_status.currentText(),
            "data_inicio": self.date_filtro_inicio.date().toString("yyyy-MM-dd") if self.chk_filtro_periodo.isChecked() else "",
            "data_fim": self.date_filtro_fim.date().toString("yyyy-MM-dd") if self.chk_filtro_periodo.isChecked() else "",
        }
        rows = self.ordem_controller.search(filters)
        formatted_rows = [
            {
                **row,
                "data_fmt": date_text(row.get("data_abertura")),
                "valor_fmt": money(row.get("valor_total")),
            }
            for row in rows
        ]
        fill_table(
            self.table_listar_ordens,
            ["ID", "Cliente", "Carro", "Placa", "Data", "Status", "Total"],
            formatted_rows,
            ["id", "cliente_nome", "carro_nome", "placa", "data_fmt", "status", "valor_fmt"],
        )

    def show_order_details(self) -> None:
        ordem_id = selected_id_from_table(self.table_listar_ordens)
        if ordem_id is None:
            return
        ordem = self.ordem_controller.get_with_items(ordem_id)
        if not ordem:
            return

        lines = [
            f"Ordem #{ordem['id']}",
            f"Cliente: {ordem['cliente_nome']}",
            f"Veiculo: {ordem['carro_nome']} - {ordem['placa']}",
            f"Abertura: {ordem['data_abertura']}",
            f"Finalizacao: {ordem.get('data_finalizacao') or '-'}",
            f"Status: {ordem['status']}",
            f"Pagamento: {ordem.get('forma_pagamento') or '-'}",
            f"Total: {money(ordem['valor_total'])}",
            "",
            "Servicos:",
        ]
        for item in ordem.get("itens", []):
            lines.append(
                f"- {item['servico_nome']} | qtd {item['quantidade']} | "
                f"{money(item['valor_unitario'])} | subtotal {money(item['subtotal'])}"
            )
        if ordem.get("observacoes"):
            lines.extend(["", f"Observacoes: {ordem['observacoes']}"])
        self.txt_detalhes_ordem.setPlainText("\n".join(lines))


def ensure_database_ready() -> None:
    initialize_database()
    AuthController().ensure_default_admin()


def main() -> int:
    app = QApplication(sys.argv)
    apply_styles(app)
    try:
        ensure_database_ready()
    except RuntimeError as exc:
        QMessageBox.critical(None, "Banco de dados indisponivel", str(exc))
        return 1
    login = LoginWindow()
    login.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
