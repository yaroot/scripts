package main

import (
	"context"
	"errors"
	"flag"
	"fmt"
	"github.com/cloudflare/cloudflare-go"
	"io/ioutil"
	"net"
	"net/http"
	"os"
	"strings"
)

func get_ip() (string, error) {
	cli := &http.Client{
		Transport: &http.Transport{
			DialContext: func(ctx context.Context, network, addr string) (net.Conn, error) {
				var d net.Dialer
				return d.DialContext(ctx, "tcp4", addr)
			},
		},
	}

	r, err := cli.Get("http://checkip.dns.he.net")
	if err != nil {
		return "", err
	}

	body, err := ioutil.ReadAll(r.Body)
	if err != nil {
		return "", err
	}

	for _, s := range strings.Split(string(body), "\n") {
		if strings.HasPrefix(s, "Your IP address is : ") {
			// Your IP address is : 10.10.10.10</body>
			s = strings.TrimPrefix(s, "Your IP address is : ")
			s = strings.TrimSuffix(s, "</body>")
			return strings.TrimSpace(s), nil
		}
	}
	return "", errors.New("cannot find IP address")
}

func update_ip(zone, record, ip string, force bool) error {
	token := os.Getenv("CF_API_TOKEN")
	if token == "" {
		return errors.New("no token provided (CF_API_TOKEN)")
	}
	api, err := cloudflare.NewWithAPIToken(token)
	if err != nil {
		return err
	}
	zoneID, err := api.ZoneIDByName(zone)
	if err != nil {
		return err
	}

	dnsRecord := cloudflare.DNSRecord{Name: record}
	recs, err := api.DNSRecords(zoneID, dnsRecord)
	if err != nil {
		return err
	}

	if len(recs) > 1 {
		return errors.New("More than 1 records, exit")
	} else if len(recs) == 1 {
		rr := recs[0]
		if rr.Type != "A" {
			return errors.New(fmt.Sprintf("Record type mismatch (%s)", rr.Type))
		}
		if rr.Content == ip {
			fmt.Printf("No need to update, [%s] already points to [%s]\n", rr.Name, rr.Content)
			return nil
		}
		fmt.Printf("Setting [%s] to [%s] (from [%s])\n", rr.Name, ip, rr.Content)
		if force {
			rr.Content = ip
			rr.TTL = 120
			err = api.UpdateDNSRecord(zoneID, rr.ID, rr)
			if err != nil {
				return err
			}
		}
	} else {
		fmt.Printf("Creating record %s -> %s\n", record, ip)
		if force {
			dnsRecord.Type = "A"
			dnsRecord.Content = ip
			dnsRecord.TTL = 120
			_, err = api.CreateDNSRecord(zoneID, dnsRecord)
			if err != nil {
				return err
			}
		}
	}
	return nil
}

func main() {
	zone := flag.String("zone", "", "zone name")
	record := flag.String("record", "", "record name")
	force := flag.Bool("force", false, "dry-run otherwise")
	ip := flag.String("ip", "", "optional ip address")
	flag.Parse()

	if *zone == "" {
		println("empty zone name")
		os.Exit(-1)
	}
	if *record == "" {
		println("empty record name")
		os.Exit(-1)
	}

	ipaddr := *ip
	if ipaddr == "" {
		newip, err := get_ip()
		if err != nil {
			panic(err)
		}
		ipaddr = newip
	}
	err := update_ip(*zone, *record, ipaddr, *force)
	if err != nil {
		panic(err)
	}
}
