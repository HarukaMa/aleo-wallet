create table record_index
(
    id           integer           not null
        constraint record_index_pk
            primary key autoincrement,
    block_height integer           not null,
    public_owner boolean default 0 not null,
    owner        blob              not null,
    nonce        blob              not null
);

create table full_record
(
    id       integer not null
        constraint full_record_pk
            primary key autoincrement,
    index_id integer not null
        constraint full_record_record_index_id_fk
            references record_index,
    record   blob    not null
);

create table serial_number
(
    sn     blob    not null
        constraint serial_number_pk
            primary key,
    height integer not null
);

create index record_index_owner_index
    on record_index (owner);

create table version
(
    version integer not null
);

insert into version (version)
values (1);