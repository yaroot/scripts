package main

import (
	"github.com/things-go/go-socks5"
	"github.com/things-go/go-socks5/bufferpool"
	"log"
	"os"
)

const (
	LISTEN       = "LISTEN"
	DEFAULT_BIND = ":8000"
)

func main() {
	server := socks5.NewServer(
		socks5.WithBufferPool(bufferpool.NewPool(32)),
		socks5.WithLogger(socks5.NewLogger(log.New(os.Stderr, "socks5:", log.LstdFlags))),
	)

	listen := os.Getenv(LISTEN)
	if listen == "" {
		listen = DEFAULT_BIND
	}
	log.Printf("Serving on %s", listen)
	err := server.ListenAndServe("tcp", listen)
	if err != nil {
		log.Fatalln(err)
	}
}
