# 🚀 CML2 Automation Tool - Édition Avancée

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-green)
![Cisco CML](https://img.shields.io/badge/Cisco-CML2-red)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20Mac-lightgrey)

**Une interface graphique complète pour automatiser Cisco Modeling Lab 2**  
*Créez, configurez et testez des topologies réseau complexes en quelques clics*

---

## 📋 Table des Matières

- [🌟 Vue d'ensemble](#-vue-densemble)
- [✨ Fonctionnalités](#-fonctionnalités)
- [🖼️ Captures d'écran](#-captures-décran)
- [⚡ Installation Rapide](#-installation-rapide)
- [🔧 Installation Détailée](#-installation-détaillée)
- [🎮 Guide d'Utilisation](#-guide-dutilisation)
- [⚙️ Configuration CML2](#️-configuration-cml2)
- [🔍 Tests et Validation](#-tests-et-validation)
- [🏗️ Architecture du Projet](#️-architecture-du-projet)
- [🧩 Extensibilité](#-extensibilité)
- [🐛 Dépannage](#-dépannage)
- [📊 Structure des Fichiers](#-structure-des-fichiers)
- [🤝 Contribution](#-contribution)
- [📜 Licence](#-licence)
- [📞 Support](#-support)
- [🔮 Roadmap](#-roadmap)

---

## 🌟 Vue d'ensemble

**CML2 Automation Tool** est une application desktop développée en Python qui révolutionne la manière de travailler avec Cisco Modeling Lab 2. Elle transforme les opérations complexes de gestion de labs réseau en une expérience visuelle et intuitive.

### 🎯 Pour qui est cet outil ?

- **Ingénieurs réseau** qui souhaitent automatiser leurs labs
- **Éducateurs** créant des environnements de formation
- **Étudiants** en réseaux et cybersécurité
- **Architectes** validant des designs réseau
- **Développeurs** testant des applications réseau

### 🔑 Avantages clés

- **⏱️ Gain de temps** : Réduisez le temps de déploiement de 80%
- **👨‍💻 Interface intuitive** : Pas besoin de lignes de commande complexes
- **🔄 Reproductibilité** : Sauvegardez et réutilisez vos topologies
- **🔗 Intégration complète** : Interface native avec l'API CML2
- **🎨 Visualisation avancée** : Voyez votre réseau comme jamais auparavant

---

## ✨ Fonctionnalités

### 🏗️ Gestion de Topologie

| Fonctionnalité | Description | Avantage |
|----------------|-------------|----------|
| **Éditeur graphique** | Interface drag-and-drop complète | Création visuelle sans codage |
| **16 types d'équipements** | Routeurs, switches, pare-feux, serveurs, etc. | Couverture complète des besoins |
| **Gestion des connexions** | Définition précise des ports et interfaces | Configuration réseau exacte |
| **Import/Export JSON** | Sauvegarde et partage de topologies | Portabilité et collaboration |
| **Validation automatique** | Détection des erreurs de connectivité | Économie de temps de débogage |

### 🎨 Visualisation Avancée

**Trois modes de visualisation disponibles :**
- 🔵 **Circulaire** : Vue d'ensemble équilibrée
- 🔲 **Grille** : Organisation structurée
- 📊 **Hiérarchique** : Vue par catégories

**Caractéristiques :**
- Zoom et déplacement fluides
- Couleurs par catégorie d'équipement
- Surbrillance des connexions
- Légende interactive

### ⚙️ Configuration Automatisée

- **Templates préconfigurés** pour tous les types d'équipements
- **Éditeur avec coloration syntaxique** et numérotation des lignes
- **Validation en temps réel** des configurations
- **Application en un clic** sur les équipements
- **Sauvegarde automatique** des configurations

### 🔬 Tests et Monitoring

- ✅ Tests de connectivité (ping, traceroute)
- ✅ Commandes show prédéfinies
- ✅ Commandes personnalisées
- ✅ Journalisation complète
- ✅ Export des résultats

### 🔄 Intégration CML2

- Connexion sécurisée via API
- Gestion complète du cycle de vie des labs
- Synchronisation en temps réel
- Support des images CML2 officielles

---

## 🖼️ Captures d'écran

*(Ajoutez vos captures d'écran ici)*

**Interface Principale :**



---

## ⚡ Installation Rapide

### Prérequis Minimum
- **Python 3.8+**
- **Contrôleur CML2 accessible**
- **2 Go de RAM minimum**
- **Connexion Internet** (pour télécharger les dépendances)

### Installation en 3 étapes

```bash
# 1. Cloner le repository
git clone https://github.com/votre-username/cml2-automation-tool.git
cd cml2-automation-tool

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Lancer l'application
python main.py

```
# Installation Détailée
# Option 1 : Installation avec venv (Recommandée)

# Créer un environnement virtuel
```python -m venv cml-env```

# Activer l'environnement
# Windows :
cml-env\Scripts\activate
# Linux/Mac :
```source cml-env/bin/activate``

# Installer les dépendances
```
pip install --upgrade pip
pip install -r requirements.txt

```

# Option 2 : Installation avec conda

# Créer un environnement conda
```conda create -n cml-tool python=3.9
conda activate cml-tool
```
# Installer les dépendances
```
pip install -r requirements.txt

```
# Option 3 : Installation manuelle

# Installer chaque dépendance individuellement
```
pip install tkinter
pip install netmiko==4.1.2
pip install virl2_client==2.5.0
pip install requests
```
# Vérification de l'installation
# Testez que tout fonctionne
```
python -c "
import tkinter
import netmiko
import virl2_client
print('✅ Toutes les dépendances sont installées !')
"
```



























