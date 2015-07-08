package main

import "os"
import "net/http"
import "log"
import "strconv"
import "fmt"

func main() {
    var port int64
    port = 8000

    if len(os.Args) == 2 {
        port, _ = strconv.ParseInt(os.Args[1], 10, 32)
    }

    log.Println("Listening on", port)
    panic(http.ListenAndServe(fmt.Sprintf(":%d", port), http.FileServer(http.Dir("."))))
}
