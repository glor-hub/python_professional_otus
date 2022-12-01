package main

import (
	"bufio"
	"compress/gzip"
	"flag"
	"fmt"
	"github.com/bradfitz/gomemcache/memcache"
	"github.com/golang/protobuf/proto"
	"homework15/appinstalled"
	"log"
	"os"
	"path/filepath"
	"strconv"
	"strings"
	"sync"
)

const NORMAL_ERR_RATE = 0.01

type options struct {
	chanBuf  int
	nworkers int
	logFile  string
	dry      bool
	pattern  string
	idfa     string
	gaid     string
	adid     string
	dvid     string
}

type appsInstalled struct {
	devType string
	devId   string
	lat     float64
	lon     float64
	apps    []uint32
}

type results struct {
	errors    int
	processed int
}

type memcacheItem struct {
	key  string
	data []byte
}

func parseAppsInstalled(line string) *appsInstalled {
	lineParts := strings.Split(line, "\t")
	if len(lineParts) < 5 {
		log.Printf("ERROR: Not all parts was found in line: %s", line)
		return nil
	}
	devType := lineParts[0]
	devId := lineParts[1]
	if devType == "" || devId == "" {
		log.Printf("ERROR: devType or devId was not found in line: %s", line)
		return nil
	}

	lat, err := strconv.ParseFloat(lineParts[2], 32)
	if err != nil {
		log.Printf("ERROR: Invalid geo coord lat in line: %s", line)
		return nil
	}

	lon, err := strconv.ParseFloat(lineParts[3], 32)
	if err != nil {
		log.Printf("ERROR: Invalid geo coord lon in line: %s", line)
		return nil
	}
	rawApps := lineParts[4]
	apps := make([]uint32, 0)
	for _, app := range strings.Split(rawApps, ",") {
		appId, err := strconv.Atoi(app)
		if err != nil {
			log.Printf("ERROR: Not all user apps are digits: in line: %s", line)
			return nil
		}
		apps = append(apps, uint32(appId))
	}
	log.Printf("INFO: appsInstalled structure: devType %s, devId %s, lat %f, lon %f, apps %s",
		devType, devId, lat, lon, apps)

	return &appsInstalled{
		devType: devType,
		devId:   devId,
		lat:     lat,
		lon:     lon,
		apps:    apps,
	}
}

func packedAppsInstalled(appsInstalled *appsInstalled) (*memcacheItem, error) {
	ua := &appinstalled.UserApps{
		Lat:  proto.Float64(appsInstalled.lat),
		Lon:  proto.Float64(appsInstalled.lon),
		Apps: appsInstalled.apps,
	}
	key := fmt.Sprintf("%s:%s", appsInstalled.devType, appsInstalled.devId)
	packed, err := proto.Marshal(ua)
	if err != nil {
		return nil, err
	}
	return &memcacheItem{key, packed}, nil
}

func memcacheStore(mcClient *memcache.Client, ItemsChan chan *memcacheItem, resultsChan chan results, wg *sync.WaitGroup) {
	defer wg.Done()
	processed := 0
	errors := 0
	for item := range ItemsChan {
		err := mcClient.Set(&memcache.Item{
			Key:   item.key,
			Value: item.data,
		})
		if err != nil {
			errors += 1
		} else {
			processed += 1
		}
	}
	resultsChan <- results{errors, processed}
}

func dotRename(path string) error {
	head := filepath.Dir(path)
	fn := filepath.Base(path)
	if err := os.Rename(path, filepath.Join(head, "."+fn)); err != nil {
		log.Printf("Can't rename a file: %s", path)
		return err
	}
	return nil
}

func processLine(linesChan chan string, memcacheChans map[string]chan *memcacheItem, resChan chan results) {
	//defer wg.Done()
	errors := 0
	for line := range linesChan {
		appsInstalled := parseAppsInstalled(line)
		if appsInstalled == nil {
			errors += 1
			continue
		}
		item, err := packedAppsInstalled(appsInstalled)
		if err != nil {
			errors += 1
			continue
		}
		mcChan, opened := memcacheChans[appsInstalled.devType]
		if !opened {
			log.Println("ERROR: Unknown device type:", appsInstalled.devType)
			errors += 1
			continue
		}
		mcChan <- item
	}
	resChan <- results{errors: errors, processed: 0}
}

func readFile(filepath string, linesChan chan string) error {
	log.Println("INFO: Start processing file:", filepath)
	file, err := os.Open(filepath)
	if err != nil {
		log.Printf("ERROR: Can't open file: %s", filepath)
		return err
	}
	defer file.Close()
	gz, err := gzip.NewReader(file)
	if err != nil {
		log.Printf("ERROR: Can't do new reader: %s", err)
		return err
	}
	defer gz.Close()

	fileScanner := bufio.NewScanner(gz)

	// read line by line
	for fileScanner.Scan() {
		line := fileScanner.Text()
		line = strings.Trim(line, " ")
		if line == "" {
			continue
		}
		linesChan <- line
	}
	if err := fileScanner.Err(); err != nil {
		log.Printf("ERROR: Error while reading file: %s", err)
		return err
	}
	return nil
}

func runProcess(opts *options) error {
	deviceMemc := map[string]string{
		"idfa": opts.idfa,
		"gaid": opts.gaid,
		"adid": opts.adid,
		"dvid": opts.dvid,
	}
	linesChan := make(chan string, opts.chanBuf)
	resultsMcChan := make(chan results, opts.chanBuf)
	resultsProcChan := make(chan results, opts.chanBuf)
	memcacheChans := make(map[string]chan *memcacheItem, opts.chanBuf)

	var wg sync.WaitGroup

	for devType, memcAddr := range deviceMemc {
		memcacheChans[devType] = make(chan *memcacheItem, opts.chanBuf)
		mc := memcache.New(memcAddr)
		wg.Add(1)
		go memcacheStore(mc, memcacheChans[devType], resultsMcChan, &wg)
	}

	for i := 0; i < opts.nworkers; i++ {
		go processLine(linesChan, memcacheChans, resultsProcChan)
	}
	files, err := filepath.Glob(opts.pattern)
	if err != nil {
		log.Println("ERROR: Could not find files in directory %s", opts.pattern)
		return err
	}
	for _, file := range files {
		err := readFile(file, linesChan)
		if err != nil {
			continue
		}
		log.Println("INFO:File %s was processed", file)
		dotRename(file)
	}
	log.Println("INFO:waiting for the completion of goroutines group ")
	wg.Wait()
	for _, mcChan := range memcacheChans {
		close(mcChan)
	}
	log.Println("INFO: goroutines group is completed")
	close(linesChan)
	processed := 0
	errors := 0
	for results := range resultsMcChan {
		processed += results.processed
		errors += results.errors
	}
	for results := range resultsProcChan {
		processed += results.processed
		errors += results.errors
	}
	close(resultsProcChan)
	close(resultsMcChan)
	log.Println("INFO:Closed all chans")

	errRate := float32(errors) / float32(processed)
	if errRate < NORMAL_ERR_RATE {
		log.Printf("Acceptable error rate (%g). Successfull load\n", errRate)
	} else {
		log.Printf("High error rate (%g > %g). Failed load\n", errRate, NORMAL_ERR_RATE)
	}
	return nil
}

func main() {
	chanBuf := flag.Int("bufsize", 1, "bufsize")
	nworkers := flag.Int("nworkers", 1, "nworkers")
	logFile := flag.String("log", "log.txt", "log")
	dry := flag.Bool("dry", false, "dry")
	pattern := flag.String("pattern", "data/*.tsv.gz", "Directory to search the files")
	idfa := flag.String("idfa", "127.0.0.1:33013", "memcached address for idfa")
	gaid := flag.String("gaid", "127.0.0.1:33014", "memcached address for gaid")
	adid := flag.String("adid", "127.0.0.1:33015", "memcached address for adid")
	dvid := flag.String("dvid", "127.0.0.1:33016", "memcached address for dvid")

	flag.Parse()

	opts := &options{
		chanBuf:  *chanBuf,
		nworkers: *nworkers,
		logFile:  *logFile,
		dry:      *dry,
		pattern:  *pattern,
		idfa:     *idfa,
		gaid:     *gaid,
		adid:     *adid,
		dvid:     *dvid,
	}

	if opts.logFile != "" {
		f, err := os.OpenFile(opts.logFile, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
		if err != nil {
			log.Fatal(err)
		}
		//log.SetOutput(f)

		defer f.Close()
		log.Println(f.Name())
	}
	log.Println("INFO: Memcache loader started with options: %s", opts)

	err := runProcess(opts)
	if err != nil {
		log.Fatalf("Unexpected error: ", err)
		return
	}
}
