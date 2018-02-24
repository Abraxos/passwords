# Passwords

A database schema, webapp, and utilities for searching, managing, and checking inclusion in a set of passwords known to hackers

At some point a while back, hackers dumped a ton of passwords from multiple breaches online. These passwords, some 1.5 billion of them, are now publicly available and should be considered unusable.

The goal of this webapp is to provide a simple and relatively secure interface to checking whether a particular password already exists in this data set. The goal being that if it already exists, a potential account creator should not be allowed to use it and should be warned that this particular password has been compromised. The ideal use-case for this webapp is that it be run on a server that can only be accessed from your private network and the server used to create accounts on your system has a certificate and is able to make calls out to this webapp to check passwords before permitting clients to use them.

## Warning

Please be advised that there are multiple security concerns and caveats that need to be addressed before using this webapp:

1) The passwords are hashed using SHA512 before being sent to the database for verification, that way, you're not sending passwords to the webapp server for casual checks. That being said, this should only be done on a secure connection. As a result, this webapp is designed to work ONLY over HTTPS and uses both server and client-side verification. This means that both the server and the client must have valid certificates from some certificate authority.
2) This database can definitely be used for evil. Don't. You've been warned. You will be caught, and you will go to jail. If you think you won't, you will _definitely_ get caught.
3) It should only ever run on your private network exposed only to trusted servers.


## The WebApp

The webapp is based on flask and gunicorn with client-side-certificate verification. It is installed with `pip` and is therefore accessible as `passwords-webapp` in the shell thereafter.

## Utilities

**`database/import_passwords.py`** - Designed to import passwords from a directory of files where every line is of the pattern: `username:password`. This utility allows you to import a database dump into the database schema for use by this webapp.
**`passwords-webapp <CONFIG FILE>`** - Runs the webapp in a gunicorn server. See `passwords-webapp --help`.