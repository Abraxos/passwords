import click
import psycopg2
import re
from psycopg2.sql import SQL, Literal
from pathlib import Path
from hashlib import sha512


def walk(root_dir: Path, function):
    for path in root_dir.iterdir():
        if path.is_dir():
            walk(path, function)
        else:
            function(path)


def sha512_hash(string):
    m = sha512()
    m.update(string.encode('utf-8'))
    return m.hexdigest()


def best_effort_bytes2str(byte_string):
    return "".join(map(chr, byte_string))


def insert_account_password(cursor, account, password):
    sha = sha512_hash(password)
    q = SQL("INSERT INTO passwords.account_passwords(acct_name, password, "
            "passwd_hash) VALUES ({0}, {1}, {2})").format(Literal(account),
                                                          Literal(password),
                                                          Literal(sha))
    cursor.execute(q)


def account_passwords_to_database(acct_psswd_pairs,
                                  db_name, user,
                                  host, password):
    conn = psycopg2.connect("dbname='{}' user='{}' host='{}' password='{}'"
                            .format(db_name, user, host, password))
    cursor = conn.cursor()
    for acct, passwd in acct_psswd_pairs:
        acct = best_effort_bytes2str(acct)
        passwd = best_effort_bytes2str(passwd)
        insert_account_password(cursor, acct, passwd)
    conn.commit()
    conn.close()


def separators_in_line(separators, line):
    # Returns the separator if there is only one separator in a given string
    return {separator: line.count(separator)
            for separator in separators if line.count(separator)}


def no_separators(line):
    return not any(s in line for s in {b':', b';', b'/'})


PASSWD_PAT = re.compile(b'(.*\@.*\..+?)[\:\\\;](.*)')
# a common mistake is switching email and password
EMAIL_PASSWD_SWITCH_PAT = re.compile(b'(.*)[\:\\\;](.*\@.*\..+?)')
# apparently a common mistake is putting a comma in the email address
EMAIL_WITH_COMMA_PAT = re.compile(b'(.*\@.+\,.+?)[\:\\\;](.*)')


def username_passwd_from_line(line):
    normal_match = PASSWD_PAT.match(line)
    if normal_match:
        return normal_match.groups()
    email_with_comma_match = EMAIL_WITH_COMMA_PAT.match(line)
    if email_with_comma_match:
        # someone accidentally wrote an email address with a comma
        username, password = email_with_comma_match.groups()
        username.replace(b',', b'.')
        return username, password
    email_passwd_switched_match = EMAIL_PASSWD_SWITCH_PAT.match(line)
    if email_passwd_switched_match:
        password, username = email_passwd_switched_match\
                             .groups()
        username.replace(b',', b'.', 1)
        return username, password
    if no_separators(line):
        # its just a username
        return line, b''
    return None, None


def process_acct_passwd_file(batch_size, separators, db_name, user, host,
                             password, path):
    print("Processing: {}".format(str(path)))
    batch_count = 0
    total_count = 0
    invalid_count = 0
    valid_count = 0
    with path.open('rb') as f:
        pairs = []
        for i, line in enumerate(f):
            line = line[:-1]  # strip the EOL character
            username, passwd = username_passwd_from_line(line)
            if username:
                pairs.append((username, passwd))
                valid_count += 1
            else:
                invalid_count += 1
            if i % batch_size == 0:
                batch_count += 1
                print("Uploading Batch {}({}) entries..."
                      .format(batch_count, len(pairs)))
                account_passwords_to_database(pairs, db_name, user, host,
                                              password)
                total_count += len(pairs)
                print("Batch {} uploaded! Total ({})"
                      .format(batch_count, total_count))
                pairs = []
    print("Uploading Batch {}({}) entries...".format(batch_count + 1,
                                                     len(pairs)))
    account_passwords_to_database(pairs, db_name, user, host, password)
    total_count += len(pairs)
    print("Batch {} uploaded! Total ({})".format(batch_count, total_count))
    total = valid_count + invalid_count
    percent_valid = (valid_count / total) * 100.0
    percent_invalid = (invalid_count / total) * 100.0
    print("Valid: {}({}%) / Invalid: {}({}%)".format(valid_count,
                                                     percent_valid,
                                                     invalid_count,
                                                     percent_invalid))
    return valid_count, invalid_count


@click.command()
@click.option('--batch-size', default=500)
@click.option('--dbname', default='passwords')
@click.argument('import_directory', type=click.Path(exists=True,
                                                    file_okay=False,
                                                    dir_okay=True,
                                                    readable=True,
                                                    resolve_path=True))
@click.argument('db_username')
@click.argument('db_password')
@click.argument('db_host')
def import_breach_compilation(batch_size, import_directory, dbname,
                              db_username, db_password, db_host):
    import_directory = Path(import_directory)
    print("Importing all accounts/passwords from: {}".format(import_directory))
    invalid_count = 0
    valid_count = 0
    for path in import_directory.rglob('*'):
        if not path.is_dir():
            v, i = process_acct_passwd_file(batch_size, (b';', b':'),
                                            dbname, db_username, db_host,
                                            db_password, path)
            valid_count += v
            invalid_count += i
    total = valid_count + invalid_count
    percent_valid = (valid_count / total) * 100.0
    percent_invalid = (invalid_count / total) * 100.0
    print("TOTAL: Valid: {}({}%) / Invalid: {}({}%)".format(valid_count,
                                                            percent_valid,
                                                            invalid_count,
                                                            percent_invalid))


def main():
    import_breach_compilation()


if __name__ == '__main__':
    main()
