# Protocol Buffers message format




(eheart/server/eheart.proto)=
## eheart/server/eheart.proto
WebSocket payload formats of e-Heart server interface

Message formats are defined in separated files
for [request](eheart/server/proto/request.proto)
and [response](eheart/server/proto/response.proto).




(eheart/server/proto/request.proto)=
## eheart/server/proto/request.proto
Formats for request messages

All request message are in [Request](Request) message format.

(Command)=
### enum Command
Commands

| Name | Number | Description |
| ---- | ------ | ----------- |
| UNDEFINED | 0 | DO NOT USE |
| INIT | 1 | Initialize an engine with a model |
| SET_DIFFVAR_VAL | 2 | Set the values of the differential variables |
| GET_DIFFVAR_NAME | 3 | Get the names of the differential variables |
| GET_CURRENT_VAL | 4 | Get the current values of time and the differential variables |
| SET_WATCHING_VAR | 5 | Set watching variables, which values are returned for SOLVE_IVP command |
| SOLVE_IVP | 6 | Solve an initial value problem and return a series of solution values. |
| CHANGE_TIME | 7 | Change the value of time |
| SET_MODEL_CONST | 8 | Set the values of model constants |
| EVAL_MODEL_VAR | 9 | Evaluate model variables |
| CALL_MODEL_METHOD | 10 | Call a method of the model class |




(CallModelMethodParam)=
### message CallModelMethodParam
CALL_MODEL_METHOD command parameters

| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| method_name | [string](string) |  | Method name |
| args | [CallModelMethodParam.ArgsEntry](CallModelMethodParam.ArgsEntry) | repeated | Arguments |



(CallModelMethodParam.ArgsEntry)=
### message CallModelMethodParam.ArgsEntry
| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| key | [string](string) |  |  |
| value | [GenericScalarOrArray](GenericScalarOrArray) |  |  |



(ChangeTimeParam)=
### message ChangeTimeParam
CHANGE_TIME command parameters

| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| t | [double](double) |  | Time to be set |
| options | [ChangeTimeParam.OptionsEntry](ChangeTimeParam.OptionsEntry) | repeated | Options for Engine.restart |



(ChangeTimeParam.OptionsEntry)=
### message ChangeTimeParam.OptionsEntry
| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| key | [string](string) |  |  |
| value | [double](double) |  |  |



(EvalModelVarParam)=
### message EvalModelVarParam
EVAL_MODEL_VAR command parameters

| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| vars | [string](string) | repeated | Variable names to be evaluated |
| t | [double](double) |  | Time to be evaluated (required) |
| y | [double](double) | repeated | Differential variable values used in evaluation |



(GetCurrentValParam)=
### message GetCurrentValParam
GET_CURRENT_VAL command parameter


(GetDiffvarNameParam)=
### message GetDiffvarNameParam
GET_DIFFVAR_NAME command parameter


(InitParam)=
### message InitParam
INIT command parameters

| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| model | [string](string) |  | Fully quarified model class name |
| t | [double](double) |  | Initial time |
| options | [InitParam.OptionsEntry](InitParam.OptionsEntry) | repeated | Options at Engine instantiation |



(InitParam.OptionsEntry)=
### message InitParam.OptionsEntry
| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| key | [string](string) |  |  |
| value | [double](double) |  |  |



(Request)=
### message Request
Requests for e-Heart server

| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| command | [Command](Command) |  | Command |
| parameter | [google.protobuf.Any](google.protobuf.Any) |  | Parameter encoded from the parameter message corresponding to the command |



(SetDiffvarValParam)=
### message SetDiffvarValParam
SET_DIFFVAR_VAL command parameter

| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| valmap | [SetDiffvarValParam.ValmapEntry](SetDiffvarValParam.ValmapEntry) | repeated | Map of differential variable names and values |



(SetDiffvarValParam.ValmapEntry)=
### message SetDiffvarValParam.ValmapEntry
| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| key | [string](string) |  |  |
| value | [double](double) |  |  |



(SetModelConstParam)=
### message SetModelConstParam
SET_MODEL_CONST command parameter

| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| valmap | [SetModelConstParam.ValmapEntry](SetModelConstParam.ValmapEntry) | repeated | Map of constant names and values |



(SetModelConstParam.ValmapEntry)=
### message SetModelConstParam.ValmapEntry
| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| key | [string](string) |  |  |
| value | [double](double) |  |  |



(SetWatchingVarParam)=
### message SetWatchingVarParam
SET_WATCHING_VAR command parameter

| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| vars | [string](string) | repeated | Names of watching variables |



(SolveIVPParam)=
### message SolveIVPParam
SOLVE_IVP command parameters

| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| tn | [double](double) |  | Next time |
| output_interval | [double](double) |  | Interval of solution output |






(eheart/server/proto/response.proto)=
## eheart/server/proto/response.proto
Formats for response messages

Response message formats depend on request commands.

(CurrentValResponse)=
### message CurrentValResponse
Response for GET_CURRENT_VAL Command

| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| t | [double](double) |  | Current time |
| y | [double](double) | repeated | Values of the differential variables |



(DiffvarNameResponse)=
### message DiffvarNameResponse
Response for GET_DIFFVAR_NAME Command

| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| names | [string](string) | repeated | Variable names |



(MethodReturnResponse)=
### message MethodReturnResponse
Response for CALL_MODEL_METHOD Command

| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| return_value | [GenericScalarOrArray](GenericScalarOrArray) | repeated | Method return value(s) |



(SolutionResponse)=
### message SolutionResponse
Response of IVP Solution for SOLVE_IVP Command

| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| t | [ValueSeries](ValueSeries) |  | Time |
| diffvars | [ValueSeries](ValueSeries) | repeated | Differential variable values |
| watching_vars | [ValueSeries](ValueSeries) | repeated | Watching variable values |



(StatusResponse)=
### message StatusResponse
Status response for all the commands in errors and 
for SET_DIFFVAR_VAL, SET_WATCHING_VAR, CHANGE_TIME,
and SET_MODEL_CONST commands

| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| success | [bool](bool) |  | Status |
| message | [string](string) |  | Error message |



(ValueArrayResponse)=
### message ValueArrayResponse
Response of variable values for EVAL_MODEL_VAR Command

| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| values | [double](double) | repeated | Array of values |



(ValueSeries)=
### message ValueSeries
Series of values

| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| values | [double](double) | repeated | Values in a series |






(eheart/server/proto/util.proto)=
## eheart/server/proto/util.proto
Utility types

(GenericScalarOrArray)=
### message GenericScalarOrArray
Generic format for method arguments and return value

| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| isscalar | [bool](bool) |  | Whether the value is a scalar |
| value | [GenericValue](GenericValue) | repeated | Value(s) |



(GenericValue)=
### message GenericValue
Generic value format

| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| real | [float](float) |  |  |
| integer | [int64](int64) |  |  |
| string | [string](string) |  |  |



