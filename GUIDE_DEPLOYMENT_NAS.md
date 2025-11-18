# Guide Complet de Déploiement sur NAS
## Application Mae & Eliot - BDSM Tracker

**✅ Workflow GitHub → NAS → Production configuré!**

---

## 📋 Table des Matières
1. [Prérequis](#prérequis)
2. [Étape 1: Exporter le code](#étape-1-exporter-le-code)
3. [Étape 2: Préparer votre NAS](#étape-2-préparer-votre-nas)
4. [Étape 3: Installer Docker](#étape-3-installer-docker)
5. [Étape 4: Transférer les fichiers](#étape-4-transférer-les-fichiers)
6. [Étape 5: Configuration](#étape-5-configuration)
7. [Étape 6: Lancer l'application](#étape-6-lancer-lapplication)
8. [Étape 7: Accéder à votre site](#étape-7-accéder-à-votre-site)
9. [Dépannage](#dépannage)

---

## Prérequis

**Ce dont vous avez besoin:**
- Un NAS (Synology, QNAP, ou autre)
- Un compte GitHub (gratuit)
- Accès administrateur à votre NAS
- 30 minutes de temps

---

## Étape 1: Exporter le code

### Option A: Via GitHub (RECOMMANDÉ)

1. **Connecter GitHub à Emergent:**
   - Dans Emergent, cliquez sur votre avatar en haut à droite
   - Cliquez sur "Profile"
   - Trouvez la section "GitHub Integration"
   - Cliquez sur "Connect GitHub"
   - Autorisez l'accès quand GitHub vous le demande

2. **Sauvegarder le code:**
   - Dans le chat Emergent, écrivez: "Save to GitHub"
   - Ou cherchez un bouton "Save to GitHub" dans l'interface
   - Attendez la confirmation
   - Notez l'URL de votre repository (exemple: https://github.com/votre-nom/mae-eliot)

### Option B: Téléchargement manuel

1. **Télécharger les fichiers:**
   - Dans Emergent, cherchez une option "Download" ou "Export"
   - Téléchargez le fichier ZIP
   - Décompressez-le sur votre ordinateur

---

## Étape 2: Préparer votre NAS

### A) Trouver l'adresse IP de votre NAS

**Méthode 1: Via l'interface web du NAS**
- Connectez-vous à l'interface de votre NAS
- Allez dans Panneau de configuration → Réseau
- Notez l'adresse IP (exemple: 192.168.1.50)

**Méthode 2: Via votre routeur**
- Connectez-vous à votre routeur (souvent 192.168.1.1)
- Regardez la liste des appareils connectés
- Trouvez votre NAS et notez son IP

**Méthode 3: Application mobile**
- Utilisez l'application de votre NAS (DS Finder pour Synology, Qfinder pour QNAP)
- L'IP sera affichée

### B) Activer SSH sur votre NAS

**Pour Synology:**
1. Ouvrez le Panneau de configuration
2. Allez dans "Terminal & SNMP"
3. Cochez "Activer le service SSH"
4. Cliquez sur "Appliquer"

**Pour QNAP:**
1. Ouvrez le Panneau de configuration
2. Allez dans "Telnet/SSH"
3. Cochez "Autoriser la connexion SSH"
4. Cliquez sur "Appliquer"

**Pour autres NAS:**
- Consultez le manuel de votre NAS
- Cherchez "activer SSH" dans les paramètres

---

## Étape 3: Installer Docker

### Pour Synology DSM 7.0+

1. **Ouvrir le Centre de paquets:**
   - Cliquez sur le menu principal
   - Ouvrez "Centre de paquets"

2. **Installer Container Manager:**
   - Dans la barre de recherche, tapez "Container Manager"
   - Cliquez sur "Container Manager" (c'est la nouvelle version de Docker)
   - Cliquez sur "Installer"
   - Attendez la fin de l'installation

### Pour QNAP

1. **Ouvrir l'App Center:**
   - Cliquez sur l'icône App Center

2. **Installer Container Station:**
   - Cherchez "Container Station"
   - Cliquez sur "Installer"
   - Attendez la fin de l'installation

### Pour autres NAS

- Cherchez "Docker" ou "Container" dans votre centre d'applications
- Si non disponible, vous devrez installer Docker manuellement via SSH (plus technique)

---

## Étape 4: Transférer les fichiers

### Méthode 1: Via Git (si vous avez utilisé GitHub)

1. **Se connecter en SSH:**
   - **Sur Windows:** Téléchargez PuTTY (https://putty.org/)
     - Ouvrez PuTTY
     - Mettez l'IP de votre NAS
     - Port: 22
     - Cliquez sur "Open"
   
   - **Sur Mac/Linux:** Ouvrez le Terminal
     ```bash
     ssh votre-nom-utilisateur@IP-DU-NAS
     ```
     (exemple: ssh admin@192.168.1.50)

2. **Installer Git (si pas déjà installé):**
   
   **Synology:**
   ```bash
   # Git est souvent déjà installé, testez:
   git --version
   
   # Si non installé, installez-le via le Centre de paquets
   ```
   
   **QNAP:**
   ```bash
   # Via QPKG
   opkg update
   opkg install git
   ```

3. **Créer un dossier pour votre application:**
   ```bash
   # Aller dans le dossier partagé
   cd /volume1/docker/  # Pour Synology
   # ou
   cd /share/Container/  # Pour QNAP
   
   # Créer un dossier
   mkdir mae-eliot
   cd mae-eliot
   ```

4. **Cloner le repository:**
   ```bash
   git clone https://github.com/votre-nom/mae-eliot.git .
   ```
   (Remplacez par l'URL de votre repo)

### Méthode 2: Via transfert de fichiers (plus simple)

1. **Sur Windows:**
   - Ouvrez l'Explorateur de fichiers
   - Dans la barre d'adresse, tapez: `\\IP-DU-NAS`
   - Exemple: `\\192.168.1.50`
   - Entrez vos identifiants
   - Allez dans le dossier partagé (souvent "docker" ou "homes")
   - Créez un dossier "mae-eliot"
   - Copiez tous vos fichiers dedans

2. **Sur Mac:**
   - Dans Finder, appuyez sur Cmd+K
   - Tapez: `smb://IP-DU-NAS`
   - Exemple: `smb://192.168.1.50`
   - Entrez vos identifiants
   - Suivez les mêmes étapes que Windows

---

## Étape 5: Configuration

### A) Modifier docker-compose.yml

1. **Ouvrir le fichier:**
   - Via SSH:
     ```bash
     cd /volume1/docker/mae-eliot  # Ou votre chemin
     nano docker-compose.yml
     ```
   
   - Ou via l'interface web de votre NAS (gestionnaire de fichiers)

2. **Modifier ces lignes importantes:**
   
   **Ligne SECRET_KEY:**
   ```yaml
   - SECRET_KEY=CHANGEZ_CETTE_CLE_SECRETE_MAINTENANT_123456789
   ```
   Changez en quelque chose de complexe, exemple:
   ```yaml
   - SECRET_KEY=MonSuperMotDePasseComplexe2024!@#
   ```

   **Ligne REACT_APP_BACKEND_URL:**
   ```yaml
   - REACT_APP_BACKEND_URL=http://localhost:8001
   ```
   Changez `localhost` par l'IP de votre NAS:
   ```yaml
   - REACT_APP_BACKEND_URL=http://192.168.1.50:8001
   ```

3. **Sauvegarder:**
   - Dans nano: Ctrl+X, puis Y, puis Entrée
   - Dans l'éditeur web: Bouton "Sauvegarder"

### B) Modifier le fichier .env du frontend (optionnel)

```bash
cd frontend
nano .env
```

Modifiez:
```
REACT_APP_BACKEND_URL=http://192.168.1.50:8001
```

---

## Étape 6: Lancer l'application

### Via SSH (Recommandé)

1. **Aller dans le dossier:**
   ```bash
   cd /volume1/docker/mae-eliot  # Votre chemin
   ```

2. **Construire et lancer:**
   ```bash
   docker-compose up -d
   ```
   
   Vous verrez:
   ```
   Creating network "mae-eliot_mae-eliot-network" ... done
   Creating volume "mae-eliot_mongodb_data" ... done
   Building backend...
   Building frontend...
   Creating mae-eliot-mongodb ... done
   Creating mae-eliot-backend ... done
   Creating mae-eliot-frontend ... done
   ```

3. **Vérifier que tout fonctionne:**
   ```bash
   docker-compose ps
   ```
   
   Tous les services doivent être "Up":
   ```
   NAME                    STATUS
   mae-eliot-mongodb       Up 2 minutes
   mae-eliot-backend       Up 1 minute
   mae-eliot-frontend      Up 1 minute
   ```

### Via l'interface web (Synology/QNAP)

**Synology - Container Manager:**
1. Ouvrez Container Manager
2. Allez dans "Projet"
3. Cliquez sur "Créer"
4. Sélectionnez le dossier contenant docker-compose.yml
5. Donnez un nom: "mae-eliot"
6. Cliquez sur "Suivant" puis "Terminé"

**QNAP - Container Station:**
1. Ouvrez Container Station
2. Allez dans "Create Application"
3. Sélectionnez "Import from docker-compose.yml"
4. Sélectionnez votre fichier
5. Cliquez sur "Create"

---

## Étape 7: Accéder à votre site

### Première connexion

1. **Ouvrez votre navigateur**

2. **Allez à l'adresse:**
   ```
   http://IP-DE-VOTRE-NAS:3000
   ```
   Exemple: `http://192.168.1.50:3000`

3. **Vous devriez voir la page de connexion!**

4. **Créer votre premier compte:**
   - Cliquez sur "S'inscrire"
   - Entrez votre email
   - Créez un mot de passe
   - Cliquez sur "S'inscrire"

5. **Se connecter:**
   - Retournez sur "Se connecter"
   - Entrez vos identifiants
   - Vous êtes connecté!

### Accès depuis l'extérieur (optionnel)

Si vous voulez accéder à votre site depuis l'extérieur de chez vous:

1. **Configurer le port forwarding sur votre routeur:**
   - Connectez-vous à votre routeur
   - Trouvez "Port Forwarding" ou "Redirection de ports"
   - Ajoutez ces règles:
     - Port externe: 3000 → Port interne: 3000 → IP du NAS
     - Port externe: 8001 → Port interne: 8001 → IP du NAS

2. **Trouver votre IP publique:**
   - Allez sur https://whatismyip.com
   - Notez votre IP publique

3. **Accéder depuis l'extérieur:**
   ```
   http://VOTRE-IP-PUBLIQUE:3000
   ```

⚠️ **ATTENTION:** Exposer votre NAS sur Internet comporte des risques de sécurité!

---

## Dépannage

### Problème: Les containers ne démarrent pas

**Solution 1: Vérifier les logs**
```bash
docker-compose logs
```

**Solution 2: Reconstruire**
```bash
docker-compose down
docker-compose up -d --build
```

### Problème: "Cannot connect to backend"

**Vérifiez que le backend fonctionne:**
```bash
docker-compose ps
```

**Testez l'API directement:**
Dans votre navigateur:
```
http://IP-DU-NAS:8001/api/
```
Vous devriez voir du JSON.

**Vérifiez REACT_APP_BACKEND_URL:**
- Il doit pointer vers l'IP de votre NAS, pas localhost

### Problème: MongoDB n'a pas assez d'espace

**Vérifier l'espace disque:**
```bash
df -h
```

**Nettoyer Docker:**
```bash
docker system prune -a
```

### Problème: "Port already in use"

**Vérifier les ports utilisés:**
```bash
netstat -tulpn | grep :3000
netstat -tulpn | grep :8001
```

**Solution:** Changer les ports dans docker-compose.yml
```yaml
ports:
  - "3001:80"  # Au lieu de 3000
```

---

## Commandes utiles

### Voir les logs en direct
```bash
docker-compose logs -f
```

### Arrêter l'application
```bash
docker-compose down
```

### Redémarrer l'application
```bash
docker-compose restart
```

### Supprimer tout (attention!)
```bash
docker-compose down -v  # -v supprime aussi les données!
```

### Voir l'utilisation des ressources
```bash
docker stats
```

### Entrer dans un container
```bash
docker exec -it mae-eliot-backend bash
```

---

## Maintenance

### Sauvegardes

**Sauvegarder la base de données:**
```bash
docker exec mae-eliot-mongodb mongodump --out /data/backup
```

**Sauvegarder le volume MongoDB:**
```bash
docker run --rm -v mae-eliot_mongodb_data:/data -v $(pwd):/backup ubuntu tar cvf /backup/mongodb-backup.tar /data
```

### Mises à jour

**Mettre à jour le code:**
```bash
cd /volume1/docker/mae-eliot
git pull
docker-compose up -d --build
```

---

## Support

Si vous avez des problèmes:
1. Vérifiez les logs: `docker-compose logs`
2. Vérifiez que tous les containers sont "Up": `docker-compose ps`
3. Redémarrez: `docker-compose restart`
4. Demandez de l'aide avec les logs

---

## Notes de sécurité importantes

✅ **À FAIRE:**
- Changez la SECRET_KEY
- Utilisez des mots de passe forts
- Faites des sauvegardes régulières
- Gardez Docker à jour

❌ **À NE PAS FAIRE:**
- N'exposez pas directement sur Internet sans HTTPS
- Ne partagez pas votre SECRET_KEY
- N'utilisez pas "admin/admin" comme identifiants

---

Bon courage! 🚀