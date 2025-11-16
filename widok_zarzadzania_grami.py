from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QStackedWidget
# Importuj swoje istniejące klasy tabel
from tabela_gier import TabelaGier 
from tabela_gier2 import TabelaGier2 

class WidokZarzadzaniaGrami(QWidget):
    def __init__(self, conn, runda_id, bundle_dir, stacked_widget=None):
        """
        Ten widżet zarządza przełączaniem między TabelaGier i TabelaGier2.
        
        Args:
            conn: Połączenie z bazą danych.
            runda_id: ID aktualnej rundy.
            bundle_dir: Ścieżka do zasobów (np. ikon).
            stacked_widget: To jest GŁÓWNY QStackedWidget Twojej aplikacji,
                            służący do pokazywania formularzy aktualizacji.
                            Przekazujemy go w dół do widoków tabel.
        """
        super().__init__()
        self.conn = conn
        self.runda_id = runda_id
        self.bundle_dir = bundle_dir
        self.main_app_stacked_widget = stacked_widget # Zapisujemy go

        self.init_ui()

    def init_ui(self):
        # Główny layout (pionowy)
        main_layout = QVBoxLayout(self)
        
        # 1. Layout dla przycisku (poziomy)
        controls_layout = QHBoxLayout()
        self.btn_przelacz = QPushButton("Zmień widok (Lista / Grupowany)")
        # controls_layout.setStyleSheet("color: #1A1A1A; font-size: 10px; padding: 1px; margin: 1px;")
        self.btn_przelacz.clicked.connect(self.przelacz_widok)
        
        controls_layout.addStretch() # Wypycha przycisk na prawą stronę
        controls_layout.addWidget(self.btn_przelacz)
        main_layout.addLayout(controls_layout)

        # 2. QStackedWidget do trzymania tabel
        self.tabela_stack = QStackedWidget()
        
        # Tworzymy instancje obu tabel
        # WAŻNE: Przekazujemy 'parent_manager=self'
        # 'stacked_widget' to ten z głównej aplikacji (do formularzy)
        self.tabela1 = TabelaGier(
            self.conn, self.runda_id, self.bundle_dir, 
            stacked_widget=self.main_app_stacked_widget,
            parent_manager=self
        )
        self.tabela2 = TabelaGier2(
            self.conn, self.runda_id, self.bundle_dir, 
            stacked_widget=self.main_app_stacked_widget,
            parent_manager=self
        )

        # Dodajemy obie tabele do "talii kart"
        self.tabela_stack.addWidget(self.tabela1)
        self.tabela_stack.addWidget(self.tabela2)

        main_layout.addWidget(self.tabela_stack)

    def przelacz_widok(self):
        # Pobieramy aktualny indeks (0 lub 1)
        current_index = self.tabela_stack.currentIndex()
        
        # Przełączamy na drugi indeks
        next_index = 1 - current_index # Prosty sposób na przełączanie 0 -> 1 i 1 -> 0
        self.tabela_stack.setCurrentIndex(next_index)
        
        # Po przełączeniu, odświeżamy dane w widoku, który staje się aktywny
        # Gwarantuje to, że dane są zawsze aktualne
        self.tabela_stack.currentWidget().load_data()

    def load_data(self):
        """
        Ta metoda jest wywoływana przez formularz aktualizacji, gdy 
        dane zostały zmienione. Musimy odświeżyć OBIE tabele.
        """
        print("WidokZarzadzaniaGrami: Odświeżanie danych w obu tabelach...")
        self.tabela1.load_data()
        self.tabela2.load_data()