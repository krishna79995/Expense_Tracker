CREATE database expensedatabase;

USE expensedatabase;


create table users(id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(255) UNIQUE, password VARCHAR(255));
select* from users;

create table expenses(name varchar(20) not null,  category varchar(20) not null, amount float not null,username varchar(20), foreign key (username) references users(username)  );
select* from expenses;	