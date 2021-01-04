package main

import (
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"sort"
	"strconv"
)

func main() {
	var port int64
	port = 8000

	if len(os.Args) == 2 {
		port, _ = strconv.ParseInt(os.Args[1], 10, 32)
	}

	log.Println("Listening on", port)
	panic(http.ListenAndServe(fmt.Sprintf(":%d", port), handler{}))
}

type handler struct {
}

func (h handler) ServeHTTP(rep http.ResponseWriter, req *http.Request) {
	defer req.Body.Close()
	log.Printf("=> %s %s%s", req.Method, req.Host, req.URL)

	keys := make([]string, 0, len(req.Header))
	for k := range req.Header {
		keys = append(keys, k)
	}
	sort.Strings(keys)

	for _, key := range keys {
		for _, val := range req.Header.Values(key) {
			log.Printf("->   %s: %s\n", key, val)
		}
	}

	body, err := ioutil.ReadAll(req.Body)
	if err != nil {
		log.Println(err.Error())
		return
	}
	bs := string(body)
	log.Printf("-> START BODY\n---\n%s\n---\n", bs)
	log.Printf("-> END BODY")
}
