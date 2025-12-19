import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import time
import threading
import json
import os
from virl2_client import ClientLibrary
from netmiko import ConnectHandler, NetmikoAuthenticationException

class CMLAutomationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CML2 Automation Tool")
        self.root.geometry("1200x800")
        
        # Variables pour stocker les données
        self.cml_client = None
        self.lab = None
        self.nodes = {}
        self.connections = []
        
        # Configuration CML2 par défaut
        self.cml_config = {
            "controller": "10.10.20.161",
            "username": "developer",
            "password": "C1sco12345",
            "lab_name": "CML Automation Lab"
        }
        
        # Types d'équipements disponibles
        self.device_types = [
            "iosvl2",  # Switch L2
            "iosv",    # Routeur
            "nxosv",   # Switch Nexus
            "desktop", # PC
            "server"   # Serveur
            "external_connector"
            "asav"
            "cat8000v"
            "csr1000v"
            "iol-xe"
            "alpine"
            "trex"
            "ubuntu"
            "vwlc"
            "wan_emulator"
            "ioll2-xe"
            "iosvl2"
            "unmanaged_switch"
        ]
        
        # Équipements prédéfinis
        self.predefined_devices = [
            {"name": "Router1", "type": "iosv"},
            {"name": "Router2", "type": "iosv"},
            {"name": "Switch1", "type": "iosvl2"},
            {"name": "Switch2", "type": "iosvl2"},
            {"name": "PC1", "type": "desktop"},
            {"name": "PC2", "type": "desktop"},
            {"name": "Server1", "type": "server"}
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
        # Frame pour l'ajout d'équipements
        frame_devices = ttk.LabelFrame(self.tab_topology, text="Gestion des Équipements", padding=10)
        frame_devices.pack(fill=tk.X, padx=10, pady=5)
        
        # Liste des équipements disponibles
        ttk.Label(frame_devices, text="Équipements prédéfinis:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.device_listbox = tk.Listbox(frame_devices, height=8, selectmode=tk.MULTIPLE)
        self.device_listbox.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        for device in self.predefined_devices:
            self.device_listbox.insert(tk.END, f"{device['name']} ({device['type']})")
        
        # Boutons pour la liste
        btn_frame = ttk.Frame(frame_devices)
        btn_frame.grid(row=2, column=0, columnspan=3, pady=5)
        
        ttk.Button(btn_frame, text="Ajouter sélection", 
                  command=self.add_selected_devices).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Tout sélectionner",
                  command=self.select_all_devices).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Tout désélectionner",
                  command=self.deselect_all_devices).pack(side=tk.LEFT, padx=5)
        
        # Ajout manuel d'équipement
        ttk.Label(frame_devices, text="Ajouter un équipement personnalisé:").grid(row=3, column=0, sticky=tk.W, pady=(10, 5))
        
        ttk.Label(frame_devices, text="Nom:").grid(row=4, column=0, sticky=tk.W, padx=5)
        self.device_name_entry = ttk.Entry(frame_devices, width=20)
        self.device_name_entry.grid(row=4, column=1, sticky=tk.W, padx=5)
        
        ttk.Label(frame_devices, text="Type:").grid(row=4, column=2, sticky=tk.W, padx=5)
        self.device_type_combo = ttk.Combobox(frame_devices, values=self.device_types, width=15)
        self.device_type_combo.grid(row=4, column=3, sticky=tk.W, padx=5)
        self.device_type_combo.set("iosvl2")
        
        ttk.Button(frame_devices, text="Ajouter", 
                  command=self.add_custom_device).grid(row=4, column=4, padx=10)
        
        # Frame pour les connexions
        frame_connections = ttk.LabelFrame(self.tab_topology, text="Connexions des Équipements", padding=10)
        frame_connections.pack(fill=tk.X, padx=10, pady=10)
        
        # Sélection des équipements à connecter
        ttk.Label(frame_connections, text="Équipement source:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.source_device_combo = ttk.Combobox(frame_connections, width=20)
        self.source_device_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(frame_connections, text="Port source:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.source_port_entry = ttk.Entry(frame_connections, width=10)
        self.source_port_entry.grid(row=0, column=3, sticky=tk.W, padx=5, pady=5)
        self.source_port_entry.insert(0, "0")
        
        ttk.Label(frame_connections, text="Équipement destination:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.dest_device_combo = ttk.Combobox(frame_connections, width=20)
        self.dest_device_combo.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(frame_connections, text="Port destination:").grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        self.dest_port_entry = ttk.Entry(frame_connections, width=10)
        self.dest_port_entry.grid(row=1, column=3, sticky=tk.W, padx=5, pady=5)
        self.dest_port_entry.insert(0, "0")
        
        ttk.Button(frame_connections, text="Ajouter connexion",
                  command=self.add_connection).grid(row=1, column=4, padx=10)
        
        # Liste des connexions
        ttk.Label(frame_connections, text="Connexions établies:").grid(row=2, column=0, sticky=tk.W, pady=(10, 5))
        
        self.connections_tree = ttk.Treeview(frame_connections, 
                                            columns=("Source", "PortS", "Dest", "PortD"), 
                                            height=6, show="headings")
        self.connections_tree.grid(row=3, column=0, columnspan=5, sticky=(tk.W, tk.E), pady=5)
        
        self.connections_tree.heading("Source", text="Source")
        self.connections_tree.heading("PortS", text="Port Source")
        self.connections_tree.heading("Dest", text="Destination")
        self.connections_tree.heading("PortD", text="Port Dest")
        
        self.connections_tree.column("Source", width=150)
        self.connections_tree.column("PortS", width=80)
        self.connections_tree.column("Dest", width=150)
        self.connections_tree.column("PortD", width=80)
        
        # Bouton pour supprimer une connexion
        ttk.Button(frame_connections, text="Supprimer connexion sélectionnée",
                  command=self.delete_connection).grid(row=4, column=0, pady=5)
        
        # Frame pour les actions du labo
        frame_actions = ttk.LabelFrame(self.tab_topology, text="Actions du Labo", padding=10)
        frame_actions.pack(fill=tk.X, padx=10, pady=10)
        
        btn_action_frame = ttk.Frame(frame_actions)
        btn_action_frame.pack()
        
        ttk.Button(btn_action_frame, text="Créer et démarrer le labo",
                  command=self.create_and_start_lab).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_action_frame, text="Arrêter le labo",
                  command=self.stop_lab).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_action_frame, text="Supprimer le labo",
                  command=self.delete_lab).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_action_frame, text="Exporter topologie",
                  command=self.export_topology).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_action_frame, text="Importer topologie",
                  command=self.import_topology).pack(side=tk.LEFT, padx=5)
    
    def setup_configuration_tab(self):
        # Frame pour la sélection de l'équipement
        frame_select = ttk.LabelFrame(self.tab_config, text="Sélection de l'Équipement", padding=10)
        frame_select.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(frame_select, text="Équipement à configurer:").pack(side=tk.LEFT, padx=5)
        self.config_device_combo = ttk.Combobox(frame_select, width=30)
        self.config_device_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(frame_select, text="Actualiser la liste",
                  command=self.refresh_device_list).pack(side=tk.LEFT, padx=10)
        
        # Frame pour l'édition de configuration
        frame_edit = ttk.LabelFrame(self.tab_config, text="Édition de Configuration", padding=10)
        frame_edit.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Zone de texte pour les commandes
        ttk.Label(frame_edit, text="Commandes de configuration (une par ligne):").pack(anchor=tk.W)
        
        self.config_text = scrolledtext.ScrolledText(frame_edit, height=15, wrap=tk.WORD)
        self.config_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Exemples de configuration préchargés
        example_config = """enable
configure terminal
hostname Router1
interface GigabitEthernet0/0
 ip address 192.168.1.1 255.255.255.0
 no shutdown
exit
router ospf 1
 network 192.168.1.0 0.0.0.255 area 0
exit"""
        self.config_text.insert(tk.END, example_config)
        
        # Boutons pour la configuration
        btn_frame = ttk.Frame(frame_edit)
        btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(btn_frame, text="Charger configuration exemple",
                  command=self.load_example_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Effacer",
                  command=self.clear_config_text).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Sauvegarder configuration",
                  command=self.save_config_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Charger configuration fichier",
                  command=self.load_config_file).pack(side=tk.LEFT, padx=5)
        
        # Frame pour l'exécution
        frame_execute = ttk.LabelFrame(self.tab_config, text="Exécution", padding=10)
        frame_execute.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Bouton d'exécution
        ttk.Button(frame_execute, text="Appliquer la configuration",
                  command=self.apply_configuration).pack(pady=5)
        
        # Zone de sortie
        ttk.Label(frame_execute, text="Sortie de la configuration:").pack(anchor=tk.W)
        
        self.output_text = scrolledtext.ScrolledText(frame_execute, height=10, wrap=tk.WORD)
        self.output_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Bouton pour effacer la sortie
        ttk.Button(frame_execute, text="Effacer la sortie",
                  command=self.clear_output).pack(pady=5)
    
    def setup_test_tab(self):
        # Frame pour la sélection du test
        frame_select = ttk.LabelFrame(self.tab_test, text="Sélection du Test", padding=10)
        frame_select.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(frame_select, text="Équipement à tester:").pack(side=tk.LEFT, padx=5)
        self.test_device_combo = ttk.Combobox(frame_select, width=30)
        self.test_device_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(frame_select, text="Commande de test:").pack(side=tk.LEFT, padx=5)
        self.test_command_combo = ttk.Combobox(frame_select, 
                                              values=["ping", "show running-config", "show interfaces", 
                                                     "show ip route", "show version", "show vlan"],
                                              width=20)
        self.test_command_combo.pack(side=tk.LEFT, padx=5)
        self.test_command_combo.set("ping")
        
        # Frame pour les paramètres du test
        frame_params = ttk.LabelFrame(self.tab_test, text="Paramètres du Test", padding=10)
        frame_params.pack(fill=tk.X, padx=10, pady=5)
        
        # Pour ping
        self.ping_frame = ttk.Frame(frame_params)
        self.ping_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(self.ping_frame, text="Adresse IP:").pack(side=tk.LEFT, padx=5)
        self.ping_ip_entry = ttk.Entry(self.ping_frame, width=20)
        self.ping_ip_entry.pack(side=tk.LEFT, padx=5)
        self.ping_ip_entry.insert(0, "192.168.1.1")
        
        ttk.Label(self.ping_frame, text="Nombre de paquets:").pack(side=tk.LEFT, padx=5)
        self.ping_count_entry = ttk.Entry(self.ping_frame, width=10)
        self.ping_count_entry.pack(side=tk.LEFT, padx=5)
        self.ping_count_entry.insert(0, "5")
        
        # Frame pour la commande personnalisée
        frame_custom = ttk.LabelFrame(self.tab_test, text="Commande Personnalisée", padding=10)
        frame_custom.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(frame_custom, text="Commande:").pack(anchor=tk.W)
        self.custom_command_entry = ttk.Entry(frame_custom, width=50)
        self.custom_command_entry.pack(fill=tk.X, pady=5)
        
        # Boutons d'exécution
        btn_frame = ttk.Frame(self.tab_test)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(btn_frame, text="Exécuter test standard",
                  command=self.run_standard_test).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Exécuter commande personnalisée",
                  command=self.run_custom_test).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Tester la connectivité",
                  command=self.run_connectivity_test).pack(side=tk.LEFT, padx=5)
        
        # Frame pour les résultats
        frame_results = ttk.LabelFrame(self.tab_test, text="Résultats des Tests", padding=10)
        frame_results.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.test_output_text = scrolledtext.ScrolledText(frame_results, height=15, wrap=tk.WORD)
        self.test_output_text.pack(fill=tk.BOTH, expand=True)
        
        # Boutons pour les résultats
        result_btn_frame = ttk.Frame(frame_results)
        result_btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(result_btn_frame, text="Effacer les résultats",
                  command=self.clear_test_results).pack(side=tk.LEFT, padx=5)
        ttk.Button(result_btn_frame, text="Sauvegarder résultats",
                  command=self.save_test_results).pack(side=tk.LEFT, padx=5)
        ttk.Button(result_btn_frame, text="Exporter tous les tests",
                  command=self.export_all_tests).pack(side=tk.LEFT, padx=5)
    
    def setup_settings_tab(self):
        # Frame pour les paramètres CML
        frame_cml = ttk.LabelFrame(self.tab_settings, text="Paramètres CML2", padding=10)
        frame_cml.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(frame_cml, text="Contrôleur CML2:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.controller_entry = ttk.Entry(frame_cml, width=30)
        self.controller_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        self.controller_entry.insert(0, self.cml_config["controller"])
        
        ttk.Label(frame_cml, text="Nom d'utilisateur:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.username_entry = ttk.Entry(frame_cml, width=30)
        self.username_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        self.username_entry.insert(0, self.cml_config["username"])
        
        ttk.Label(frame_cml, text="Mot de passe:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.password_entry = ttk.Entry(frame_cml, width=30, show="*")
        self.password_entry.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        self.password_entry.insert(0, self.cml_config["password"])
        
        # Frame pour les paramètres du labo
        frame_lab = ttk.LabelFrame(self.tab_settings, text="Paramètres du Labo", padding=10)
        frame_lab.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(frame_lab, text="Nom du labo:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.lab_name_entry = ttk.Entry(frame_lab, width=30)
        self.lab_name_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        self.lab_name_entry.insert(0, self.cml_config["lab_name"])
        
        ttk.Label(frame_lab, text="Identifiants des équipements:").grid(row=1, column=0, sticky=tk.W, pady=5)
        
        cred_frame = ttk.Frame(frame_lab)
        cred_frame.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(cred_frame, text="Utilisateur:").pack(side=tk.LEFT)
        self.device_user_entry = ttk.Entry(cred_frame, width=15)
        self.device_user_entry.pack(side=tk.LEFT, padx=5)
        self.device_user_entry.insert(0, "cisco")
        
        ttk.Label(cred_frame, text="Mot de passe:").pack(side=tk.LEFT, padx=(10, 0))
        self.device_pass_entry = ttk.Entry(cred_frame, width=15, show="*")
        self.device_pass_entry.pack(side=tk.LEFT, padx=5)
        self.device_pass_entry.insert(0, "cisco")
        
        # Frame pour les boutons de gestion
        frame_manage = ttk.LabelFrame(self.tab_settings, text="Gestion", padding=10)
        frame_manage.pack(fill=tk.X, padx=10, pady=10)
        
        btn_frame = ttk.Frame(frame_manage)
        btn_frame.pack()
        
        ttk.Button(btn_frame, text="Sauvegarder paramètres",
                  command=self.save_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Charger paramètres",
                  command=self.load_settings_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Tester connexion CML",
                  command=self.test_cml_connection).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Réinitialiser",
                  command=self.reset_settings).pack(side=tk.LEFT, padx=5)
        
        # Informations sur l'application
        info_frame = ttk.LabelFrame(self.tab_settings, text="Informations", padding=10)
        info_frame.pack(fill=tk.X, padx=10, pady=10)
        
        info_text = """CML2 Automation Tool v1.0
Développé pour Cisco Modeling Labs 2
Fonctionnalités:
• Gestion de topologie réseau
• Configuration automatisée
• Tests de connectivité
• Export/Import de configurations
"""
        ttk.Label(info_frame, text=info_text, justify=tk.LEFT).pack()
    
    # ===== MÉTHODES POUR LA TOPOLOGIE =====
    
    def add_selected_devices(self):
        selected = self.device_listbox.curselection()
        if not selected:
            messagebox.showwarning("Aucune sélection", "Veuillez sélectionner au moins un équipement.")
            return
        
        for index in selected:
            device_str = self.device_listbox.get(index)
            device_name = device_str.split(" (")[0]
            device_type = device_str.split("(")[1].rstrip(")")
            
            self.source_device_combo['values'] = list(self.source_device_combo['values']) + [device_name]
            self.dest_device_combo['values'] = list(self.dest_device_combo['values']) + [device_name]
            self.config_device_combo['values'] = list(self.config_device_combo['values']) + [device_name]
            self.test_device_combo['values'] = list(self.test_device_combo['values']) + [device_name]
            
            self.nodes[device_name] = {"type": device_type, "interfaces": {}}
        
        self.update_status(f"{len(selected)} équipement(s) ajouté(s)")
    
    def select_all_devices(self):
        self.device_listbox.selection_set(0, tk.END)
    
    def deselect_all_devices(self):
        self.device_listbox.selection_clear(0, tk.END)
    
    def add_custom_device(self):
        name = self.device_name_entry.get().strip()
        dev_type = self.device_type_combo.get()
        
        if not name:
            messagebox.showerror("Erreur", "Veuillez entrer un nom pour l'équipement.")
            return
        
        if name in self.nodes:
            messagebox.showerror("Erreur", "Un équipement avec ce nom existe déjà.")
            return
        
        # Ajouter aux combobox
        self.source_device_combo['values'] = list(self.source_device_combo['values']) + [name]
        self.dest_device_combo['values'] = list(self.dest_device_combo['values']) + [name]
        self.config_device_combo['values'] = list(self.config_device_combo['values']) + [name]
        self.test_device_combo['values'] = list(self.test_device_combo['values']) + [name]
        
        self.nodes[name] = {"type": dev_type, "interfaces": {}}
        
        self.update_status(f"Équipement '{name}' ajouté")
        self.device_name_entry.delete(0, tk.END)
    
    def add_connection(self):
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
    
    def delete_connection(self):
        selected = self.connections_tree.selection()
        if not selected:
            messagebox.showwarning("Aucune sélection", "Veuillez sélectionner une connexion à supprimer.")
            return
        
        for item in selected:
            values = self.connections_tree.item(item)["values"]
            self.connections_tree.delete(item)
            
            # Supprimer de la liste
            for i, conn in enumerate(self.connections):
                if (conn["source"] == values[0] and conn["port_s"] == values[1] and
                    conn["dest"] == values[2] and conn["port_d"] == values[3]):
                    del self.connections[i]
                    break
        
        self.update_status("Connexion(s) supprimée(s)")
    
    def create_and_start_lab(self):
        if not self.nodes:
            messagebox.showerror("Erreur", "Aucun équipement défini. Veuillez ajouter des équipements.")
            return
        
        # Vérifier la connexion CML
        if not self.connect_to_cml():
            return
        
        # Nettoyer les labs existants
        thread = threading.Thread(target=self.cleanup_and_create_lab)
        thread.daemon = True
        thread.start()
    
    def cleanup_and_create_lab(self):
        try:
            self.update_status("Nettoyage des labs existants...")
            
            # Nettoyer les labs existants avec le même nom
            lab_name = self.lab_name_entry.get()
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
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    topology = json.load(f)
                
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
                
                self.lab_name_entry.delete(0, tk.END)
                self.lab_name_entry.insert(0, topology.get("lab_name", "Nouveau Lab"))
                
                self.update_status(f"Topologie importée depuis {file_path}")
                messagebox.showinfo("Succès", f"Topologie importée depuis {file_path}")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de l'import: {str(e)}")
    
    # ===== MÉTHODES POUR LA CONFIGURATION =====
    
    def refresh_device_list(self):
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
    
    def load_example_config(self):
        examples = {
            "Routeur": """enable
configure terminal
hostname Router1
interface GigabitEthernet0/0
 ip address 192.168.1.1 255.255.255.0
 no shutdown
exit
interface GigabitEthernet0/1
 ip address 192.168.2.1 255.255.255.0
 no shutdown
exit
router ospf 1
 network 192.168.1.0 0.0.0.255 area 0
 network 192.168.2.0 0.0.0.255 area 0
exit""",
            
            "Switch": """enable
configure terminal
hostname Switch1
vlan 10
 name VLAN10
exit
vlan 20
 name VLAN20
exit
interface range GigabitEthernet0/0-3
 switchport mode access
 switchport access vlan 10
 no shutdown
exit
interface range GigabitEthernet0/4-7
 switchport mode access
 switchport access vlan 20
 no shutdown
exit
interface GigabitEthernet0/24
 switchport mode trunk
 no shutdown
exit""",
            
            "PC": """enable
configure terminal
hostname PC1
interface GigabitEthernet0/0
 ip address dhcp
 no shutdown
exit
ip default-gateway 192.168.1.1"""
        }
        
        # Créer une fenêtre de sélection
        example_window = tk.Toplevel(self.root)
        example_window.title("Sélectionner un exemple")
        example_window.geometry("400x300")
        
        ttk.Label(example_window, text="Choisissez un exemple de configuration:").pack(pady=10)
        
        for name, config in examples.items():
            btn = ttk.Button(example_window, text=name,
                           command=lambda c=config, w=example_window: self.insert_example_config(c, w))
            btn.pack(pady=5)
    
    def insert_example_config(self, config, window):
        self.config_text.delete(1.0, tk.END)
        self.config_text.insert(tk.END, config)
        window.destroy()
        self.update_status("Exemple de configuration chargé")
    
    def clear_config_text(self):
        self.config_text.delete(1.0, tk.END)
    
    def save_config_file(self):
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
    
    def load_config_file(self):
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
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors du chargement: {str(e)}")
    
    def apply_configuration(self):
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
        try:
            self.update_status(f"Configuration de {device_name}...")
            
            # Établir la connexion console
            connection = self.connect_to_device_console(device_name)
            if not connection:
                self.output_text.insert(tk.END, f"\n✗ Échec de connexion à {device_name}\n")
                return
            
            # Diviser les commandes
            commands = [cmd.strip() for cmd in config_text.split('\n') if cmd.strip()]
            
            # Appliquer les commandes
            for cmd in commands:
                output = self.send_command_raw(connection, cmd)
                self.output_text.insert(tk.END, f"\n{cmd}")
                self.output_text.insert(tk.END, f"\n{output}\n")
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
        connection.write_channel(command + '\r')
        time.sleep(wait_time)
        output = connection.read_channel()
        return output
    
    def connect_to_device_console(self, device_name):
        try:
            connection = ConnectHandler(
                device_type='terminal_server',
                host=self.cml_config["controller"],
                username=self.cml_config["username"],
                password=self.cml_config["password"],
                session_timeout=120,
            )

            connection.write_channel('\r')
            time.sleep(1)
            connection.write_channel(f'open /{self.lab.title}/{device_name}/0\r')
            time.sleep(3)

            output = connection.read_channel()
            connection.write_channel('\r')
            time.sleep(1)
            connection.write_channel(self.device_user_entry.get() + '\r')
            time.sleep(1)
            connection.write_channel(self.device_pass_entry.get() + '\r')
            time.sleep(2)
            
            output += connection.read_channel()

            if '>' in output or '#' in output:
                return connection
            else:
                self.output_text.insert(tk.END, f"\n✗ Connexion échouée: {output}\n")
                return None
                
        except Exception as e:
            self.output_text.insert(tk.END, f"\n✗ Erreur de connexion: {str(e)}\n")
            return None
    
    def clear_output(self):
        self.output_text.delete(1.0, tk.END)
    
    # ===== MÉTHODES POUR LES TESTS =====
    
    def run_standard_test(self):
        device = self.test_device_combo.get()
        test_type = self.test_command_combo.get()
        
        if not device:
            messagebox.showerror("Erreur", "Veuillez sélectionner un équipement.")
            return
        
        if not self.connect_to_cml():
            return
        
        # Construire la commande de test
        if test_type == "ping":
            ip = self.ping_ip_entry.get()
            count = self.ping_count_entry.get()
            command = f"ping {ip} repeat {count}"
        else:
            command = test_type
        
        thread = threading.Thread(target=self._run_test_thread, 
                                 args=(device, command, test_type))
        thread.daemon = True
        thread.start()
    
    def run_custom_test(self):
        device = self.test_device_combo.get()
        command = self.custom_command_entry.get().strip()
        
        if not device:
            messagebox.showerror("Erreur", "Veuillez sélectionner un équipement.")
            return
        
        if not command:
            messagebox.showwarning("Commande vide", "Veuillez entrer une commande.")
            return
        
        if not self.connect_to_cml():
            return
        
        thread = threading.Thread(target=self._run_test_thread, 
                                 args=(device, command, "personnalisée"))
        thread.daemon = True
        thread.start()
    
    def run_connectivity_test(self):
        if not self.lab:
            messagebox.showerror("Erreur", "Aucun lab actif.")
            return
        
        thread = threading.Thread(target=self._run_connectivity_test_thread)
        thread.daemon = True
        thread.start()
    
    def _run_connectivity_test_thread(self):
        try:
            self.test_output_text.insert(tk.END, "\n" + "="*50 + "\n")
            self.test_output_text.insert(tk.END, "TEST DE CONNECTIVITÉ\n")
            self.test_output_text.insert(tk.END, "="*50 + "\n")
            
            # Tester chaque équipement
            for node in self.lab.nodes():
                self.test_output_text.insert(tk.END, f"\nÉquipement: {node.label}\n")
                self.test_output_text.see(tk.END)
                
                try:
                    connection = self.connect_to_device_console(node.label)
                    if connection:
                        # Tester la commande show version
                        output = self.send_command_raw(connection, "show version", wait_time=2)
                        self.test_output_text.insert(tk.END, f"✓ Connecté - Version:\n{output[:200]}...\n")
                        connection.disconnect()
                    else:
                        self.test_output_text.insert(tk.END, "✗ Non connecté\n")
                except Exception as e:
                    self.test_output_text.insert(tk.END, f"✗ Erreur: {str(e)}\n")
                
                self.test_output_text.see(tk.END)
                time.sleep(1)
            
            self.test_output_text.insert(tk.END, "\n" + "="*50 + "\n")
            self.test_output_text.insert(tk.END, "Test de connectivité terminé\n")
            self.update_status("Test de connectivité terminé")
            
        except Exception as e:
            self.test_output_text.insert(tk.END, f"\n✗ Erreur: {str(e)}\n")
            self.update_status(f"Erreur de test: {str(e)}")
    
    def _run_test_thread(self, device, command, test_type):
        try:
            self.test_output_text.insert(tk.END, "\n" + "="*50 + "\n")
            self.test_output_text.insert(tk.END, f"TEST: {test_type.upper()}\n")
            self.test_output_text.insert(tk.END, f"Équipement: {device}\n")
            self.test_output_text.insert(tk.END, f"Commande: {command}\n")
            self.test_output_text.insert(tk.END, "="*50 + "\n")
            
            connection = self.connect_to_device_console(device)
            if not connection:
                self.test_output_text.insert(tk.END, "\n✗ Échec de connexion\n")
                return
            
            # Exécuter la commande
            output = self.send_command_raw(connection, command, wait_time=3)
            
            self.test_output_text.insert(tk.END, f"\nRésultat:\n{output}\n")
            self.test_output_text.insert(tk.END, "\n" + "="*50 + "\n")
            self.test_output_text.insert(tk.END, "Test terminé\n")
            
            connection.disconnect()
            
            self.test_output_text.see(tk.END)
            self.update_status(f"Test {test_type} sur {device} terminé")
            
        except Exception as e:
            error_msg = f"\n✗ Erreur lors du test: {str(e)}\n"
            self.test_output_text.insert(tk.END, error_msg)
            self.test_output_text.see(tk.END)
            self.update_status(f"Erreur de test: {str(e)}")
    
    def clear_test_results(self):
        self.test_output_text.delete(1.0, tk.END)
    
    def save_test_results(self):
        results = self.test_output_text.get(1.0, tk.END).strip()
        if not results:
            messagebox.showwarning("Résultats vides", "Aucun résultat à sauvegarder.")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    f.write(results)
                self.update_status(f"Résultats sauvegardés dans {file_path}")
                messagebox.showinfo("Succès", f"Résultats sauvegardés dans {file_path}")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de la sauvegarde: {str(e)}")
    
    def export_all_tests(self):
        # Cette méthode pourrait être étendue pour exporter tous les tests historiques
        self.save_test_results()
    
    # ===== MÉTHODES POUR LES PARAMÈTRES =====
    
    def save_settings(self):
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
            messagebox.showinfo("Succès", "Paramètres sauvegardés avec succès.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la sauvegarde: {str(e)}")
    
    def load_config(self):
        try:
            if os.path.exists("cml_settings.json"):
                with open("cml_settings.json", "r") as f:
                    saved_config = json.load(f)
                    self.cml_config.update(saved_config)
                    
                    # Mettre à jour les champs
                    self.controller_entry.delete(0, tk.END)
                    self.controller_entry.insert(0, self.cml_config["controller"])
                    self.username_entry.delete(0, tk.END)
                    self.username_entry.insert(0, self.cml_config["username"])
                    self.password_entry.delete(0, tk.END)
                    self.password_entry.insert(0, self.cml_config["password"])
                    self.lab_name_entry.delete(0, tk.END)
                    self.lab_name_entry.insert(0, self.cml_config["lab_name"])
        except:
            pass  # Utiliser les paramètres par défaut
    
    def load_settings_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, "r") as f:
                    saved_config = json.load(f)
                
                self.cml_config.update(saved_config)
                
                # Mettre à jour les champs
                self.controller_entry.delete(0, tk.END)
                self.controller_entry.insert(0, self.cml_config["controller"])
                self.username_entry.delete(0, tk.END)
                self.username_entry.insert(0, self.cml_config["username"])
                self.password_entry.delete(0, tk.END)
                self.password_entry.insert(0, self.cml_config["password"])
                self.lab_name_entry.delete(0, tk.END)
                self.lab_name_entry.insert(0, self.cml_config["lab_name"])
                
                self.update_status(f"Paramètres chargés depuis {file_path}")
                messagebox.showinfo("Succès", f"Paramètres chargés depuis {file_path}")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors du chargement: {str(e)}")
    
    def test_cml_connection(self):
        thread = threading.Thread(target=self._test_cml_connection_thread)
        thread.daemon = True
        thread.start()
    
    def _test_cml_connection_thread(self):
        try:
            self.update_status("Test de connexion CML en cours...")
            
            client = ClientLibrary(
                f"https://{self.controller_entry.get()}",
                self.username_entry.get(),
                self.password_entry.get(),
                ssl_verify=False
            )
            
            # Tester en listant les labs
            labs = list(client.all_labs())
            
            self.update_status(f"✓ Connexion CML réussie ({len(labs)} labs trouvés)")
            messagebox.showinfo("Connexion réussie", 
                              f"Connexion CML établie avec succès!\n{len(labs)} labs trouvés.")
            
        except Exception as e:
            self.update_status(f"✗ Échec connexion CML: {str(e)}")
            messagebox.showerror("Échec connexion", 
                               f"Échec de connexion à CML:\n{str(e)}")
    
    def reset_settings(self):
        if messagebox.askyesno("Confirmation", 
                              "Êtes-vous sûr de vouloir réinitialiser tous les paramètres?"):
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
    
    def connect_to_cml(self):
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
        self.status_bar.config(text=f"Statut: {message}")
        self.root.update()

def main():
    root = tk.Tk()
    app = CMLAutomationApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()