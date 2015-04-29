DROP TABLE IF EXISTS SpecData;

CREATE TABLE SpecData (
	SpecID integer PRIMARY KEY NOT NULL,
	xdata text,
	ydata text,
	Doping text,
	Temperature real,
	Time datetime,
	BiasVolt real,
	Current real,
	Resolution real,
	ExclusionFlag integer,
	TopoID integer
);

DROP TABLE IF EXISTS GapData;

CREATE TABLE GapData (
	SpecID integer PRIMARY KEY NOT NULL,
	GapSize real,
	BoxcarWidth real,
	FOREIGN KEY (SpecID) REFERENCES SpecData(SpecID)
);

DROP TABLE IF EXISTS AveSpec;

CREATE TABLE AveSpec (
	AveID integer PRIMARY KEY NOT NULL,
	NumAveraged integer,
	GapMin real,
	GapMax real,
	xdata text,
	ydata text
);

DROP TABLE IF EXISTS SpecAvePair;

CREATE TABLE SpecAvePair (
	SpecID integer,
	AveID integer,
	FOREIGN KEY (SpecID) REFERENCES SpecData(SpecID),
	FOREIGN KEY (AveID) REFERENCES AveSpec(AveID)
);

DROP TABLE IF EXISTS TopoData;

CREATE TABLE TopoData (
	TopoID integer PRIMARY KEY NOT NULL,
	TopoImg blob
);