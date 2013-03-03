package elevator

import (
	"fmt"
	"errors"
	leveldb 	"github.com/jmhodges/levigo"
	uuid 		"code.google.com/p/go-uuid/uuid"
)

type Db struct {
	Name		string			`json:"-"`
	Uid 		string 			`json:"uid"`
	Path		string 			`json:"path"`
	Status		int  			`json:"-"`
	Connector 	*leveldb.DB		`json:"-"`
	Channel 	chan *Request	`json:"-"`
}


func NewDb(db_name string, path string) (*Db) {
	return &Db{
		Name: db_name,
		Path: path,
		Uid: uuid.New(),
		Status: DB_STATUS_UNMOUNTED,
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
		if err != nil { return err }

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

// Forward synchronously puts a value in
// the Db channel. It intends to be used in a
// goroutine, in order to keep Db operations
// ordered while not blocking the incoming requests
// handling.
func (db *Db) Forward(request *Request) {
	db.Channel <- request
}

// Routine listens on the Db channel awaiting
// for incoming requests to execute and sends clients
// response.
func (db *Db) Routine() {
	for request := range db.Channel {
		fmt.Println(request)
	}
}
