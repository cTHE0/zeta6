use std::fs::{File, OpenOptions};
use std::io::{BufRead, BufReader, Write};
use std::path::Path;
use tokio::io::{AsyncBufReadExt, AsyncWriteExt, BufReader as TokioBufReader};
use tokio::net::TcpStream;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let args: Vec<String> = std::env::args().collect();
    if args.len() < 3 {
        eprintln!("Usage: {} <serveur:port> <username>", args[0]);
        std::process::exit(1);
    }
    
    let server = &args[1];
    let username = &args[2];
    let msg_file = format!("{}_messages.txt", username);
    
    println!("Connexion à {}...", server);
    let socket = TcpStream::connect(server).await?;
    println!("✓ Connecté au serveur");
    let (reader, mut writer) = socket.into_split();
    let mut reader = TokioBufReader::new(reader);
    let mut line = String::new();
    
    // Login
    println!("Authentification...");
    reader.read_line(&mut line).await?;
    writer.write_all(format!("{}\n", username).as_bytes()).await?;
    line.clear();
    
    // Recevoir messages en attente
    println!("Récupération des messages...");
    loop {
        line.clear();
        reader.read_line(&mut line).await?;
        let trimmed = line.trim();
        
        if trimmed == "OK" {
            break;
        } else if trimmed.starts_with("MSG:") {
            let msg = &trimmed[4..];
            save_message(&msg_file, msg)?;
            println!("📩 {}", msg);
        }
    }
    
    println!("✓ Prêt !");
    println!("\nCommandes: /send <user> <message> | /poll | /list | /quit");
    print!("> ");
    std::io::stdout().flush()?;
    
    // Thread pour recevoir messages
    let msg_file_clone = msg_file.clone();
    tokio::spawn(async move {
        let mut line = String::new();
        loop {
            line.clear();
            if reader.read_line(&mut line).await.is_err() { break; }
            let trimmed = line.trim();
            
            if trimmed.starts_with("MSG:") {
                let msg = &trimmed[4..];
                if save_message(&msg_file_clone, msg).is_ok() {
                    println!("\n📩 {}", msg);
                    print!("> ");
                    std::io::stdout().flush().ok();
                }
            }
        }
    });
    
    // Boucle commandes
    let stdin = std::io::stdin();
    for line in stdin.lock().lines() {
        let line = line?;
        let parts: Vec<&str> = line.trim().split_whitespace().collect();
        
        if parts.is_empty() { continue; }
        
        match parts[0] {
            "/send" if parts.len() >= 3 => {
                let to = parts[1];
                let msg = parts[2..].join(" ");
                writer.write_all(format!("SEND:{}:{}\n", to, msg).as_bytes()).await?;
                save_message(&msg_file, &format!("TO {}:{}", to, msg))?;
                println!("✓ Envoyé");
            }
            "/poll" => {
                writer.write_all(b"POLL:\n").await?;
            }
            "/list" => {
                list_messages(&msg_file)?;
            }
            "/quit" => {
                break;
            }
            _ => {
                println!("Commande inconnue");
            }
        }
        print!("> ");
        std::io::stdout().flush()?;
    }
    
    Ok(())
}

fn save_message(file: &str, msg: &str) -> std::io::Result<()> {
    let mut f = OpenOptions::new()
        .create(true)
        .append(true)
        .open(file)?;
    writeln!(f, "{}", msg)?;
    Ok(())
}

fn list_messages(file: &str) -> std::io::Result<()> {
    if !Path::new(file).exists() {
        println!("Aucun message");
        return Ok(());
    }
    
    let f = File::open(file)?;
    let reader = BufReader::new(f);
    
    println!("\n--- Historique ---");
    for line in reader.lines() {
        println!("{}", line?);
    }
    println!("------------------\n");
    Ok(())
}
