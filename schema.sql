drop table if exists entries;
create table entries (
  id integer primary key autoincrement,
  category text not null,
  priority integer not null,
  description text not null
);


