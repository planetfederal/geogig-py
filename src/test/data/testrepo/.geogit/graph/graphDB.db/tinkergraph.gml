graph [
	node [
		id 1
		blueprintsId "3"
		identifier "758eb00ce65173dc17d71e902ec3797ecb2705e9"
	]
	node [
		id 2
		blueprintsId "1"
		identifier "3f15ee86775f1b2d53dfe31f410d8b7bd07bcd33"
	]
	node [
		id 3
		blueprintsId "0"
		identifier "root"
	]
	node [
		id 4
		blueprintsId "7"
		identifier "93880f09e919526008ff598ba86ee671b2b9594a"
	]
	node [
		id 5
		blueprintsId "5"
		identifier "92863701fd6e8724331c012617dbea32136dcc4c"
	]
	node [
		id 6
		blueprintsId "9"
		identifier "17dd53454861cd308d09dec61268d2ddb2c113e0"
	]
	edge [
		source 2
		target 3
		label "TOROOT"
		blueprintsId "2"
	]
	edge [
		source 6
		target 5
		label "PARENT"
		blueprintsId "10"
	]
	edge [
		source 5
		target 1
		label "PARENT"
		blueprintsId "6"
	]
	edge [
		source 1
		target 2
		label "PARENT"
		blueprintsId "4"
	]
	edge [
		source 4
		target 5
		label "PARENT"
		blueprintsId "8"
	]
]
