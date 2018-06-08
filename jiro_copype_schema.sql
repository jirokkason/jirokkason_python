--コマンドラインでsqlite3 "DB名".dbと入力
--sqliteに入り、.read schema.sqlと実行
drop table if exists jiro_copype;
create table jiro_copype (
    id integer primary key autoincrement not null,
    title varchar(255),
    body text not null,
    url text
);