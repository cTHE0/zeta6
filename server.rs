use std::collections::HashMap;
use std::net::SocketAddr;
use std::sync::Arc;
use tokio::io::{AsyncBufReadExt, AsyncWriteExt, BufReader};
use tokio::net::{TcpListener, TcpStream};
use tokio::sync::Mutex;

type Clients = Arc<Mutex<HashMap<String, SocketAddr>>>;
type MessageQueue = Arc<Mutex<HashMap<String, Vec<String>>>>;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let listener = TcpListener::bind("0.0.0.0:8080").await?;
    let clients: Clients = Arc::new(Mutex::new(HashMap::new()));
    let queue: MessageQueue = Arc::new(Mutex::new(HashMap::new()));
    
    println!("Serveur démarré sur 0.0.0.0:8080");

    loop {
        let (socket, addr) = listener.accept().await?;
        let clients = clients.clone();
        let queue = queue.clone();
        
        tokio::spawn(async move {
            if let Err(e) = handle_client(socket, addr, clients, queue).await {
                eprintln!("Erreur client: {}", e);
            }
        });
    }
}

async fn handle_client(
    mut socket: TcpStream,
    addr: SocketAddr,
    clients: Clients,
    queue: MessageQueue,
) -> Result<(), Box<dyn std::error::Error>> {
    let (reader, mut writer) = socket.split();
    let mut reader = BufReader::new(reader);
    let mut line = String::new();
    
    // Login
    writer.write_all(b"USERNAME: ").await?;
    reader.read_line(&mut line).await?;
    let username = line.trim().to_string();
    line.clear();
    
    clients.lock().await.insert(username.clone(), addr);
    println!("{} connecté", username);
    
    // Envoyer messages en attente
    let mut q = queue.lock().await;
    if let Some(messages) = q.get_mut(&username) {
        for msg in messages.drain(..) {
            writer.write_all(format!("MSG:{}\n", msg).as_bytes()).await?;
        }
    }
    drop(q);
    
    writer.write_all(b"OK\n").await?;
    
    // Boucle principale
    loop {
        line.clear();
        let n = reader.read_line(&mut line).await?;
        if n == 0 { break; }
        
        let parts: Vec<&str> = line.trim().splitn(2, ':').collect();
        if parts.len() != 2 { continue; }
        
        match parts[0] {
            "SEND" => {
                // Format: SEND:destinataire:message
                let msg_parts: Vec<&str> = parts[1].splitn(2, ':').collect();
                if msg_parts.len() == 2 {
                    let to = msg_parts[0];
                    let msg = format!("{}:{}", username, msg_parts[1]);
                    
                    let mut q = queue.lock().await;
                    q.entry(to.to_string()).or_insert_with(Vec::new).push(msg);
                    writer.write_all(b"ACK\n").await?;
                }
            }
            "POLL" => {
                let mut q = queue.lock().await;
                if let Some(messages) = q.get_mut(&username) {
                    for msg in messages.drain(..) {
                        writer.write_all(format!("MSG:{}\n", msg).as_bytes()).await?;
                    }
                }
                writer.write_all(b"POLL_OK\n").await?;
            }
            _ => {}
        }
    }
    
    clients.lock().await.remove(&username);
    println!("{} déconnecté", username);
    Ok(())
}
