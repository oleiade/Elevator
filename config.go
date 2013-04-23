package elevator

import (
	"reflect"
	goconfig "github.com/msbranco/goconfig"
)

type Config struct {
	Daemon			bool	`ini:"daemonize"`
	Endpoint		string	`ini:"endpoint"`
	Pidfile			string	`ini:"pidfile"`
	StorePath		string	`ini:"database_store_path"`
	StoragePath		string	`ini:"databases_storage_path"`
	DefaultDb		string	`ini:"default_db"`
	ActivityLog		string	`ini:"activity_log"`
	ErrorsLog		string	`ini:"errors_log"`
	Unixsocket		string	`ini:"unixsocket"`
}

func NewConfig() *Config {
	return &Config{
		Daemon: false,
		Endpoint: "tcp://127.0.0.1:4141",
		StorePath: "/var/lib/elevator/store",
		StoragePath: "/var/lib/elevator",
		DefaultDb: "default",
		ActivityLog: "/var/log/elevator/activity.log",
		ErrorsLog: "/var/log/elevator/errors.log",
		Unixsocket: "",
	}
}

func (c *Config) FromFile(filepath string) error {
	ini_config, err := goconfig.ReadConfigFile(filepath)
	if err != nil { return err }

	config := reflect.ValueOf(c).Elem()
	config_type := config.Type()

	for i := 0; i < config.NumField() ; i++ {
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