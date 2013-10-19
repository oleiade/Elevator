package elevator

import (
	leveldb "github.com/jmhodges/levigo"
	goconfig "github.com/msbranco/goconfig"
	"github.com/oleiade/reflections"
	"reflect"
)

type Config struct {
	// Exported core configuration
	Daemon      bool   `ini:"daemonize"`
	Endpoint    string `ini:"endpoint"`
	Pidfile     string `ini:"pidfile"`
	Storepath   string `ini:"database_store"`
	Storagepath string `ini:"databases_storage_path"`
	Defaultdb   string `ini:"default_db"`
	Logfile     string `ini:"log_file"`
	Loglevel    string `ini:"log_level"`

	// Unexported storage engine configuration variables
	compression     bool `ini:"compression"`       // default: true
	blocksize       int  `ini:"block_size"`        // default: 4096
	cachesize       int  `ini:"cache_size"`        // default: 128 * 1048576 (128MB)
	bloomfilterbits int  `ini:"bloom_filter_bits"` // default: 100
	maxopenfiles    int  `ini:"max_open_files"`    // default: 150
	verifychecksums bool `ini:"verify_checksums"`  // default: false
	writebuffersize int  `ini:"write_buffer_size"` // default: 64 * 1048576 (64MB)
}

func NewConfig() *Config {
	return &Config{
		// core configuration default setup
		Daemon:      false,
		Endpoint:    "tcp://127.0.0.1:4141",
		Pidfile:     "/var/run/elevator.pid",
		Storepath:   "/var/lib/elevator/store",
		Storagepath: "/var/lib/elevator",
		Defaultdb:   "default",
		Logfile:     "/var/log/elevator.log",
		Loglevel:    "INFO",

		// storage engine configuration default setup
		compression:     true,
		blocksize:       4096,
		cachesize:       512 * 1048576,
		bloomfilterbits: 100,
		maxopenfiles:    150,
		verifychecksums: false,
		writebuffersize: 64 * 1048576,
	}
}

func (c *Config) ExtractLeveldbOptions() *leveldb.Options {
	options := leveldb.NewOptions()

	options.SetCreateIfMissing(true)
	options.SetCompression(leveldb.CompressionOpt(Btoi(c.compression)))
	options.SetBlockSize(c.blocksize)
	options.SetCache(leveldb.NewLRUCache(c.cachesize))
	options.SetFilterPolicy(leveldb.NewBloomFilter(c.bloomfilterbits))
	options.SetMaxOpenFiles(c.maxopenfiles)
	options.SetParanoidChecks(c.verifychecksums)
	options.SetWriteBufferSize(c.writebuffersize)

	return options
}

// A bit verbose, and not that dry, but could not find
// more clever for now.
func (c *Config) UpdateFromCmdline(cmdline *Cmdline) {
	if *cmdline.DaemonMode != DEFAULT_DAEMON_MODE {
		c.Daemon = *cmdline.DaemonMode
	}

	if *cmdline.Endpoint != DEFAULT_ENDPOINT {
		c.Endpoint = *cmdline.Endpoint
	}

	if *cmdline.LogLevel != DEFAULT_LOG_LEVEL {
		c.Loglevel = *cmdline.LogLevel
	}
}

func (c *Config) OverrideWithIni(filePath string) error {
	iniConfig, err := goconfig.ReadConfigFile(filePath)
	if err != nil {
		return err
	}

	iniConfigSections := iniConfig.GetSections()
	configTags, _ := reflections.Tags(*c, "ini")

	for _, section := range iniConfigSections {
		sectionOptions, err := iniConfig.GetOptions(section)
		if err != nil {
			return err
		}

		for field, tag := range configTags {
			if StringSliceContains(sectionOptions, tag) {
				fieldType, _ := reflections.GetFieldKind(*c, field)
				var configValue interface{}

				switch fieldType {
				case reflect.Bool:
					configValue, err = iniConfig.GetBool(section, tag)
				case reflect.String:
					configValue, err = iniConfig.GetString(section, tag)
				case reflect.Int:
					configValue, err = iniConfig.GetInt64(section, tag)
				}

				if err == nil {
					reflections.SetField(c, field, configValue)
				}
			}
		}

	}

	return nil
}
