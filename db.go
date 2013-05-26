package elevator

import (
	uuid "code.google.com/p/go-uuid/uuid"
	"errors"
	"fmt"
	l4g "github.com/alecthomas/log4go"
	leveldb "github.com/jmhodges/levigo"
)

type Db struct {
	Name      string        		`json:"name"`
	Uid       string        		`json:"uid"`
	Path      string        		`json:"path"`
	Options   *StorageEngineConfig 	`json:"-"`
	Status    int           		`json:"-"`
	Connector *leveldb.DB   		`json:"-"`
	Channel   chan *Request 		`json:"-"`
}


func NewDb(db_name string, path string, config *StorageEngineConfig) *Db {
	return &Db{
		Name:    db_name,
		Path:    path,
		Uid:     uuid.New(),
		Status:  DB_STATUS_UNMOUNTED,
		Options: config,
		Channel: make(chan *Request),
	}
}


// StartRoutine listens on the Db channel awaiting
// for incoming requests to execute. Willingly
// blocking on each Exec call received through the
// channel in order to protect requests.
func (db *Db) StartRoutine() {
	for request := range db.Channel {
		response, err := processRequest(db, request)
		if err == nil {
			forwardResponse(response, request)
		}
	}
}

// Mount sets the database status to DB_STATUS_MOUNTED
// and instantiates the according leveldb connector
func (db *Db) Mount() (err error) {
	if db.Status == DB_STATUS_UNMOUNTED {
		db.Connector, err = leveldb.Open(db.Path, db.Options.ToLeveldbOptions())
		if err != nil {
			return err
		}

		db.Status = DB_STATUS_MOUNTED
		db.Channel = make(chan *Request)
		go db.StartRoutine()
	} else {
		error := errors.New(fmt.Sprintf("Database %s already mounted", db.Name))
		l4g.Error(error)
		return error
	}

	l4g.Debug(func() string {
		return fmt.Sprintf("Database %s mounted", db.Name)
	})

	return nil
}

// Unmount sets the database status to DB_STATUS_UNMOUNTED
// and deletes the according leveldb connector
func (db *Db) Unmount() (err error) {
	if db.Status == DB_STATUS_MOUNTED {
		db.Connector.Close()
		close(db.Channel)
		db.Status = DB_STATUS_UNMOUNTED
	} else {
		error := errors.New(fmt.Sprintf("Database %s already unmounted", db.Name))
		l4g.Error(error)
		return error
	}

	l4g.Debug(func() string {
		return fmt.Sprintf("Database %s unmounted", db.Name)
	})

	return nil
}
