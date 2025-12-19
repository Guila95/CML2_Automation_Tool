import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import time
import threading
import json
import os
import math
from virl2_client import ClientLibrary
from netmiko import ConnectHandler, NetmikoAuthenticationException

class CMLAutomationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CML2 Automation Tool - Édition Avancée")
        self.root.geometry("1400x900")
        
        # Variables pour stocker les données
        self.cml_client = None
        self.lab = None
        self.nodes = {}
        self.connections = []
        self.topology_elements = {}  # Pour stocker les éléments graphiques
        
        # Configuration CML2 par défaut
        self.cml_config = {
            "controller": "10.10.20.161",
            "username": "developer",
            "password": "C1sco12345",
            "lab_name": "CML Automation Lab"
        }
        
        # Types d'équipements disponibles (complet)
        self.device_types = [
            "external_connector",
            "asav",
            "cat8000v", 
            "csr1000v",
            "iol-xe",
            "alpine",
            "trex",
            "ubuntu",
            "vwlc",
            "wan_emulator",
            "ioll2-xe",
            "iosvl2",
            "unmanaged_switch",
            "iosv",
            "desktop",
            "server"
        ]
        
        # Descriptions détaillées des équipements
        self.device_descriptions = {
            "external_connector": "Connecteur externe pour connexion à des réseaux externes\nFonction: Interface de sortie\nImage: N/A",
            "asav": "ASA virtuel - Pare-feu Cisco Adaptive Security Appliance\nFonction: Pare-feu, VPN, IPS\nImage: asav-9.16.x",
            "cat8000v": "Catalyst 8000V - Routeur SD-WAN virtuel\nFonction: Routeur SD-WAN, Sécurité\nImage: cat8kv-17.09.x",
            "csr1000v": "Cloud Services Router 1000V\nFonction: Routeur Cloud, VPN, SD-WAN\nImage: csr1000v-17.03.x",
            "iol-xe": "IOS on Linux XE - Routeur virtuel\nFonction: Routeur entreprise\nImage: iol-xe-17.09.x",
            "alpine": "Linux Alpine - Distribution légère Linux\nFonction: Serveur Linux, Test\nImage: alpine-3.16",
            "trex": "TRex - Générateur de trafic\nFonction: Test de performance réseau\nImage: trex-2.93",
            "ubuntu": "Ubuntu Server - Distribution Linux\nFonction: Serveur généraliste\nImage: ubuntu-22.04",
            "vwlc": "Virtual Wireless LAN Controller\nFonction: Contrôleur WiFi virtuel\nImage: vwlc-8.10.x",
            "wan_emulator": "Émulateur WAN - Simulation de liens WAN\nFonction: Émulation de latence, perte, gigue\nImage: wan-emulator-1.0",
            "ioll2-xe": "IOS on Linux L2 XE - Switch virtuel\nFonction: Switch L2 avec IOS XE\nImage: ioll2-xe-17.09.x",
            "iosvl2": "IOSv L2 - Switch L2 classique\nFonction: Switch couche 2 standard\nImage: iosvl2-15.2",
            "unmanaged_switch": "Switch non managé\nFonction: Hub/switch basique\nImage: unmanaged-switch",
            "iosv": "IOSv - Routeur virtuel\nFonction: Routeur Cisco standard\nImage: iosv-15.9",
            "desktop": "Poste de travail\nFonction: Client réseau\nImage: desktop-ubuntu",
            "server": "Serveur\nFonction: Serveur applicatif\nImage: server-ubuntu"
        }
        
        # Équipements prédéfinis par catégorie
        self.predefined_devices = [
            # Routeurs
            {"name": "Router-CSR", "type": "csr1000v", "category": "Routeur"},
            {"name": "Router-Cat8k", "type": "cat8000v", "category": "Routeur"},
            {"name": "Router-IOSv", "type": "iosv", "category": "Routeur"},
            {"name": "Router-IOL", "type": "iol-xe", "category": "Routeur"},
            
            # Switches
            {"name": "Switch-IOSvL2", "type": "iosvl2", "category": "Switch"},
            {"name": "Switch-IOL-L2", "type": "ioll2-xe", "category": "Switch"},
            {"name": "Switch-Unmanaged", "type": "unmanaged_switch", "category": "Switch"},
            
            # Sécurité
            {"name": "Firewall-ASAv", "type": "asav", "category": "Sécurité"},
            {"name": "WLC", "type": "vwlc", "category": "Sécurité"},
            
            # Serveurs
            {"name": "Server-Ubuntu", "type": "ubuntu", "category": "Serveur"},
            {"name": "Server-Alpine", "type": "alpine", "category": "Serveur"},
            {"name": "Server-Generic", "type": "server", "category": "Serveur"},
            
            # Clients
            {"name": "PC1", "type": "desktop", "category": "Client"},
            {"name": "PC2", "type": "desktop", "category": "Client"},
            
            # Test
            {"name": "TRex-Traffic", "type": "trex", "category": "Test"},
            {"name": "WAN-Emulator", "type": "wan_emulator", "category": "Test"},
            {"name": "External-Conn", "type": "external_connector", "category": "Connectivité"}
        ]
        
        self.setup_gui()
        self.load_config()
    
    def setup_gui(self):
        # Création des onglets
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Onglet Topologie
        self.tab_topology = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_topology, text="Topologie")
        self.setup_topology_tab()
        
        # Onglet Visualisation Graphique
        self.tab_visualization = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_visualization, text="Visualisation")
        self.setup_visualization_tab()
        
        # Onglet Configuration
        self.tab_config = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_config, text="Configuration")
        self.setup_configuration_tab()
        
        # Onglet Test
        self.tab_test = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_test, text="Test")
        self.setup_test_tab()
        
        # Onglet Paramètres
        self.tab_settings = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_settings, text="Paramètres")
        self.setup_settings_tab()
        
        # Barre de statut
        self.status_bar = tk.Label(self.root, text="Prêt", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def setup_topology_tab(self):
        # PanedWindow pour diviser la fenêtre
        main_pane = ttk.PanedWindow(self.tab_topology, orient=tk.HORIZONTAL)
        main_pane.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Frame gauche - Gestion des équipements
        left_frame = ttk.Frame(main_pane)
        main_pane.add(left_frame, weight=1)
        
        # Frame droite - Connexions
        right_frame = ttk.Frame(main_pane)
        main_pane.add(right_frame, weight=1)
        
        # === FRAME GAUCHE - GESTION ÉQUIPEMENTS ===
        # Frame pour la sélection par catégorie
        frame_category = ttk.LabelFrame(left_frame, text="Catégories d'Équipements", padding=10)
        frame_category.pack(fill=tk.X, padx=5, pady=5)
        
        # Boutons de catégories
        categories = ["Tous", "Routeur", "Switch", "Sécurité", "Serveur", "Client", "Test", "Connectivité"]
        cat_frame = ttk.Frame(frame_category)
        cat_frame.pack()
        
        for i, category in enumerate(categories):
            btn = ttk.Button(cat_frame, text=category, width=12,
                           command=lambda c=category: self.filter_devices_by_category(c))
            btn.grid(row=i//4, column=i%4, padx=2, pady=2)
        
        # Frame pour la liste des équipements
        frame_devices = ttk.LabelFrame(left_frame, text="Équipements Disponibles", padding=10)
        frame_devices.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Treeview avec catégories
        self.device_tree = ttk.Treeview(frame_devices, columns=("Name", "Type", "Category"), 
                                       height=15, show="headings")
        self.device_tree.pack(fill=tk.BOTH, expand=True)
        
        self.device_tree.heading("Name", text="Nom")
        self.device_tree.heading("Type", text="Type")
        self.device_tree.heading("Category", text="Catégorie")
        
        self.device_tree.column("Name", width=120)
        self.device_tree.column("Type", width=100)
        self.device_tree.column("Category", width=100)
        
        # Boutons pour la liste
        btn_frame = ttk.Frame(frame_devices)
        btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(btn_frame, text="Ajouter sélection", 
                  command=self.add_selected_devices).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Description", 
                  command=self.show_device_description).pack(side=tk.LEFT, padx=2)
        
        # Remplir l'arbre
        self.populate_device_tree()
        
        # Frame pour l'ajout manuel
        frame_custom = ttk.LabelFrame(left_frame, text="Ajout Personnalisé", padding=10)
        frame_custom.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(frame_custom, text="Nom:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.device_name_entry = ttk.Entry(frame_custom, width=20)
        self.device_name_entry.grid(row=0, column=1, sticky=tk.W, padx=5)
        
        ttk.Label(frame_custom, text="Type:").grid(row=0, column=2, sticky=tk.W, padx=5)
        self.device_type_combo = ttk.Combobox(frame_custom, values=self.device_types, width=15)
        self.device_type_combo.grid(row=0, column=3, sticky=tk.W, padx=5)
        self.device_type_combo.set("iosvl2")
        
        ttk.Button(frame_custom, text="Description type", 
                  command=self.show_type_description).grid(row=0, column=4, padx=5)
        
        ttk.Button(frame_custom, text="Ajouter", 
                  command=self.add_custom_device).grid(row=1, column=0, columnspan=5, pady=5)
        
        # === FRAME DROITE - CONNEXIONS ===
        # Frame pour les connexions
        frame_connections = ttk.LabelFrame(right_frame, text="Connexions", padding=10)
        frame_connections.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Sélection des équipements à connecter
        form_frame = ttk.Frame(frame_connections)
        form_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(form_frame, text="Source:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.source_device_combo = ttk.Combobox(form_frame, width=20)
        self.source_device_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(form_frame, text="Port:").grid(row=0, column=2, sticky=tk.W, pady=2)
        self.source_port_entry = ttk.Entry(form_frame, width=8)
        self.source_port_entry.grid(row=0, column=3, sticky=tk.W, padx=5, pady=2)
        self.source_port_entry.insert(0, "0")
        
        ttk.Label(form_frame, text="Destination:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.dest_device_combo = ttk.Combobox(form_frame, width=20)
        self.dest_device_combo.grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(form_frame, text="Port:").grid(row=1, column=2, sticky=tk.W, pady=2)
        self.dest_port_entry = ttk.Entry(form_frame, width=8)
        self.dest_port_entry.grid(row=1, column=3, sticky=tk.W, padx=5, pady=2)
        self.dest_port_entry.insert(0, "0")
        
        ttk.Button(form_frame, text="Ajouter connexion",
                  command=self.add_connection).grid(row=1, column=4, padx=10)
        
        # Liste des connexions avec scrollbar
        list_frame = ttk.Frame(frame_connections)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Scrollbar pour l'arbre
        tree_scroll = ttk.Scrollbar(list_frame)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.connections_tree = ttk.Treeview(list_frame, 
                                            columns=("Source", "PortS", "Dest", "PortD"), 
                                            height=8, show="headings",
                                            yscrollcommand=tree_scroll.set)
        self.connections_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll.config(command=self.connections_tree.yview)
        
        self.connections_tree.heading("Source", text="Source")
        self.connections_tree.heading("PortS", text="Port Source")
        self.connections_tree.heading("Dest", text="Destination")
        self.connections_tree.heading("PortD", text="Port Dest")
        
        self.connections_tree.column("Source", width=120)
        self.connections_tree.column("PortS", width=80)
        self.connections_tree.column("Dest", width=120)
        self.connections_tree.column("PortD", width=80)
        
        # Boutons pour les connexions
        conn_btn_frame = ttk.Frame(frame_connections)
        conn_btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(conn_btn_frame, text="Supprimer connexion",
                  command=self.delete_connection).pack(side=tk.LEFT, padx=2)
        ttk.Button(conn_btn_frame, text="Vérifier connectivité",
                  command=self.check_connectivity).pack(side=tk.LEFT, padx=2)
        
        # Frame pour les actions du labo
        frame_actions = ttk.LabelFrame(right_frame, text="Actions du Labo", padding=10)
        frame_actions.pack(fill=tk.X, padx=5, pady=5)
        
        btn_action_frame = ttk.Frame(frame_actions)
        btn_action_frame.pack()
        
        ttk.Button(btn_action_frame, text="Créer et démarrer le labo",
                  command=self.create_and_start_lab).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_action_frame, text="Visualiser topologie",
                  command=self.show_visualization).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_action_frame, text="Arrêter le labo",
                  command=self.stop_lab).pack(side=tk.LEFT, padx=2)
        
        btn_action_frame2 = ttk.Frame(frame_actions)
        btn_action_frame2.pack(pady=5)
        
        ttk.Button(btn_action_frame2, text="Supprimer le labo",
                  command=self.delete_lab).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_action_frame2, text="Exporter topologie",
                  command=self.export_topology).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_action_frame2, text="Importer topologie",
                  command=self.import_topology).pack(side=tk.LEFT, padx=2)
    
    def setup_visualization_tab(self):
        # Frame principal pour la visualisation
        main_frame = ttk.Frame(self.tab_visualization)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame pour les contrôles
        control_frame = ttk.LabelFrame(main_frame, text="Contrôles de Visualisation", padding=10)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Boutons de contrôle
        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack()
        
        ttk.Button(btn_frame, text="Actualiser", 
                  command=self.refresh_visualization).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Disposition Circulaire", 
                  command=lambda: self.draw_topology("circular")).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Disposition Grille", 
                  command=lambda: self.draw_topology("grid")).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Disposition Hiérarchique", 
                  command=lambda: self.draw_topology("hierarchical")).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Zoom +", 
                  command=self.zoom_in).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Zoom -", 
                  command=self.zoom_out).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Réinitialiser vue", 
                  command=self.reset_view).pack(side=tk.LEFT, padx=5)
        
        # Canvas pour la visualisation avec scrollbars
        canvas_frame = ttk.Frame(main_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbars
        h_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        v_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Canvas
        self.canvas = tk.Canvas(canvas_frame, 
                               bg="white",
                               xscrollcommand=h_scrollbar.set,
                               yscrollcommand=v_scrollbar.set,
                               scrollregion=(0, 0, 2000, 2000))
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        h_scrollbar.config(command=self.canvas.xview)
        v_scrollbar.config(command=self.canvas.yview)
        
        # Variables pour le zoom
        self.zoom_level = 1.0
        self.canvas_objects = []
        
        # Bind des événements de souris
        self.canvas.bind("<ButtonPress-1>", self.start_drag)
        self.canvas.bind("<B1-Motion>", self.drag)
        self.canvas.bind("<MouseWheel>", self.mouse_wheel)  # Windows
        self.canvas.bind("<Button-4>", self.mouse_wheel)    # Linux
        self.canvas.bind("<Button-5>", self.mouse_wheel)    # Linux
        
        # Légende
        legend_frame = ttk.LabelFrame(main_frame, text="Légende", padding=10)
        legend_frame.pack(fill=tk.X, pady=(10, 0))
        
        legend_canvas = tk.Canvas(legend_frame, height=60, bg="white")
        legend_canvas.pack(fill=tk.X)
        
        # Dessiner la légende
        colors = {
            "Routeur": "#FF6B6B",
            "Switch": "#4ECDC4",
            "Sécurité": "#FFD166",
            "Serveur": "#06D6A0",
            "Client": "#118AB2",
            "Test": "#EF476F",
            "Connectivité": "#073B4C"
        }
        
        x_pos = 20
        for category, color in colors.items():
            legend_canvas.create_rectangle(x_pos, 20, x_pos + 20, 40, fill=color, outline="black")
            legend_canvas.create_text(x_pos + 30, 30, text=category, anchor=tk.W)
            x_pos += 100
    
    def setup_configuration_tab(self):
        # Configuration tab remains mostly the same, but with better organization
        main_pane = ttk.PanedWindow(self.tab_config, orient=tk.VERTICAL)
        main_pane.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Top frame for device selection and config
        top_frame = ttk.Frame(main_pane)
        main_pane.add(top_frame, weight=2)
        
        # Bottom frame for output
        bottom_frame = ttk.Frame(main_pane)
        main_pane.add(bottom_frame, weight=1)
        
        # === TOP FRAME ===
        # Device selection
        frame_select = ttk.LabelFrame(top_frame, text="Sélection de l'Équipement", padding=10)
        frame_select.pack(fill=tk.X, padx=5, pady=5)
        
        selection_frame = ttk.Frame(frame_select)
        selection_frame.pack(fill=tk.X)
        
        ttk.Label(selection_frame, text="Équipement:").pack(side=tk.LEFT, padx=5)
        self.config_device_combo = ttk.Combobox(selection_frame, width=30)
        self.config_device_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(selection_frame, text="Actualiser",
                  command=self.refresh_device_list).pack(side=tk.LEFT, padx=10)
        ttk.Button(selection_frame, text="Info équipement",
                  command=self.show_device_info).pack(side=tk.LEFT, padx=5)
        
        # Config templates
        frame_templates = ttk.LabelFrame(top_frame, text="Templates de Configuration", padding=10)
        frame_templates.pack(fill=tk.X, padx=5, pady=5)
        
        templates_frame = ttk.Frame(frame_templates)
        templates_frame.pack()
        
        templates = [
            ("Routeur de base", self.load_router_template),
            ("Switch L2", self.load_switch_template),
            ("Pare-feu ASA", self.load_firewall_template),
            ("Configuration IP", self.load_ip_template),
            ("Routage OSPF", self.load_ospf_template),
            ("VLAN Trunk", self.load_vlan_template)
        ]
        
        for i, (name, cmd) in enumerate(templates):
            btn = ttk.Button(templates_frame, text=name, command=cmd)
            btn.grid(row=i//3, column=i%3, padx=5, pady=5, sticky="ew")
        
        # Configuration editor
        frame_edit = ttk.LabelFrame(top_frame, text="Éditeur de Configuration", padding=10)
        frame_edit.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Toolbar for editor
        toolbar = ttk.Frame(frame_edit)
        toolbar.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(toolbar, text="Charger fichier", 
                  command=self.load_config_file).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Sauvegarder", 
                  command=self.save_config_file).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Effacer", 
                  command=self.clear_config_text).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Valider syntaxe", 
                  command=self.validate_config).pack(side=tk.LEFT, padx=2)
        
        # Text editor with line numbers
        editor_frame = ttk.Frame(frame_edit)
        editor_frame.pack(fill=tk.BOTH, expand=True)
        
        # Line numbers
        self.line_numbers = tk.Text(editor_frame, width=4, padx=3, takefocus=0, 
                                   border=0, background='lightgrey', state='disabled')
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        
        # Main text editor
        self.config_text = scrolledtext.ScrolledText(editor_frame, wrap=tk.WORD, 
                                                    font=("Courier", 10))
        self.config_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Configure tags for syntax highlighting
        self.config_text.tag_configure("command", foreground="blue")
        self.config_text.tag_configure("interface", foreground="darkgreen")
        self.config_text.tag_configure("comment", foreground="gray")
        
        # Bind events for line numbers
        self.config_text.bind('<KeyRelease>', self.update_line_numbers)
        self.config_text.bind('<MouseWheel>', self.update_line_numbers)
        
        # === BOTTOM FRAME ===
        frame_output = ttk.LabelFrame(bottom_frame, text="Sortie de Configuration", padding=10)
        frame_output.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Output toolbar
        output_toolbar = ttk.Frame(frame_output)
        output_toolbar.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(output_toolbar, text="Appliquer configuration",
                  command=self.apply_configuration).pack(side=tk.LEFT, padx=2)
        ttk.Button(output_toolbar, text="Tester configuration",
                  command=self.test_configuration).pack(side=tk.LEFT, padx=2)
        ttk.Button(output_toolbar, text="Effacer sortie",
                  command=self.clear_output).pack(side=tk.LEFT, padx=2)
        ttk.Button(output_toolbar, text="Exporter logs",
                  command=self.export_logs).pack(side=tk.LEFT, padx=2)
        
        # Output text area
        self.output_text = scrolledtext.ScrolledText(frame_output, wrap=tk.WORD, 
                                                    height=10, font=("Courier", 9))
        self.output_text.pack(fill=tk.BOTH, expand=True)
    
    def setup_test_tab(self):
        """Configure l'onglet Test"""
        main_frame = ttk.Frame(self.tab_test)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame pour la sélection
        frame_select = ttk.LabelFrame(main_frame, text="Sélection du Test", padding=10)
        frame_select.pack(fill=tk.X, pady=(0, 10))
        
        select_frame = ttk.Frame(frame_select)
        select_frame.pack()
        
        ttk.Label(select_frame, text="Équipement:").pack(side=tk.LEFT, padx=5)
        self.test_device_combo = ttk.Combobox(select_frame, width=25)
        self.test_device_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(select_frame, text="Type de test:").pack(side=tk.LEFT, padx=5)
        self.test_type_combo = ttk.Combobox(select_frame, 
                                           values=["Ping", "Show running-config", "Show interfaces",
                                                  "Show version", "Show IP route", "Show VLAN"],
                                           width=20)
        self.test_type_combo.pack(side=tk.LEFT, padx=5)
        self.test_type_combo.set("Ping")
        
        # Frame pour les paramètres
        frame_params = ttk.LabelFrame(main_frame, text="Paramètres", padding=10)
        frame_params.pack(fill=tk.X, pady=(0, 10))
        
        # Adresse IP pour ping
        self.ping_frame = ttk.Frame(frame_params)
        self.ping_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(self.ping_frame, text="Adresse IP:").pack(side=tk.LEFT, padx=5)
        self.ping_ip_entry = ttk.Entry(self.ping_frame, width=20)
        self.ping_ip_entry.pack(side=tk.LEFT, padx=5)
        self.ping_ip_entry.insert(0, "192.168.1.1")
        
        # Commandes personnalisées
        ttk.Label(frame_params, text="Commande personnalisée:").pack(anchor=tk.W)
        self.custom_cmd_entry = ttk.Entry(frame_params, width=50)
        self.custom_cmd_entry.pack(fill=tk.X, pady=5)
        
        # Boutons d'exécution
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(btn_frame, text="Exécuter test standard",
                  command=self.run_standard_test).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Exécuter commande personnalisée",
                  command=self.run_custom_test).pack(side=tk.LEFT, padx=5)
        
        # Zone de résultats
        frame_results = ttk.LabelFrame(main_frame, text="Résultats", padding=10)
        frame_results.pack(fill=tk.BOTH, expand=True)
        
        self.test_output = scrolledtext.ScrolledText(frame_results, wrap=tk.WORD, height=15)
        self.test_output.pack(fill=tk.BOTH, expand=True)
        
        # Boutons pour les résultats
        result_btn_frame = ttk.Frame(frame_results)
        result_btn_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(result_btn_frame, text="Effacer résultats",
                  command=self.clear_test_results).pack(side=tk.LEFT, padx=5)
        ttk.Button(result_btn_frame, text="Exporter résultats",
                  command=self.export_test_results).pack(side=tk.LEFT, padx=5)
    
    def setup_settings_tab(self):
        """Configure l'onglet Paramètres"""
        main_frame = ttk.Frame(self.tab_settings)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame pour CML
        frame_cml = ttk.LabelFrame(main_frame, text="Configuration CML2", padding=10)
        frame_cml.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(frame_cml, text="Contrôleur:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.controller_entry = ttk.Entry(frame_cml, width=30)
        self.controller_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        self.controller_entry.insert(0, self.cml_config["controller"])
        
        ttk.Label(frame_cml, text="Utilisateur:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.username_entry = ttk.Entry(frame_cml, width=30)
        self.username_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        self.username_entry.insert(0, self.cml_config["username"])
        
        ttk.Label(frame_cml, text="Mot de passe:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.password_entry = ttk.Entry(frame_cml, width=30, show="*")
        self.password_entry.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        self.password_entry.insert(0, self.cml_config["password"])
        
        # Frame pour les équipements
        frame_devices = ttk.LabelFrame(main_frame, text="Identifiants Équipements", padding=10)
        frame_devices.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(frame_devices, text="Utilisateur:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.device_user_entry = ttk.Entry(frame_devices, width=20)
        self.device_user_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        self.device_user_entry.insert(0, "cisco")
        
        ttk.Label(frame_devices, text="Mot de passe:").grid(row=0, column=2, sticky=tk.W, padx=10, pady=5)
        self.device_pass_entry = ttk.Entry(frame_devices, width=20, show="*")
        self.device_pass_entry.grid(row=0, column=3, sticky=tk.W, padx=5, pady=5)
        self.device_pass_entry.insert(0, "cisco")
        
        # Frame pour le lab
        frame_lab = ttk.LabelFrame(main_frame, text="Paramètres Lab", padding=10)
        frame_lab.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(frame_lab, text="Nom du lab:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.lab_name_entry = ttk.Entry(frame_lab, width=30)
        self.lab_name_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        self.lab_name_entry.insert(0, self.cml_config["lab_name"])
        
        # Frame pour les actions
        frame_actions = ttk.LabelFrame(main_frame, text="Actions", padding=10)
        frame_actions.pack(fill=tk.X, pady=(0, 10))
        
        btn_frame = ttk.Frame(frame_actions)
        btn_frame.pack()
        
        ttk.Button(btn_frame, text="Sauvegarder paramètres",
                  command=self.save_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Tester connexion CML",
                  command=self.test_cml_connection).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Réinitialiser",
                  command=self.reset_settings).pack(side=tk.LEFT, padx=5)
    
    # ===== MÉTHODES POUR LA TOPOLOGIE =====
    
    def populate_device_tree(self):
        """Remplit l'arbre des équipements disponibles"""
        self.device_tree.delete(*self.device_tree.get_children())
        for device in self.predefined_devices:
            self.device_tree.insert("", tk.END, values=(
                device["name"], device["type"], device["category"]
            ))
    
    def filter_devices_by_category(self, category):
        """Filtre les équipements par catégorie"""
        self.device_tree.delete(*self.device_tree.get_children())
        
        if category == "Tous":
            devices = self.predefined_devices
        else:
            devices = [d for d in self.predefined_devices if d["category"] == category]
        
        for device in devices:
            self.device_tree.insert("", tk.END, values=(
                device["name"], device["type"], device["category"]
            ))
    
    def show_device_description(self):
        """Affiche la description de l'équipement sélectionné"""
        selection = self.device_tree.selection()
        if not selection:
            messagebox.showwarning("Aucune sélection", "Veuillez sélectionner un équipement.")
            return
        
        item = self.device_tree.item(selection[0])
        device_type = item["values"][1]
        
        self.show_description_window(device_type)
    
    def show_type_description(self):
        """Affiche la description du type sélectionné"""
        device_type = self.device_type_combo.get()
        self.show_description_window(device_type)
    
    def show_description_window(self, device_type):
        """Affiche une fenêtre avec la description détaillée"""
        desc_window = tk.Toplevel(self.root)
        desc_window.title(f"Description - {device_type}")
        desc_window.geometry("500x400")
        desc_window.transient(self.root)
        desc_window.grab_set()
        
        # Cadre principal
        main_frame = ttk.Frame(desc_window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Titre
        title_label = ttk.Label(main_frame, text=device_type.upper(), 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Description
        description = self.device_descriptions.get(device_type, "Description non disponible.")
        
        desc_text = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, 
                                             height=10, font=("Arial", 10))
        desc_text.pack(fill=tk.BOTH, expand=True, pady=10)
        desc_text.insert(tk.END, description)
        desc_text.config(state="disabled")
        
        # Caractéristiques techniques (simulées)
        tech_frame = ttk.LabelFrame(main_frame, text="Caractéristiques Techniques", padding=10)
        tech_frame.pack(fill=tk.X, pady=10)
        
        # Caractéristiques par type
        tech_info = {
            "iosv": "• Processeur: 1 vCPU\n• Mémoire: 512MB-2GB\n• Stockage: 256MB-1GB\n• IOS: 15.x",
            "iosvl2": "• Processeur: 1 vCPU\n• Mémoire: 512MB-2GB\n• Stockage: 256MB-1GB\n• IOS: 15.2",
            "csr1000v": "• Processeur: 2-4 vCPU\n• Mémoire: 4-8GB\n• Stockage: 8-16GB\n• IOS-XE: 17.x",
            "asav": "• Processeur: 2-4 vCPU\n• Mémoire: 4-8GB\n• Stockage: 8-16GB\n• ASA: 9.x",
            "ubuntu": "• Processeur: 1-2 vCPU\n• Mémoire: 1-4GB\n• Stockage: 8-32GB\n• OS: Ubuntu 22.04",
            "trex": "• Processeur: 4-8 vCPU\n• Mémoire: 8-16GB\n• Stockage: 16-32GB\n• DPDK optimisé"
        }
        
        default_tech = "• Processeur: 1-2 vCPU\n• Mémoire: 512MB-4GB\n• Stockage: 1-8GB"
        
        tech_label = ttk.Label(tech_frame, text=tech_info.get(device_type, default_tech),
                              justify=tk.LEFT)
        tech_label.pack()
        
        # Bouton de fermeture
        ttk.Button(main_frame, text="Fermer", 
                  command=desc_window.destroy).pack(pady=10)
    
    def add_selected_devices(self):
        """Ajoute les équipements sélectionnés à la topologie"""
        selected = self.device_tree.selection()
        if not selected:
            messagebox.showwarning("Aucune sélection", "Veuillez sélectionner au moins un équipement.")
            return
        
        for item_id in selected:
            item = self.device_tree.item(item_id)
            device_name = item["values"][0]
            device_type = item["values"][1]
            
            # Générer un nom unique si nécessaire
            base_name = device_name
            counter = 1
            while device_name in self.nodes:
                device_name = f"{base_name}_{counter}"
                counter += 1
            
            # Ajouter aux combobox
            current_values = list(self.source_device_combo['values'])
            if device_name not in current_values:
                self.source_device_combo['values'] = current_values + [device_name]
                self.dest_device_combo['values'] = current_values + [device_name]
                self.config_device_combo['values'] = current_values + [device_name]
                self.test_device_combo['values'] = current_values + [device_name]
            
            # Stocker l'équipement
            self.nodes[device_name] = {
                "type": device_type,
                "category": item["values"][2],
                "interfaces": {}
            }
        
        self.update_status(f"{len(selected)} équipement(s) ajouté(s)")
        self.refresh_visualization()
    
    def add_custom_device(self):
        """Ajoute un équipement personnalisé"""
        name = self.device_name_entry.get().strip()
        dev_type = self.device_type_combo.get()
        
        if not name:
            messagebox.showerror("Erreur", "Veuillez entrer un nom pour l'équipement.")
            return
        
        if name in self.nodes:
            messagebox.showerror("Erreur", "Un équipement avec ce nom existe déjà.")
            return
        
        # Déterminer la catégorie
        category = self.get_category_from_type(dev_type)
        
        # Ajouter aux combobox
        current_values = list(self.source_device_combo['values'])
        self.source_device_combo['values'] = current_values + [name]
        self.dest_device_combo['values'] = current_values + [name]
        self.config_device_combo['values'] = current_values + [name]
        self.test_device_combo['values'] = current_values + [name]
        
        # Stocker l'équipement
        self.nodes[name] = {
            "type": dev_type,
            "category": category,
            "interfaces": {}
        }
        
        self.update_status(f"Équipement '{name}' ajouté ({dev_type})")
        self.device_name_entry.delete(0, tk.END)
        self.refresh_visualization()
    
    def get_category_from_type(self, device_type):
        """Retourne la catégorie basée sur le type d'équipement"""
        categories = {
            "iosv": "Routeur",
            "csr1000v": "Routeur",
            "cat8000v": "Routeur",
            "iol-xe": "Routeur",
            "iosvl2": "Switch",
            "ioll2-xe": "Switch",
            "unmanaged_switch": "Switch",
            "asav": "Sécurité",
            "vwlc": "Sécurité",
            "ubuntu": "Serveur",
            "alpine": "Serveur",
            "server": "Serveur",
            "desktop": "Client",
            "trex": "Test",
            "wan_emulator": "Test",
            "external_connector": "Connectivité"
        }
        return categories.get(device_type, "Autre")
    
    def add_connection(self):
        """Ajoute une connexion entre deux équipements"""
        source = self.source_device_combo.get()
        dest = self.dest_device_combo.get()
        port_s = self.source_port_entry.get()
        port_d = self.dest_port_entry.get()
        
        if not source or not dest:
            messagebox.showerror("Erreur", "Veuillez sélectionner les deux équipements.")
            return
        
        if source == dest:
            messagebox.showerror("Erreur", "Impossible de connecter un équipement à lui-même.")
            return
        
        try:
            port_s = int(port_s)
            port_d = int(port_d)
        except ValueError:
            messagebox.showerror("Erreur", "Les ports doivent être des nombres.")
            return
        
        # Vérifier si la connexion existe déjà
        for conn in self.connections:
            if (conn["source"] == source and conn["dest"] == dest and 
                conn["port_s"] == port_s and conn["port_d"] == port_d):
                messagebox.showwarning("Connexion existante", "Cette connexion existe déjà.")
                return
        
        # Ajouter la connexion
        connection = {
            "source": source,
            "port_s": port_s,
            "dest": dest,
            "port_d": port_d
        }
        self.connections.append(connection)
        
        # Mettre à jour l'arbre
        self.connections_tree.insert("", tk.END, 
                                   values=(source, port_s, dest, port_d))
        
        self.update_status(f"Connexion ajoutée: {source}:{port_s} -> {dest}:{port_d}")
        self.refresh_visualization()
    
    def delete_connection(self):
        """Supprime la connexion sélectionnée"""
        selected = self.connections_tree.selection()
        if not selected:
            messagebox.showwarning("Aucune sélection", "Veuillez sélectionner une connexion à supprimer.")
            return
        
        for item in selected:
            values = self.connections_tree.item(item)["values"]
            self.connections_tree.delete(item)
            
            # Supprimer de la liste des connexions
            for i, conn in enumerate(self.connections):
                if (conn["source"] == values[0] and conn["port_s"] == values[1] and
                    conn["dest"] == values[2] and conn["port_d"] == values[3]):
                    del self.connections[i]
                    break
        
        self.update_status("Connexion(s) supprimée(s)")
        self.refresh_visualization()
    
    def check_connectivity(self):
        """Vérifie la connectivité de la topologie"""
        if not self.connections:
            messagebox.showinfo("Connectivité", "Aucune connexion définie.")
            return
        
        # Simple vérification de base
        issues = []
        
        # Vérifier les équipements non connectés
        connected_devices = set()
        for conn in self.connections:
            connected_devices.add(conn["source"])
            connected_devices.add(conn["dest"])
        
        for device in self.nodes:
            if device not in connected_devices:
                issues.append(f"⚠ {device} n'est connecté à aucun autre équipement")
        
        # Vérifier les connexions doubles
        for i, conn1 in enumerate(self.connections):
            for conn2 in self.connections[i+1:]:
                if (conn1["source"] == conn2["source"] and 
                    conn1["port_s"] == conn2["port_s"]):
                    issues.append(f"⚠ Port {conn1['port_s']} de {conn1['source']} utilisé deux fois")
        
        # Afficher les résultats
        if issues:
            result = "Problèmes de connectivité détectés:\n\n" + "\n".join(issues)
        else:
            result = "✅ Topologie valide - Tous les équipements sont correctement connectés"
        
        messagebox.showinfo("Vérification Connectivité", result)
    
    # ===== MÉTHODES POUR LA VISUALISATION =====
    
    def show_visualization(self):
        """Affiche l'onglet de visualisation"""
        self.notebook.select(self.tab_visualization)
        self.refresh_visualization()
    
    def refresh_visualization(self):
        """Rafraîchit la visualisation"""
        self.draw_topology("circular")
    
    def draw_topology(self, layout="circular"):
        """Dessine la topologie avec le layout spécifié"""
        # Effacer le canvas
        self.canvas.delete("all")
        self.canvas_objects.clear()
        
        if not self.nodes:
            self.canvas.create_text(400, 300, text="Aucun équipement dans la topologie",
                                   font=("Arial", 14), fill="gray")
            return
        
        # Définir les couleurs par catégorie
        category_colors = {
            "Routeur": "#FF6B6B",      # Rouge
            "Switch": "#4ECDC4",       # Turquoise
            "Sécurité": "#FFD166",     # Jaune
            "Serveur": "#06D6A0",      # Vert
            "Client": "#118AB2",       # Bleu
            "Test": "#EF476F",         # Rose
            "Connectivité": "#073B4C", # Noir bleuté
            "Autre": "#999999"         # Gris
        }
        
        # Calculer les positions selon le layout
        positions = {}
        node_list = list(self.nodes.keys())
        
        if layout == "circular":
            positions = self.calculate_circular_layout(node_list)
        elif layout == "grid":
            positions = self.calculate_grid_layout(node_list)
        elif layout == "hierarchical":
            positions = self.calculate_hierarchical_layout(node_list)
        
        # Appliquer le zoom
        for node in positions:
            x, y = positions[node]
            positions[node] = (x * self.zoom_level, y * self.zoom_level)
        
        # Dessiner les connexions d'abord (pour qu'elles soient en dessous)
        for conn in self.connections:
            source = conn["source"]
            dest = conn["dest"]
            
            if source in positions and dest in positions:
                x1, y1 = positions[source]
                x2, y2 = positions[dest]
                
                # Dessiner la ligne
                line = self.canvas.create_line(x1, y1, x2, y2, 
                                              fill="#666666", width=2, arrow=tk.LAST)
                self.canvas_objects.append(("line", line))
                
                # Ajouter le label des ports
                mid_x = (x1 + x2) / 2
                mid_y = (y1 + y2) / 2
                
                port_text = f"{conn['port_s']}→{conn['port_d']}"
                text_id = self.canvas.create_text(mid_x, mid_y, text=port_text,
                                                 fill="#333333", font=("Arial", 8))
                self.canvas_objects.append(("text", text_id))
        
        # Dessiner les nœuds
        for node_name, (x, y) in positions.items():
            node_info = self.nodes[node_name]
            category = node_info.get("category", "Autre")
            color = category_colors.get(category, "#999999")
            
            # Dessiner le rectangle (nœud)
            rect = self.canvas.create_rectangle(x-60, y-30, x+60, y+30,
                                               fill=color, outline="#333333", width=2)
            self.canvas_objects.append(("node", rect, node_name))
            
            # Ajouter le nom
            name_text = self.canvas.create_text(x, y-10, text=node_name,
                                               font=("Arial", 10, "bold"), fill="#000000")
            self.canvas_objects.append(("text", name_text))
            
            # Ajouter le type
            type_text = self.canvas.create_text(x, y+10, text=node_info["type"],
                                               font=("Arial", 8), fill="#333333")
            self.canvas_objects.append(("text", type_text))
            
            # Bind des événements pour l'interaction
            self.canvas.tag_bind(rect, "<Enter>", 
                                lambda e, n=node_name: self.highlight_node(n))
            self.canvas.tag_bind(rect, "<Leave>", 
                                lambda e: self.clear_highlight())
            self.canvas.tag_bind(rect, "<Button-3>", 
                                lambda e, n=node_name: self.show_node_context_menu(e, n))
        
        # Mettre à jour la région de défilement
        self.update_scroll_region()
    
    def calculate_circular_layout(self, nodes):
        """Calcule les positions pour un layout circulaire"""
        positions = {}
        center_x, center_y = 500, 400
        radius = min(300, len(nodes) * 30)
        
        for i, node in enumerate(nodes):
            angle = 2 * math.pi * i / len(nodes)
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            positions[node] = (x, y)
        
        return positions
    
    def calculate_grid_layout(self, nodes):
        """Calcule les positions pour un layout en grille"""
        positions = {}
        cols = math.ceil(math.sqrt(len(nodes)))
        start_x, start_y = 200, 200
        spacing = 150
        
        for i, node in enumerate(nodes):
            row = i // cols
            col = i % cols
            x = start_x + col * spacing
            y = start_y + row * spacing
            positions[node] = (x, y)
        
        return positions
    
    def calculate_hierarchical_layout(self, nodes):
        """Calcule les positions pour un layout hiérarchique"""
        positions = {}
        
        # Grouper par catégorie
        categories = {}
        for node in nodes:
            category = self.nodes[node].get("category", "Autre")
            if category not in categories:
                categories[category] = []
            categories[category].append(node)
        
        # Positionner les catégories
        start_x, start_y = 200, 150
        category_spacing = 300
        node_spacing = 120
        
        for i, (category, node_list) in enumerate(categories.items()):
            cat_x = start_x + i * category_spacing
            
            for j, node in enumerate(node_list):
                x = cat_x
                y = start_y + j * node_spacing
                positions[node] = (x, y)
        
        return positions
    
    def highlight_node(self, node_name):
        """Met en surbrillance un nœud et ses connexions"""
        # Trouver le rectangle du nœud
        for obj in self.canvas_objects:
            if obj[0] == "node" and obj[2] == node_name:
                rect_id = obj[1]
                self.canvas.itemconfig(rect_id, outline="#FF0000", width=3)
                break
        
        # Mettre en surbrillance les connexions
        for conn in self.connections:
            if conn["source"] == node_name or conn["dest"] == node_name:
                # Trouver la ligne correspondante
                for i, obj in enumerate(self.canvas_objects):
                    if obj[0] == "line":
                        # On ne peut pas facilement identifier quelle ligne correspond à quelle connexion
                        # Une approche plus sophistiquée serait nécessaire
                        pass
    
    def clear_highlight(self):
        """Efface toutes les surbrillances"""
        for obj in self.canvas_objects:
            if obj[0] == "node":
                rect_id = obj[1]
                self.canvas.itemconfig(rect_id, outline="#333333", width=2)
    
    def show_node_context_menu(self, event, node_name):
        """Affiche un menu contextuel pour un nœud"""
        context_menu = tk.Menu(self.root, tearoff=0)
        context_menu.add_command(label=f"Configurer {node_name}", 
                                command=lambda: self.configure_node(node_name))
        context_menu.add_command(label="Supprimer", 
                                command=lambda: self.delete_node(node_name))
        context_menu.add_command(label="Propriétés", 
                                command=lambda: self.show_node_properties(node_name))
        context_menu.add_separator()
        context_menu.add_command(label="Connecter à...", 
                                command=lambda: self.connect_from_node(node_name))
        
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
    
    def configure_node(self, node_name):
        """Configure un nœud spécifique"""
        self.notebook.select(self.tab_config)
        self.config_device_combo.set(node_name)
    
    def delete_node(self, node_name):
        """Supprime un nœud de la topologie"""
        if messagebox.askyesno("Confirmation", 
                              f"Supprimer l'équipement '{node_name}' et toutes ses connexions?"):
            # Supprimer le nœud
            del self.nodes[node_name]
            
            # Supprimer les connexions associées
            self.connections = [conn for conn in self.connections 
                              if conn["source"] != node_name and conn["dest"] != node_name]
            
            # Mettre à jour les combobox
            for combo in [self.source_device_combo, self.dest_device_combo, 
                         self.config_device_combo, self.test_device_combo]:
                values = list(combo['values'])
                if node_name in values:
                    values.remove(node_name)
                    combo['values'] = values
            
            # Mettre à jour l'arbre des connexions
            self.connections_tree.delete(*self.connections_tree.get_children())
            for conn in self.connections:
                self.connections_tree.insert("", tk.END, 
                                           values=(conn["source"], conn["port_s"], 
                                                  conn["dest"], conn["port_d"]))
            
            self.update_status(f"Équipement '{node_name}' supprimé")
            self.refresh_visualization()
    
    def show_node_properties(self, node_name):
        """Affiche les propriétés d'un nœud"""
        if node_name not in self.nodes:
            return
        
        node_info = self.nodes[node_name]
        
        prop_window = tk.Toplevel(self.root)
        prop_window.title(f"Propriétés - {node_name}")
        prop_window.geometry("400x300")
        
        main_frame = ttk.Frame(prop_window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Titre
        ttk.Label(main_frame, text=node_name, 
                 font=("Arial", 14, "bold")).pack(pady=(0, 10))
        
        # Informations
        info_frame = ttk.LabelFrame(main_frame, text="Informations", padding=10)
        info_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(info_frame, text=f"Type: {node_info['type']}").pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"Catégorie: {node_info.get('category', 'Non définie')}").pack(anchor=tk.W)
        
        # Interfaces
        if node_info["interfaces"]:
            intf_frame = ttk.LabelFrame(main_frame, text="Interfaces", padding=10)
            intf_frame.pack(fill=tk.BOTH, expand=True, pady=5)
            
            for intf, status in node_info["interfaces"].items():
                ttk.Label(intf_frame, text=f"• {intf}: {status}").pack(anchor=tk.W)
        else:
            ttk.Label(main_frame, text="Aucune interface configurée").pack(pady=5)
        
        # Bouton de fermeture
        ttk.Button(main_frame, text="Fermer", 
                  command=prop_window.destroy).pack(pady=10)
    
    def connect_from_node(self, node_name):
        """Prépare la connexion depuis un nœud spécifique"""
        self.source_device_combo.set(node_name)
        self.notebook.select(self.tab_topology)
    
    def zoom_in(self):
        """Zoom dans la visualisation"""
        self.zoom_level *= 1.2
        self.refresh_visualization()
    
    def zoom_out(self):
        """Zoom hors de la visualisation"""
        self.zoom_level /= 1.2
        if self.zoom_level < 0.5:
            self.zoom_level = 0.5
        self.refresh_visualization()
    
    def reset_view(self):
        """Réinitialise la vue"""
        self.zoom_level = 1.0
        self.refresh_visualization()
    
    def update_scroll_region(self):
        """Met à jour la région de défilement du canvas"""
        bbox = self.canvas.bbox("all")
        if bbox:
            padding = 100
            self.canvas.configure(scrollregion=(
                bbox[0] - padding, bbox[1] - padding,
                bbox[2] + padding, bbox[3] + padding
            ))
    
    def start_drag(self, event):
        """Début du glissement du canvas"""
        self.canvas.scan_mark(event.x, event.y)
    
    def drag(self, event):
        """Glissement du canvas"""
        self.canvas.scan_dragto(event.x, event.y, gain=1)
    
    def mouse_wheel(self, event):
        """Gestion de la molette de la souris"""
        if event.delta > 0 or event.num == 4:
            self.zoom_in()
        else:
            self.zoom_out()
    
    # ===== MÉTHODES POUR LES TEMPLATES DE CONFIGURATION =====
    
    def load_router_template(self):
        """Charge un template de configuration pour routeur"""
        template = """! Configuration de base pour routeur
enable
configure terminal
hostname ROUTER
no ip domain lookup
!
! Configuration des interfaces
interface GigabitEthernet0/0
 description LAN Interface
 ip address 192.168.1.1 255.255.255.0
 no shutdown
!
interface GigabitEthernet0/1
 description WAN Interface
 ip address 10.0.0.1 255.255.255.252
 no shutdown
!
! Routage par défaut
ip route 0.0.0.0 0.0.0.0 10.0.0.2
!
! Configuration SSH
ip domain-name example.com
crypto key generate rsa modulus 2048
username admin privilege 15 secret cisco
line vty 0 4
 transport input ssh
 login local
!
end
write memory"""
        self.config_text.delete(1.0, tk.END)
        self.config_text.insert(tk.END, template)
        self.update_line_numbers()
    
    def load_switch_template(self):
        """Charge un template de configuration pour switch L2"""
        template = """! Configuration de base pour switch L2
enable
configure terminal
hostname SWITCH
!
! Configuration des VLANs
vlan 10
 name VLAN10
!
vlan 20
 name VLAN20
!
vlan 99
 name MANAGEMENT
!
! Configuration des interfaces d'accès
interface range GigabitEthernet0/1-12
 switchport mode access
 switchport access vlan 10
 spanning-tree portfast
 no shutdown
!
interface range GigabitEthernet0/13-24
 switchport mode access
 switchport access vlan 20
 spanning-tree portfast
 no shutdown
!
! Configuration du trunk
interface GigabitEthernet0/0
 switchport trunk encapsulation dot1q
 switchport mode trunk
 switchport trunk native vlan 99
 switchport trunk allowed vlan 10,20,99
 no shutdown
!
! Configuration de l'interface de management
interface Vlan99
 ip address 192.168.99.1 255.255.255.0
 no shutdown
!
ip default-gateway 192.168.99.254
!
spanning-tree mode rapid-pvst
spanning-tree vlan 1,10,20,99 priority 4096
!
end
write memory"""
        self.config_text.delete(1.0, tk.END)
        self.config_text.insert(tk.END, template)
        self.update_line_numbers()
    
    def load_firewall_template(self):
        """Charge un template de configuration pour pare-feu ASA"""
        template = """! Configuration de base pour ASA
enable
configure terminal
hostname ASA-FIREWALL
!
! Configuration des interfaces
interface GigabitEthernet0/0
 nameif INSIDE
 security-level 100
 ip address 192.168.1.1 255.255.255.0
 no shutdown
!
interface GigabitEthernet0/1
 nameif OUTSIDE
 security-level 0
 ip address 10.0.0.1 255.255.255.252
 no shutdown
!
! Configuration NAT
object network INSIDE-NET
 subnet 192.168.1.0 255.255.255.0
 nat (INSIDE,OUTSIDE) dynamic interface
!
! Règles d'accès
access-list OUTSIDE-IN extended permit icmp any any
access-list OUTSIDE-IN extended permit tcp any any eq www
access-list OUTSIDE-IN extended permit tcp any any eq 443
access-group OUTSIDE-IN in interface OUTSIDE
!
! Configuration SSH
aaa authentication ssh console LOCAL
username admin password cisco123 privilege 15
crypto key generate rsa modulus 2048
ssh 192.168.1.0 255.255.255.0 INSIDE
ssh timeout 30
!
end
write memory"""
        self.config_text.delete(1.0, tk.END)
        self.config_text.insert(tk.END, template)
        self.update_line_numbers()
    
    def load_ip_template(self):
        """Charge un template de configuration IP de base"""
        template = """! Configuration IP de base
enable
configure terminal
!
! Configuration des interfaces
interface GigabitEthernet0/0
 ip address 192.168.1.1 255.255.255.0
 no shutdown
!
interface GigabitEthernet0/1
 ip address 192.168.2.1 255.255.255.0
 no shutdown
!
! Configuration DNS
ip name-server 8.8.8.8
ip name-server 8.8.4.4
!
! Test de connectivité
do ping 8.8.8.8
!
end
write memory"""
        self.config_text.delete(1.0, tk.END)
        self.config_text.insert(tk.END, template)
        self.update_line_numbers()
    
    def load_ospf_template(self):
        """Charge un template de configuration OSPF"""
        template = """! Configuration OSPF
enable
configure terminal
!
router ospf 1
 network 192.168.1.0 0.0.0.255 area 0
 network 192.168.2.0 0.0.0.255 area 0
!
! Configuration des interfaces OSPF
interface GigabitEthernet0/0
 ip ospf cost 10
 ip ospf hello-interval 5
!
interface GigabitEthernet0/1
 ip ospf cost 20
 ip ospf hello-interval 5
!
! Redistribution de route par défaut
default-information originate
!
end
write memory"""
        self.config_text.delete(1.0, tk.END)
        self.config_text.insert(tk.END, template)
        self.update_line_numbers()
    
    def load_vlan_template(self):
        """Charge un template de configuration VLAN"""
        template = """! Configuration VLAN et Trunking
enable
configure terminal
!
! Création des VLANs
vlan 10
 name SALES
!
vlan 20
 name ENGINEERING
!
vlan 30
 name ADMIN
!
vlan 99
 name NATIVE
!
! Configuration des interfaces d'accès
interface GigabitEthernet1/0/1
 switchport mode access
 switchport access vlan 10
 spanning-tree portfast
 no shutdown
!
interface GigabitEthernet1/0/2
 switchport mode access
 switchport access vlan 20
 spanning-tree portfast
 no shutdown
!
! Configuration du trunk
interface GigabitEthernet1/0/24
 switchport trunk encapsulation dot1q
 switchport mode trunk
 switchport trunk native vlan 99
 switchport trunk allowed vlan 10,20,30,99
 no shutdown
!
! Vérification
do show vlan brief
do show interfaces trunk
!
end
write memory"""
        self.config_text.delete(1.0, tk.END)
        self.config_text.insert(tk.END, template)
        self.update_line_numbers()
    
    def update_line_numbers(self, event=None):
        """Met à jour les numéros de ligne"""
        self.line_numbers.config(state="normal")
        self.line_numbers.delete(1.0, tk.END)
        
        line_count = self.config_text.get("1.0", "end-1c").count("\n") + 1
        line_numbers_text = "\n".join(str(i) for i in range(1, line_count + 1))
        
        self.line_numbers.insert(1.0, line_numbers_text)
        self.line_numbers.config(state="disabled")
    
    def validate_config(self):
        """Valide la syntaxe de la configuration"""
        config_text = self.config_text.get(1.0, tk.END).strip()
        
        if not config_text:
            messagebox.showinfo("Validation", "La configuration est vide.")
            return
        
        # Vérifications basiques
        issues = []
        
        # Vérifier les commandes communes
        lines = config_text.split('\n')
        for i, line in enumerate(lines, 1):
            line = line.strip()
            
            if line.startswith("!"):
                continue  # Commentaire, ignorer
            
            # Vérifications spécifiques
            if "interface " in line and "no shutdown" not in "\n".join(lines[i:]):
                # On vérifie si no shutdown est présent plus loin
                found = False
                for j in range(i, min(i+10, len(lines))):
                    if "no shutdown" in lines[j]:
                        found = True
                        break
                if not found:
                    issues.append(f"Ligne {i}: Interface sans 'no shutdown'")
            
            if line.startswith("ip address") and "/" not in line and "255.255.255" not in line:
                issues.append(f"Ligne {i}: Format d'adresse IP incorrect")
        
        # Afficher les résultats
        if issues:
            result = "Problèmes détectés:\n\n" + "\n".join(issues)
            messagebox.showwarning("Validation", result)
        else:
            messagebox.showinfo("Validation", "✅ Configuration syntaxiquement valide")
    
    def show_device_info(self):
        """Affiche les informations de l'équipement sélectionné"""
        device = self.config_device_combo.get()
        if not device:
            messagebox.showwarning("Aucune sélection", "Veuillez sélectionner un équipement.")
            return
        
        if device in self.nodes:
            node_info = self.nodes[device]
            info_text = f"""Équipement: {device}
Type: {node_info['type']}
Catégorie: {node_info.get('category', 'Non définie')}

Description:
{self.device_descriptions.get(node_info['type'], 'Description non disponible')}"""
            
            messagebox.showinfo(f"Informations - {device}", info_text)
        else:
            messagebox.showerror("Erreur", f"Équipement '{device}' non trouvé dans la topologie.")
    
    def test_configuration(self):
        """Teste la configuration sans l'appliquer"""
        config_text = self.config_text.get(1.0, tk.END).strip()
        
        if not config_text:
            messagebox.showwarning("Configuration vide", "Aucune configuration à tester.")
            return
        
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, "=== TEST DE CONFIGURATION ===\n\n")
        
        # Simulation simple des effets de la configuration
        lines = config_text.split('\n')
        for line in lines:
            line = line.strip()
            if not line or line.startswith("!"):
                continue
            
            if "hostname" in line:
                self.output_text.insert(tk.END, f"✓ Changement de nom d'hôte\n")
            elif "interface" in line:
                self.output_text.insert(tk.END, f"✓ Configuration d'interface\n")
            elif "ip address" in line:
                self.output_text.insert(tk.END, f"✓ Attribution d'adresse IP\n")
            elif "no shutdown" in line:
                self.output_text.insert(tk.END, f"✓ Activation d'interface\n")
            elif "router ospf" in line:
                self.output_text.insert(tk.END, f"✓ Configuration OSPF\n")
            elif "vlan" in line:
                self.output_text.insert(tk.END, f"✓ Création/modification de VLAN\n")
        
        self.output_text.insert(tk.END, "\n✅ Test terminé - Configuration prête à être appliquée")
        self.update_status("Test de configuration terminé")
    
    def export_logs(self):
        """Exporte les logs de configuration"""
        logs = self.output_text.get(1.0, tk.END).strip()
        
        if not logs:
            messagebox.showwarning("Logs vides", "Aucun log à exporter.")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".log",
            filetypes=[("Log files", "*.log"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    f.write(logs)
                self.update_status(f"Logs exportés vers {file_path}")
                messagebox.showinfo("Succès", f"Logs exportés vers {file_path}")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de l'export: {str(e)}")
    
    # ===== MÉTHODES POUR LA CONFIGURATION =====
    
    def clear_config_text(self):
        """Efface le texte de configuration"""
        self.config_text.delete(1.0, tk.END)
        self.update_line_numbers()
    
    def apply_configuration(self):
        """Applique la configuration à l'équipement sélectionné"""
        device = self.config_device_combo.get()
        config_text = self.config_text.get(1.0, tk.END).strip()
        
        if not device:
            messagebox.showerror("Erreur", "Veuillez sélectionner un équipement.")
            return
        
        if not config_text:
            messagebox.showwarning("Configuration vide", "La configuration est vide.")
            return
        
        # Vérifier la connexion CML
        if not self.connect_to_cml():
            return
        
        # Exécuter dans un thread séparé
        thread = threading.Thread(target=self._apply_config_thread, 
                                 args=(device, config_text))
        thread.daemon = True
        thread.start()
    
    def _apply_config_thread(self, device_name, config_text):
        """Thread pour appliquer la configuration"""
        try:
            self.update_status(f"Configuration de {device_name}...")
            self.output_text.insert(tk.END, f"\n=== Configuration de {device_name} ===\n")
            
            if not self.lab:
                self.output_text.insert(tk.END, "✗ Aucun lab actif. Veuillez d'abord créer un lab.\n")
                return
            
            # Établir la connexion console
            connection = self.connect_to_device_console(device_name)
            if not connection:
                self.output_text.insert(tk.END, f"✗ Échec de connexion à {device_name}\n")
                return
            
            # Diviser les commandes
            commands = [cmd.strip() for cmd in config_text.split('\n') if cmd.strip()]
            
            # Appliquer les commandes
            for cmd in commands:
                if cmd.startswith("!"):
                    continue  # Ignorer les commentaires
                
                output = self.send_command_raw(connection, cmd)
                self.output_text.insert(tk.END, f"\n{cmd}")
                self.output_text.insert(tk.END, f"\n{output[:200]}...\n")  # Limiter la sortie
                self.output_text.see(tk.END)
                time.sleep(0.5)
            
            # Sauvegarder la configuration
            self.send_command_raw(connection, "write memory", wait_time=2)
            
            self.output_text.insert(tk.END, f"\n✓ Configuration de {device_name} terminée\n")
            self.update_status(f"Configuration de {device_name} terminée")
            
            connection.disconnect()
            
        except Exception as e:
            error_msg = f"✗ Erreur lors de la configuration: {str(e)}\n"
            self.output_text.insert(tk.END, error_msg)
            self.output_text.see(tk.END)
            self.update_status(f"Erreur: {str(e)}")
    
    def send_command_raw(self, connection, command, wait_time=1.0):
        """Envoie une commande brute à l'équipement"""
        connection.write_channel(command + '\r')
        time.sleep(wait_time)
        output = connection.read_channel()
        return output
    
    def connect_to_device_console(self, device_name):
        """Établit une connexion console vers un équipement"""
        try:
            # Récupérer les identifiants
            device_user = self.device_user_entry.get() if hasattr(self, 'device_user_entry') else "cisco"
            device_pass = self.device_pass_entry.get() if hasattr(self, 'device_pass_entry') else "cisco"
            
            connection = ConnectHandler(
                device_type='terminal_server',
                host=self.cml_config["controller"],
                username=self.cml_config["username"],
                password=self.cml_config["password"],
                session_timeout=120,
            )

            # Initialisation
            connection.write_channel('\r')
            time.sleep(1)
            
            # Connexion à la console
            connection.write_channel(f'open /{self.lab.title}/{device_name}/0\r')
            time.sleep(3)

            output = connection.read_channel()
            
            # Authentification
            connection.write_channel('\r')
            time.sleep(1)
            connection.write_channel(device_user + '\r')
            time.sleep(1)
            connection.write_channel(device_pass + '\r')
            time.sleep(2)
            
            output += connection.read_channel()

            if '>' in output or '#' in output:
                return connection
            else:
                self.output_text.insert(tk.END, f"\n✗ Connexion échouée: {output[:100]}...\n")
                return None
                
        except Exception as e:
            self.output_text.insert(tk.END, f"\n✗ Erreur de connexion: {str(e)}\n")
            return None
    
    def clear_output(self):
        """Efface la zone de sortie"""
        self.output_text.delete(1.0, tk.END)
    
    def load_config_file(self):
        """Charge une configuration depuis un fichier"""
        file_path = filedialog.askopenfilename(
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    config_text = f.read()
                self.config_text.delete(1.0, tk.END)
                self.config_text.insert(tk.END, config_text)
                self.update_status(f"Configuration chargée depuis {file_path}")
                self.update_line_numbers()
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors du chargement: {str(e)}")
    
    def save_config_file(self):
        """Sauvegarde la configuration dans un fichier"""
        config_text = self.config_text.get(1.0, tk.END).strip()
        if not config_text:
            messagebox.showwarning("Configuration vide", "La configuration est vide.")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    f.write(config_text)
                self.update_status(f"Configuration sauvegardée dans {file_path}")
                messagebox.showinfo("Succès", f"Configuration sauvegardée dans {file_path}")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de la sauvegarde: {str(e)}")
    
    def refresh_device_list(self):
        """Actualise la liste des équipements"""
        if not self.lab:
            messagebox.showerror("Erreur", "Aucun lab actif. Veuillez d'abord créer un lab.")
            return
        
        try:
            devices = [node.label for node in self.lab.nodes()]
            self.config_device_combo['values'] = devices
            self.test_device_combo['values'] = devices
            
            if devices:
                self.config_device_combo.set(devices[0])
                self.test_device_combo.set(devices[0])
            
            self.update_status(f"Liste d'équipements actualisée: {len(devices)} équipement(s)")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'actualisation: {str(e)}")
    
    # ===== MÉTHODES POUR LES TESTS =====
    
    def run_standard_test(self):
        """Exécute un test standard"""
        device = self.test_device_combo.get()
        test_type = self.test_type_combo.get()
        
        if not device:
            messagebox.showerror("Erreur", "Veuillez sélectionner un équipement.")
            return
        
        # Construire la commande
        if test_type == "Ping":
            ip = self.ping_ip_entry.get()
            command = f"ping {ip}"
        elif test_type == "Show running-config":
            command = "show running-config"
        elif test_type == "Show interfaces":
            command = "show interfaces"
        elif test_type == "Show version":
            command = "show version"
        elif test_type == "Show IP route":
            command = "show ip route"
        elif test_type == "Show VLAN":
            command = "show vlan"
        else:
            command = test_type
        
        self._execute_test_command(device, command)
    
    def run_custom_test(self):
        """Exécute une commande personnalisée"""
        device = self.test_device_combo.get()
        command = self.custom_cmd_entry.get().strip()
        
        if not device:
            messagebox.showerror("Erreur", "Veuillez sélectionner un équipement.")
            return
        
        if not command:
            messagebox.showwarning("Commande vide", "Veuillez entrer une commande.")
            return
        
        self._execute_test_command(device, command)
    
    def _execute_test_command(self, device, command):
        """Exécute une commande de test"""
        if not self.connect_to_cml() or not self.lab:
            self.test_output.insert(tk.END, "✗ Aucun lab actif. Veuillez d'abord créer un lab.\n")
            return
        
        thread = threading.Thread(target=self._execute_test_thread, 
                                 args=(device, command))
        thread.daemon = True
        thread.start()
    
    def _execute_test_thread(self, device, command):
        """Thread pour exécuter les tests"""
        try:
            self.test_output.insert(tk.END, f"\n=== Test: {device} ===\n")
            self.test_output.insert(tk.END, f"Commande: {command}\n")
            self.test_output.insert(tk.END, "-" * 50 + "\n")
            
            connection = self.connect_to_device_console(device)
            if not connection:
                self.test_output.insert(tk.END, "✗ Échec de connexion\n")
                return
            
            # Exécuter la commande
            output = self.send_command_raw(connection, command, wait_time=3)
            self.test_output.insert(tk.END, output + "\n")
            self.test_output.see(tk.END)
            
            connection.disconnect()
            self.test_output.insert(tk.END, "✓ Test terminé\n")
            
        except Exception as e:
            self.test_output.insert(tk.END, f"✗ Erreur: {str(e)}\n")
    
    def clear_test_results(self):
        """Efface les résultats des tests"""
        self.test_output.delete(1.0, tk.END)
    
    def export_test_results(self):
        """Exporte les résultats des tests"""
        results = self.test_output.get(1.0, tk.END).strip()
        if not results:
            messagebox.showwarning("Résultats vides", "Aucun résultat à exporter.")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    f.write(results)
                messagebox.showinfo("Succès", f"Résultats exportés vers {file_path}")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de l'export: {str(e)}")
    
    # ===== MÉTHODES POUR LES PARAMÈTRES =====
    
    def save_settings(self):
        """Sauvegarde les paramètres"""
        self.cml_config = {
            "controller": self.controller_entry.get(),
            "username": self.username_entry.get(),
            "password": self.password_entry.get(),
            "lab_name": self.lab_name_entry.get()
        }
        
        try:
            with open("cml_settings.json", "w") as f:
                json.dump(self.cml_config, f, indent=4)
            self.update_status("Paramètres sauvegardés")
            messagebox.showinfo("Succès", "Paramètres sauvegardés.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur sauvegarde: {str(e)}")
    
    def test_cml_connection(self):
        """Teste la connexion à CML"""
        try:
            client = ClientLibrary(
                f"https://{self.controller_entry.get()}",
                self.username_entry.get(),
                self.password_entry.get(),
                ssl_verify=False
            )
            
            labs = list(client.all_labs())
            messagebox.showinfo("Succès", f"Connexion CML réussie!\n{len(labs)} labs trouvés.")
            self.update_status("Connexion CML testée avec succès")
        except Exception as e:
            messagebox.showerror("Échec", f"Échec connexion CML:\n{str(e)}")
    
    def reset_settings(self):
        """Réinitialise les paramètres"""
        if messagebox.askyesno("Confirmation", "Réinitialiser tous les paramètres?"):
            self.cml_config = {
                "controller": "10.10.20.161",
                "username": "developer",
                "password": "C1sco12345",
                "lab_name": "CML Automation Lab"
            }
            
            self.controller_entry.delete(0, tk.END)
            self.controller_entry.insert(0, self.cml_config["controller"])
            self.username_entry.delete(0, tk.END)
            self.username_entry.insert(0, self.cml_config["username"])
            self.password_entry.delete(0, tk.END)
            self.password_entry.insert(0, self.cml_config["password"])
            self.lab_name_entry.delete(0, tk.END)
            self.lab_name_entry.insert(0, self.cml_config["lab_name"])
            
            self.device_user_entry.delete(0, tk.END)
            self.device_user_entry.insert(0, "cisco")
            self.device_pass_entry.delete(0, tk.END)
            self.device_pass_entry.insert(0, "cisco")
            
            self.update_status("Paramètres réinitialisés")
    
    def load_config(self):
        """Charge la configuration"""
        try:
            if os.path.exists("cml_settings.json"):
                with open("cml_settings.json", "r") as f:
                    saved_config = json.load(f)
                    self.cml_config.update(saved_config)
                    
                    if hasattr(self, 'controller_entry'):
                        self.controller_entry.delete(0, tk.END)
                        self.controller_entry.insert(0, self.cml_config["controller"])
                        self.username_entry.delete(0, tk.END)
                        self.username_entry.insert(0, self.cml_config["username"])
                        self.password_entry.delete(0, tk.END)
                        self.password_entry.insert(0, self.cml_config["password"])
                        self.lab_name_entry.delete(0, tk.END)
                        self.lab_name_entry.insert(0, self.cml_config["lab_name"])
        except:
            pass
    
    # ===== MÉTHODES POUR LE LAB =====
    
    def create_and_start_lab(self):
        """Crée et démarre le lab dans CML"""
        if not self.nodes:
            messagebox.showerror("Erreur", "Aucun équipement défini. Veuillez ajouter des équipements.")
            return
        
        if not self.connect_to_cml():
            return
        
        thread = threading.Thread(target=self.cleanup_and_create_lab)
        thread.daemon = True
        thread.start()
    
    def cleanup_and_create_lab(self):
        """Nettoyage et création du lab (thread)"""
        try:
            self.update_status("Nettoyage des labs existants...")
            lab_name = self.lab_name_entry.get()
            
            # Nettoyer les labs existants avec le même nom
            for existing_lab in self.cml_client.all_labs():
                if existing_lab.title == lab_name:
                    if existing_lab.state == 'STARTED':
                        existing_lab.stop()
                        while existing_lab.state != 'STOPPED':
                            time.sleep(5)
                    existing_lab.wipe()
                    existing_lab.remove()
            
            self.update_status("Création du lab...")
            
            # Créer le lab
            self.lab = self.cml_client.create_lab(lab_name)
            
            # Créer les nœuds
            for node_name, node_info in self.nodes.items():
                self.lab.create_node(node_name, node_info["type"])
                time.sleep(0.5)
            
            # Créer les connexions
            for conn in self.connections:
                try:
                    source_node = self.lab.get_node_by_label(conn["source"])
                    dest_node = self.lab.get_node_by_label(conn["dest"])
                    
                    if source_node and dest_node:
                        self.lab.create_link(
                            self.lab.create_interface(source_node, conn["port_s"]),
                            self.lab.create_interface(dest_node, conn["port_d"])
                        )
                        time.sleep(0.5)
                except Exception as e:
                    self.update_status(f"Erreur connexion {conn['source']}-{conn['dest']}: {str(e)}")
            
            self.update_status("Démarrage du lab...")
            
            # Démarrer le lab
            self.lab.start()
            time.sleep(60)  # Attendre le démarrage
            
            self.update_status(f"Lab '{lab_name}' créé et démarré avec succès")
            messagebox.showinfo("Succès", f"Lab '{lab_name}' créé et démarré avec succès!")
            
        except Exception as e:
            self.update_status(f"Erreur: {str(e)}")
            messagebox.showerror("Erreur", f"Erreur lors de la création du lab: {str(e)}")
    
    def stop_lab(self):
        """Arrête le lab actif"""
        if not self.lab:
            messagebox.showerror("Erreur", "Aucun lab actif.")
            return
        
        try:
            self.lab.stop()
            self.update_status("Lab arrêté")
            messagebox.showinfo("Succès", "Lab arrêté avec succès.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'arrêt: {str(e)}")
    
    def delete_lab(self):
        """Supprime le lab actif"""
        if not self.lab:
            messagebox.showerror("Erreur", "Aucun lab actif.")
            return
        
        if messagebox.askyesno("Confirmation", "Êtes-vous sûr de vouloir supprimer le lab?"):
            try:
                self.lab.wipe()
                self.lab.remove()
                self.lab = None
                self.update_status("Lab supprimé")
                messagebox.showinfo("Succès", "Lab supprimé avec succès.")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de la suppression: {str(e)}")
    
    def export_topology(self):
        """Exporte la topologie dans un fichier JSON"""
        topology = {
            "nodes": self.nodes,
            "connections": self.connections,
            "lab_name": self.lab_name_entry.get()
        }
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    json.dump(topology, f, indent=4)
                self.update_status(f"Topologie exportée vers {file_path}")
                messagebox.showinfo("Succès", f"Topologie exportée vers {file_path}")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de l'export: {str(e)}")
    
    def import_topology(self):
        """Importe une topologie depuis un fichier JSON"""
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    topology = json.load(f)
                
                # Mettre à jour les données
                self.nodes = topology.get("nodes", {})
                self.connections = topology.get("connections", [])
                
                # Mettre à jour les combobox
                device_names = list(self.nodes.keys())
                self.source_device_combo['values'] = device_names
                self.dest_device_combo['values'] = device_names
                self.config_device_combo['values'] = device_names
                self.test_device_combo['values'] = device_names
                
                # Mettre à jour l'arbre des connexions
                self.connections_tree.delete(*self.connections_tree.get_children())
                for conn in self.connections:
                    self.connections_tree.insert("", tk.END, 
                                               values=(conn["source"], conn["port_s"], 
                                                      conn["dest"], conn["port_d"]))
                
                # Mettre à jour le nom du lab
                if "lab_name" in topology:
                    self.lab_name_entry.delete(0, tk.END)
                    self.lab_name_entry.insert(0, topology["lab_name"])
                
                self.update_status(f"Topologie importée depuis {file_path}")
                self.refresh_visualization()
                messagebox.showinfo("Succès", f"Topologie importée depuis {file_path}")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de l'import: {str(e)}")
    
    def connect_to_cml(self):
        """Établit la connexion à CML"""
        try:
            if not self.cml_client:
                self.cml_client = ClientLibrary(
                    f"https://{self.cml_config['controller']}",
                    self.cml_config["username"],
                    self.cml_config["password"],
                    ssl_verify=False
                )
            return True
        except Exception as e:
            messagebox.showerror("Erreur de connexion", 
                               f"Impossible de se connecter à CML:\n{str(e)}")
            return False
    
    def update_status(self, message):
        """Met à jour la barre de statut"""
        self.status_bar.config(text=f"Statut: {message}")
        self.root.update()

def main():
    root = tk.Tk()
    app = CMLAutomationApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()