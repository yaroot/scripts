package main

import (
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"strconv"
)

func main() {
	var listenPort, targetPort int64

	if len(os.Args) != 3 {
		log.Printf("usage: %s [listen-port] [target-port]\n", os.Args[0])
		return
	}
	listenPort = parsePort(os.Args[1])
	targetPort = parsePort(os.Args[2])

	log.Printf("Starting on :%d -> :%d\n", listenPort, targetPort)
	err := http.ListenAndServe(
		fmt.Sprintf("127.0.0.1:%d", listenPort),
		http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			defer r.Body.Close()

			reqUrl := fmt.Sprintf("http://127.0.0.1:%d%s", targetPort, r.URL.String())
			req, err := http.NewRequest(r.Method, reqUrl, r.Body)
			if err != nil {
				http.Error(w, "Proxy error", http.StatusInternalServerError)
				return
			}
			log.Printf("    -> %s\n", req.URL.String())

			resp, err := http.DefaultClient.Do(req)
			if err != nil {
				http.Error(w, "Backend error", http.StatusBadGateway)
				return
			}
			defer resp.Body.Close()

			_, err = io.Copy(w, resp.Body)
			if err != nil {
				log.Printf("Error: transfering response %s\n", err.Error())
			}
			log.Printf("%d <- %s\n", resp.StatusCode, req.URL.String())
		}),
	)
	if err != nil {
		log.Panic(err)
	}

}

func parsePort(x string) int64 {
	p, err := strconv.ParseInt(x, 10, 16)
	if err != nil {
		log.Panicf("Invalid port: '%s'\n", x)
	}
	return p
}
