CREATE ROLE api_user WITH LOGIN ENCRYPTED PASSWORD 'api$pass';

CREATE TABLE IF NOT EXISTS predict_logs
(
	TS TIMESTAMP DEFAULT now(),
	f1 FLOAT NOT NULL,
	f2 FLOAT NOT NULL,
	f3 VARCHAR(1),
	predict INT NOT NULL
);

CREATE TABLE IF NOT EXISTS predict_logs_cnt
(
	f3 VARCHAR(1),
	cnt INT,
	CONSTRAINT predict_logs_cnt_PK PRIMARY KEY (f3)
);

CREATE TABLE IF NOT EXISTS predict_err_logs
(
	TS TIMESTAMP DEFAULT now(),
	f1 VARCHAR(255) NOT NULL,
	f2 VARCHAR(255) NOT NULL,
	f3 VARCHAR(255)  NOT NULL,
	err VARCHAR(500) NOT NULL
);

CREATE TABLE IF NOT EXISTS "user"
(
	ID SERIAL NOT NULL,
	Full_name VARCHAR(255) NOT NULL,
	CONSTRAINT user_PK PRIMARY KEY (ID)
);

CREATE TABLE IF NOT EXISTS login_user
(
	User_ID INT NOT NULL,
	Token VARCHAR(500) NOT NULL,
	CONSTRAINT login_user_PK PRIMARY KEY (User_ID),
	CONSTRAINT login_user_user_ID FOREIGN KEY (User_ID)
	  REFERENCES "user" (ID)
);
CREATE INDEX IDX_login_user_token ON login_user USING Hash (Token);

-- ""user""
INSERT INTO "user" (Full_name ) VALUES	('Test User 1'), ('Test User 2');

-- login_user
INSERT INTO login_user VALUES (1, 'tokenTest1'), (2,'tokenTest2');
	
INSERT INTO predict_logs_cnt
	VALUES ('',0),('A',0),('B',0),('C',0),('D',0),('E',0);

GRANT SELECT, INSERT ON ALL TABLES IN SCHEMA public TO api_user;
GRANT UPDATE ON predict_logs_cnt TO api_user;