#[macro_use] extern crate rocket;
use http::StatusCode;
use std::{env, process, thread, time};
use rocket::http::{Status};
use rocket::config::{Config};

#[get("/health")]
fn health() -> Status {
    Status::Ok
}

#[get("/?<data>", format="text/plain")]
fn binary(data: Option<String>) -> String { 
    let res = data.map(|val|to_binary(&val))
        .unwrap_or("Please provide a text to convert into binary.".to_string());
    res
}   

#[launch]
async fn rocket() -> _ {
    let ingress_host: String = match env::var("INGRESS_HOST") {
        Ok(val) => val.parse().unwrap(),
        Err(_) => {
            println!("Env variable 'INGRESS_HOST' not defined, exiting..");
            process::exit(1);
        }    
    };

    let port: u16 = match env::var("MICROSERVICE_PORT") {
        Ok(val) => val.parse().unwrap_or(8080),
        Err(_) => {
            println!("Env variable 'MICROSERVICE_PORT' not defined, exiting..");
            process::exit(1);
        }    
    };

    match register(ingress_host.as_str(), "binary-rs", port).await {
        Ok(()) => println!("Service is registered.."),
        Err(_) => {
            println!("Something went wrong during service registration..");
            process::exit(1);
        }
    };

    let figment = Config::figment()
        .merge(("address", "0.0.0.0"))
        .merge(("port", port));
        
    rocket::custom(figment).mount("/binary-rs", routes![binary, health])
}

async fn register(host: &str, command: &str, port: u16) -> Result<(), Box<dyn std::error::Error>> {

    let params = [("command", command), ("port", &port.to_string())];
    let client = reqwest::Client::new();
    

    let mut registered: bool = false;
    while !registered {
        
        println!("{}", [host,"register"].join(""));
        let response = client.post([host, "register"].join("/"))
            .form(&params)
            .send().await?;
    
        registered = match response.status() {
            StatusCode::OK => true,
            _ => { 
                thread::sleep(time::Duration::from_secs(30));
                false
            }    
        };
    }      
    Ok(()) 
}

fn to_binary(text: &String) -> String {
    let mut binary_representation: String = String::new();

    for byte in text.as_bytes() {
        binary_representation += &format!("{:b}", byte);
    }
    return binary_representation
}    
