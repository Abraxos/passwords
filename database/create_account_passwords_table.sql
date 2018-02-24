CREATE TABLE passwords.account_passwords
(
    account_id bigint NOT NULL DEFAULT nextval('passwords.account_passwords_account_id_seq'::regclass),
    name text COLLATE pg_catalog."default" NOT NULL,
    password text COLLATE pg_catalog."default" NOT NULL,
    sha512 character varying(128) COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT account_passwords_pkey PRIMARY KEY (account_id, sha512)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;