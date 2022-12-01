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
	processed := 0
	errors := 0
	defer wg.Done()
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

//func dotRename(file string) {
//	head, filename := filepath.Split(file)
//	newfilename := filepath.Join(head, ".", filename)
//	os.Rename(filename, newfilename)
//}

func dotRename(path string) error {
	head := filepath.Dir(path)
	fn := filepath.Base(path)
	if err := os.Rename(path, filepath.Join(head, "."+fn)); err != nil {
		log.Printf("Can't rename a file: %s", path)
		return err
	}
	return nil
}

func processLine(linesChan chan string, memcacheChans map[string]chan *memcacheItem, resChan chan results, wg *sync.WaitGroup) {
	errors := 0
	defer wg.Done()
	for line := range linesChan {
		log.Printf("INFO:Line: %s", line)
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
		log.Println("INFO:item: %s", item)
		mcChan <- item
	}
	resChan <- results{errors: errors, processed: 0}
}

func readFile(filepath string, linesChan chan string) error {
	log.Println("INFO: Start processing file:", filepath)
	file, err := os.Open(filepath)
	log.Println("INFO:5 %s", file)
	if err != nil {
		log.Printf("ERROR: Can't open file: %s", filepath)
		return err
	}
	//defer file.Close()
	gz, err := gzip.NewReader(file)
	log.Println("INFO:6 %s", gz)
	if err != nil {
		log.Printf("ERROR: Can't do new reader: %s", err)
		return err
	}
	//defer gz.Close()

	fileScanner := bufio.NewScanner(gz)

	// read line by line
	for fileScanner.Scan() {
		line := fileScanner.Text()
		line = strings.Trim(line, " ")
		log.Println("INFO:7Line: %s", line)
		if line == "" {
			log.Println("INFO:continue9 ")
			continue
		}
		log.Println("INFO:Line: %s", line)
		linesChan <- line
	}
	//if err := fileScanner.Err(); err != nil {
	//	log.Printf("ERROR: Error while reading file: %s", err)
	//	return err
	//}
	log.Println("INFO:read all")
	return nil
}

func runProcess(opts *options) error {
	deviceMemc := map[string]string{
		"idfa": opts.idfa,
		"gaid": opts.gaid,
		"adid": opts.adid,
		"dvid": opts.dvid,
	}
	log.Println("INFO:1")
	files, err := filepath.Glob(opts.pattern)
	log.Println("INFO:2")
	if err != nil {
		log.Println("ERROR: Could not find files in directory %s", opts.pattern)
		return err
	}
	log.Println("INFO:opts.chanBuf %s", opts.chanBuf)
	linesChan := make(chan string, opts.chanBuf)
	for _, file := range files {
		log.Println("INFO:3")
		err := readFile(file, linesChan)
		if err != nil {
			continue
		}
		//readFile(file, linesChan)
		log.Println("INFO:8 file")
		err1 := dotRename(file)
		if err1 != nil {
			return err1
		}
	}

	resultsChan := make(chan results)
	memcacheChans := make(map[string]chan *memcacheItem)
	log.Println("INFO:going opts.nworkers ")

	var wgProc sync.WaitGroup

	log.Println("INFO:going go processLine", opts.nworkers)
	for i := 0; i < opts.nworkers; i++ {
		log.Println("INFO:go processLine", opts.nworkers)
		wgProc.Add(1)
		go processLine(linesChan, memcacheChans, resultsChan, &wgProc)
	}

	var wgMemc sync.WaitGroup

	log.Println(len(deviceMemc))

	for devType, memcAddr := range deviceMemc {
		memcacheChans[devType] = make(chan *memcacheItem, opts.chanBuf)
		mcache := memcache.New(memcAddr)
		log.Println("INFO:go memc")
		wgMemc.Add(1)
		go memcacheStore(mcache, memcacheChans[devType], resultsChan, &wgMemc)
	}

	wgProc.Wait()
	wgMemc.Wait()

	close(linesChan)
	for _, mcChan := range memcacheChans {
		close(mcChan)
	}
	close(resultsChan)

	processed := 0
	errors := 0
	for results := range resultsChan {
		processed += results.processed
		errors += results.errors
	}

	errRate := float32(errors) / float32(processed)
	if errRate < NORMAL_ERR_RATE {
		log.Printf("Acceptable error rate (%g). Successfull load\n", errRate)
	} else {
		log.Printf("High error rate (%g > %g). Failed load\n", errRate, NORMAL_ERR_RATE)
	}
	return nil
}

func main() {
	chanBuf := flag.Int("bufsize", 5, "bufsize")
	nworkers := flag.Int("nworkers", 5, "nworkers")
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

		//defer f.Close()
		log.Println(f.Name())
	}
	log.Println("INFO: Memcache loader started with options: %s", opts)

	err := runProcess(opts)
	if err != nil {
		log.Fatalf("Unexpected error: ", err)
		return
	}
}
