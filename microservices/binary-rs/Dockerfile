FROM rust:latest as builder
WORKDIR /usr/src/binary-rs
COPY . .
RUN cargo install --path .

FROM debian:buster-slim
RUN apt-get update && apt-get install -y libssl-dev
COPY --from=builder /usr/local/cargo/bin/binary-rs /usr/local/bin/binary-rs
ENTRYPOINT ["/usr/local/bin/binary-rs"]
