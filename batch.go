package elevator

type BatchOperations []BatchOperation

type BatchOperation struct {
    OpCode string
    OpArgs []string
}


func NewBatchOperation(op_code string, op_args []string) *BatchOperation {
    return &BatchOperation{
        OpCode: op_code,
        OpArgs: op_args,
    }
}

func BatchOperationFromSlice(slice []string) *BatchOperation {
    return NewBatchOperation(slice[0], slice[1:])
}

func BatchOperationsFromRequestArgs(args []string) *BatchOperations {
    var ops BatchOperations
    var cur_index int = 0
    var last_index int = 0

    for index, elem := range args {
        cur_index = index
        if index > 0 {
            if elem == SIGNAL_BATCH_PUT || elem == SIGNAL_BATCH_DELETE {
                ops = append(ops, *BatchOperationFromSlice(args[last_index:index]))
                last_index = index
            }
        }
    }

    // Add the rest
    if cur_index > 0 {
        ops = append(ops, *BatchOperationFromSlice(args[last_index : cur_index+1]))
    }

    return &ops
}
