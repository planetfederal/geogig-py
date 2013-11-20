graph [
	node [
		id 1
		blueprintsId "3"
		identifier "a34bd61962538ab9a7e7c041d8f9138504036d92"
	]
	node [
		id 2
		blueprintsId "1"
		identifier "a049f20b9b393b1f9d702b5c7c440b1dfc2f02b2"
	]
	node [
		id 3
		blueprintsId "0"
		identifier "root"
	]
	node [
		id 4
		blueprintsId "7"
		identifier "267aafec09e34f289fe9ca9e149ca7f55035bc7a"
	]
	node [
		id 5
		blueprintsId "5"
		identifier "257c8cb9a7eb5ad4740b970bf4e4f901b98042ef"
	]
	node [
		id 6
		blueprintsId "9"
		identifier "02284b8722378a8850e204ffd396bd2f12e3f91f"
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
