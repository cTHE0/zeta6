# Messagerie Minimale Rust

## Architecture
- **Serveur VPS**: Relais pur, ne stocke rien de permanent
- **Client CLI**: Stockage local des messages dans `<username>_messages.txt`

## Compilation (sur votre machine)

```bash
cargo build --release
```

Cela génère :
- `target/release/server` → à envoyer sur votre VPS
- `target/release/client` → à distribuer aux clients

## Déploiement

### Sur le VPS
```bash
./server
```

### Sur les machines clientes
```bash
./client <ip_serveur>:8080 <votre_username>
```

## Utilisation

### Commandes client
- `/send <user> <message>` - Envoyer un message
- `/poll` - Vérifier nouveaux messages
- `/list` - Afficher l'historique local
- `/quit` - Quitter

### Exemple
```bash
# Terminal 1 (alice)
./client localhost:8080 alice
> /send bob Salut!

# Terminal 2 (bob)
./client localhost:8080 bob
📩 alice:Salut!
> /send alice Coucou!
```

## Stockage
Chaque utilisateur a un fichier `<username>_messages.txt` contenant:
- Messages reçus: `expediteur:message`
- Messages envoyés: `TO destinataire:message`

## Protocole
- `USERNAME:` - Identification
- `SEND:dest:msg` - Envoi message
- `POLL:` - Récupération messages
- `MSG:from:text` - Réception message
- `ACK` / `OK` - Confirmations
