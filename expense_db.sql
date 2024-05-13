CREATE database expensedatabase;

USE expensedatabase;


create table users(id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(255) UNIQUE, password VARCHAR(255));
select* from users;

create table expenses(id INT AUTO_INCREMENT PRIMARY KEY,name varchar(20) not null,  category varchar(20) not null, amount float not null,username varchar(20), expense_date date ,foreign key (username) references users(username)  );
select* from expenses;	
select* from expense_shares;
select* from group_members;
select* from group1;
drop table expenses;
drop table expense_shares;
drop table group_members;
drop table group1;
show tables;
CREATE TABLE IF NOT EXISTS group1
                     (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255) UNIQUE);
CREATE TABLE expenses(id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255),category varchar(20) ,amount DECIMAL(10, 2),username varchar(20), expense_date DATE, group_id INT,
                     FOREIGN KEY (group_id) REFERENCES group1(id),foreign key (username) references users(username)  );
CREATE TABLE IF NOT EXISTS group_members
                     (id INT AUTO_INCREMENT PRIMARY KEY, group_id INT, name VARCHAR(255),
                     FOREIGN KEY (group_id) REFERENCES group1(id));
CREATE TABLE IF NOT EXISTS expense_shares
                     (id INT AUTO_INCREMENT PRIMARY KEY, expense_id INT, name VARCHAR(255),
                     share_amount DECIMAL(10, 2), FOREIGN KEY (expense_id) REFERENCES expenses(id));