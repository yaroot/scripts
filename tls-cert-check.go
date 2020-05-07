package main

import (
	"crypto/tls"
	"flag"
	"fmt"
	"log"
	"net"
	"os"
	"time"
)

func main() {
	target := flag.String("target", "", "format: <host:port>")
	minDays := flag.Int("min-days", 0, "check expiration date (if greater than 0)")
	verbose := flag.Bool("v", false, "print expiration date")
	flag.Parse()

	if *target == "" {
		fmt.Println("Missing target")
		os.Exit(1)
	}

	dialer := new(net.Dialer)
	dialer.Timeout = 10 * time.Second

	conn, err := tls.DialWithDialer(dialer, "tcp", *target, &tls.Config{})
	if err != nil {
		log.Panicln(err)
	}

	certs := conn.ConnectionState().PeerCertificates
	if len(certs) == 0 {
		fmt.Println("No certification") // impossible here
		os.Exit(1)
	}

	crt := certs[0]
	daysLeft := int(crt.NotAfter.Sub(time.Now()).Hours() / 24)

	if *verbose {
		fmt.Printf("Expiration date: %s\n", crt.NotAfter.String())
	}

	if *minDays > 0 {
		if daysLeft <= *minDays {
			fmt.Printf("%d day(s) left\n", daysLeft)
			os.Exit(1)
		}
	}
}
