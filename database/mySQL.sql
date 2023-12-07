create table request(
	ID int not null,
	apartment_number int(10) not null,
	area varchar(200) not null,
	description varchar(500) not null,
	request_time timestamp not null,
	image_path varchar(100),
	status varchar(10) check(status IN('pending', 'completed')) not null,
	primary key (ID)
);

create table tenant(
	ID int not null,
	name varchar(100) not null,
	phone_number varchar(11) not null,
	email varchar(50) not null,
	check_in timestamp not null,
	check_out timestamp,
	apartment_number int not null,
	primary key (ID)
);