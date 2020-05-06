package main

import (
	"bufio"
	"flag"
	"fmt"
	"github.com/miekg/dns"
	"log"
	"os"
	"strings"
)

type DNSHandler struct {
	blocklist map[string]byte
	client    *dns.Client
	upstream  string
}

func (d *DNSHandler) ServeDNS(w dns.ResponseWriter, r *dns.Msg) {
	forward := make([]dns.Question, 0)
	blocked := make([]dns.Question, 0)

	for _, q := range r.Question {
		_, found := d.blocklist[strings.TrimSuffix(q.Name, ".")]
		if found {
			log.Printf("Blocking %s\n", q.String())
			blocked = append(blocked, q)
		} else {
			forward = append(forward, q)
		}
	}

	if len(forward) > 0 {
		m := new(dns.Msg)
		m.MsgHdr.RecursionDesired = true
		m.Compress = r.Compress
		m.Question = forward

		//log.Println("query")
		//log.Printf("%+v\n", m)

		mr, _, err := d.client.Exchange(m, d.upstream)
		if err != nil {
			log.Println(err.Error())
		}
		if mr != nil {
			//log.Println("response")
			//log.Printf("%+v\n", mr)
			r.MsgHdr = mr.MsgHdr
			r.Answer = mr.Answer
			r.Ns = mr.Ns
			r.Extra = mr.Extra
		}
	}

	for _, b := range blocked {
		r.MsgHdr.Response = true
		r.MsgHdr.RecursionAvailable = true
		rr, err := dns.NewRR(fmt.Sprintf("%s 10 IN A 0.0.0.0", b.Name))
		if err != nil {
			log.Println(err.Error())
		} else {
			r.Answer = append(r.Answer, rr)
		}
	}

	err := w.WriteMsg(r)
	if err != nil {
		log.Println(err.Error())
	}
}

func readBlockList(path string, bl map[string]byte) error {
	f, err := os.Open(path)
	if err != nil {
		return err
	}
	defer f.Close()
	r := bufio.NewScanner(f)
	for r.Scan() {
		a := strings.TrimSuffix(r.Text(), ".")
		bl[a] = '1'
	}
	return nil
}

func main() {
	bind := flag.String("bind", "127.0.0.1:1052", "binding address")
	upstream := flag.String("upstream", "127.0.0.1:1053", "upstream dns")
	blockListFile := flag.String("block_file", "block.list", "path to block file")
	flag.Parse()

	blocklist := make(map[string]byte)

	err := readBlockList(*blockListFile, blocklist)
	if err != nil {
		log.Panicln(err.Error())
	}

	log.Printf("Loaded %d domains from '%s'\n", len(blocklist), *blockListFile)

	client := new(dns.Client)
	client.Net = "tcp"

	dnshandler := &DNSHandler{
		blocklist: blocklist,
		client:    client,
		upstream:  *upstream,
	}

	udpServer := dns.Server{
		Addr:    *bind,
		Net:     "udp",
		Handler: dnshandler,
	}

	tcpServer := dns.Server{
		Addr:    *bind,
		Net:     "tcp",
		Handler: dnshandler,
	}

	go func() {
		err = udpServer.ListenAndServe()
		if err != nil {
			log.Panicln(err.Error())
		}
	}()

	err = tcpServer.ListenAndServe()
	if err != nil {
		log.Panicln(err.Error())
	}
}
