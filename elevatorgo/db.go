package elevator

import (
	"errors"
	leveldb "github.com/jmhodges/levigo"
)

type Db struct {
	Name				string		`json:"-"`
	Uid 				string 		`json:"uid"`
	Path				string 		`json:"path"`
	Status				int  		`json:"-"`
	Connector 			*leveldb.DB	`json:"-"`
	Channel 			chan string `json:"-"`
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
	} else {
		return errors.New("Database already unmounted")
	}

	return nil
}
