CREATE TABLE imported_private_key
(
    id   integer not null
        constraint imported_private_key_pk
            primary key autoincrement,
    seed blob    not null,
    memo text
);

CREATE TABLE address_memo
(
    "index" integer not null
        constraint address_memo_pk
            primary key,
    memo    text
);

CREATE TABLE master_wallet_key
(
    key blob not null
);

CREATE TABLE master_seed
(
    seed blob not null
);

CREATE TABLE salt
(
    salt blob not null
);

CREATE TABLE record
(
    id          integer not null
        constraint record_pk
            primary key autoincrement,
    height      integer not null,
    ciphertext  blob    not null,
    "index"     integer,
    imported_id integer
        constraint record_imported_private_key_id_fk
            references imported_private_key,
    spent       boolean not null default false
);

CREATE TABLE transition_index
(
    transition_id blob    not null
        constraint transition_nonce_pk
            primary key,
    "index"       integer not null
);

CREATE TABLE max_used_index
(
    "index" integer not null
);

CREATE INDEX record_index_idx
    ON record ("index");

CREATE INDEX record_imported_id_idx
    ON record (imported_id);

CREATE TABLE version
(
    version integer not null
);

INSERT INTO version (version)
VALUES (1);

INSERT INTO max_used_index ("index")
VALUES (0);
