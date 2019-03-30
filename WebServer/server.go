package hello

import(
	"net/http"
	"encoding/json"
	"io/ioutil"
)

func init(){
	http.HandleFunc("/", handler)
}

var memory []map[string]string

func handler(writer http.ResponseWriter, request *http.Request){
	switch request.Method{
		case "POST":
			var dict map[string]string
			data, _ := ioutil.ReadAll(request.Body)
			json.Unmarshal(data, &dict)
			memory = append(memory, dict)
			writer.WriteHeader(200)
		case "GET":
			s, _ := json.MarshalIndent(memory, "","    ")
			writer.WriteHeader(200)
			writer.Write(s)
	}
}
