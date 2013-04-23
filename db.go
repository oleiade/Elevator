package elevator

import (
	"log"
	"errors"
	uuid "code.google.com/p/go-uuid/uuid"
	leveldb "github.com/jmhodges/levigo"
)

type Db struct {
	Name      string        `json:"name"`
	Uid       string        `json:"uid"`
	Path      string        `json:"path"`
	Status    int           `json:"-"`
	Connector *leveldb.DB   `json:"-"`
	Channel   chan *Request `json:"-"`
}

func NewDb(db_name string, path string) *Db {
	return &Db{
		Name:    db_name,
		Path:    path,
		Uid:     uuid.New(),
		Status:  DB_STATUS_UNMOUNTED,
		Channel: make(chan *Request),
	}
}

// Mount sets the database status to DB_STATUS_MOUNTED
// and instantiates the according leveldb connector
func (db *Db) Mount() (err error) {
	if db.Status == DB_STATUS_UNMOUNTED {
		opts := leveldb.NewOptions()
		opts.SetCache(leveldb.NewLRUCache(512))
		opts.SetCreateIfMissing(true)

		db.Connector, err = leveldb.Open(db.Path, opts)
		if err != nil {
			return err
		}

		db.Status = DB_STATUS_MOUNTED
		db.Channel = make(chan *Request)
		go db.Routine()
	} else {
		return errors.New("Database already mounted")
	}

	return nil
}

// Unmount sets the database status to DB_STATUS_UNMOUNTED
// and deletes the according leveldb connector
func (db *Db) Unmount() (err error) {
	if db.Status == DB_STATUS_MOUNTED {
		db.Status = DB_STATUS_UNMOUNTED
		db.Connector = nil
		close(db.Channel)
	} else {
		return errors.New("Database already unmounted")
	}

	return nil
}

// Routine listens on the Db channel awaiting
// for incoming requests to execute and sends clients
// response.
func (db *Db) Routine() {
	log.Printf("%s routine started", db.Name)
	for request := range db.Channel {
		Exec(db, request)
	}
}
