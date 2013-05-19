package elevator

import (
	goconfig "github.com/msbranco/goconfig"
	"reflect"
)

type Config struct {
	Daemon      bool   `ini:"daemonize"`
	Endpoint    string `ini:"endpoint"`
	Pidfile     string `ini:"pidfile"`
	StorePath   string `ini:"database_store_path"`
	StoragePath string `ini:"databases_storage_path"`
	DefaultDb   string `ini:"default_db"`
	LogFile 	string `ini:"log_file"`
	LogLevel    string `ini:"log_level"`
}

func NewConfig() *Config {
	return &Config{
		Daemon:      false,
		Endpoint:    "tcp://127.0.0.1:4141",
		Pidfile:     "/var/run/elevator.pid",
		StorePath:   "/var/lib/elevator/store",
		StoragePath: "/var/lib/elevator",
		DefaultDb:   "default",
		LogFile: 	 "/var/log/elevator.log",
		LogLevel:    "INFO",
	}
}

func (c *Config) FromFile(filepath string) error {
	ini_config, err := goconfig.ReadConfigFile(filepath)
	if err != nil {
		return err
	}

	config := reflect.ValueOf(c).Elem()
	config_type := config.Type()

	for i := 0; i < config.NumField(); i++ {
		struct_field := config.Field(i)
		field_tag := config_type.Field(i).Tag.Get("ini")

		switch {
		case struct_field.Type().Kind() == reflect.Bool:
			config_value, err := ini_config.GetBool("core", field_tag)
			if err == nil {
				struct_field.SetBool(config_value)
			}
		case struct_field.Type().Kind() == reflect.String:
			config_value, err := ini_config.GetString("core", field_tag)
			if err == nil {
				struct_field.SetString(config_value)
			}
		}
	}

	return nil
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
		c.LogLevel = *cmdline.LogLevel
	}
}
