package main

import (
	"context"
	"errors"
	"flag"
	"fmt"
	"io"
	"net"
	"net/http"
	"os"
	"strings"

	"github.com/cloudflare/cloudflare-go/v5"
	"github.com/cloudflare/cloudflare-go/v5/dns"
	"github.com/cloudflare/cloudflare-go/v5/option"
	"github.com/cloudflare/cloudflare-go/v5/zones"
)

type CfUpdate struct {
	httpCli  *http.Client
	cfClient *cloudflare.Client
}

func newV4Client() *http.Client {
	cli := &http.Client{
		Transport: &http.Transport{
			DialContext: func(ctx context.Context, network, addr string) (net.Conn, error) {
				var d net.Dialer
				return d.DialContext(ctx, "tcp4", addr)
			},
		},
	}
	return cli
}

func (u *CfUpdate) GetIp() (string, error) {
	r, err := u.httpCli.Get("http://checkip.dns.he.net")
	if err != nil {
		return "", err
	}
	defer r.Body.Close()

	body, err := io.ReadAll(r.Body)
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
	return "", errors.New("no ip address found")
}

func (u *CfUpdate) GetZoneByName(ctx context.Context, zone string) (string, error) {
	params := zones.ZoneListParams{
		Name: cloudflare.F(zone),
	}
	page, err := u.cfClient.Zones.List(ctx, params)
	if err != nil {
		return "", err
	}

	for page != nil {
		for _, z := range page.Result {
			if z.Name == zone {
				return z.ID, nil
			}
		}

		page, err = page.GetNextPage()
		if err != nil {
			return "", err
		}
	}
	return "", errors.New("zone not found")
}

func (u *CfUpdate) GetRecordByName(ctx context.Context, zoneId string, record string) (*dns.RecordResponse, error) {
	params := dns.RecordListParams{
		ZoneID: cloudflare.F(zoneId),
		Name: cloudflare.F(dns.RecordListParamsName{
			Exact: cloudflare.F(record),
		}),
	}

	page, err := u.cfClient.DNS.Records.List(ctx, params)
	if err != nil {
		return nil, err
	}

	for page != nil {
		for _, r := range page.Result {
			if r.Name == record {
				return &r, nil
			}
		}

		page, err = page.GetNextPage()
		if err != nil {
			return nil, err
		}
	}
	return nil, errors.New("record not found")
}

func (u *CfUpdate) UpdateIp(ctx context.Context, zone, record, ip string, force bool) error {
	zoneId, err := u.GetZoneByName(ctx, zone)
	if err != nil {
		return err
	}

	r, err := u.GetRecordByName(ctx, zoneId, record)
	if err != nil {
		return err
	}

	if r.Content == ip {
		fmt.Printf("Skip updating, %s already sets to [%s]\n", zone, ip)
		return nil
	}

	fmt.Printf("Updating %s: from [%s] to [%s]\n", record, r.Content, ip)
	if force {
		_, err = u.cfClient.DNS.Records.Edit(ctx, r.ID, dns.RecordEditParams{
			ZoneID: cloudflare.F(zoneId),
			Body: dns.ARecordParam{
				Content: cloudflare.F(ip),
			},
		})
		if err != nil {
			return err
		}
	}

	return nil
}

func main() {
	zone := flag.String("zone", "", "zone name (example.com)")
	record := flag.String("record", "", "record name (server.example.com)")
	force := flag.Bool("force", false, "dry-run otherwise")
	ip := flag.String("ip", "", "optional ip address (leave empty to auto-detect the address)")
	flag.Parse()
	var err error

	cfToken := os.Getenv("CF_API_TOKEN")
	if cfToken == "" {
		panic("no token provided (CF_API_TOKEN)")
	}

	if *zone == "" {
		panic("empty zone name")
	}
	if *record == "" {
		panic("empty record name")
	}

	cfupdate := &CfUpdate{
		httpCli:  newV4Client(),
		cfClient: cloudflare.NewClient(option.WithAPIToken(cfToken)),
	}

	ipaddr := *ip
	if ipaddr == "" {
		ipaddr, err = cfupdate.GetIp()
		if err != nil {
			panic(err)
		}
	}
	fmt.Printf("detect ip: %s\n", ipaddr)

	err = cfupdate.UpdateIp(context.Background(), *zone, *record, ipaddr, *force)
	if err != nil {
		panic(err)
	}
}
