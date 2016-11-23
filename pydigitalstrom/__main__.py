# -*- coding: UTF-8 -*-
from clint.textui import puts, prompt, colored

from pydigitalstrom.authorization import DigitalStromAuthentication


def main():
    puts(colored.green('---------------------'))
    puts(colored.green('Generate an application token to '
                       'access your digitalSTROM API'))
    puts(colored.green('Username and password will not be stored'))
    puts(colored.green('---------------------'))
    puts('')
    puts(colored.yellow('Please enter the URL to your digitalSTROM server '
                        '(e.g. https://myserver.com:8080), your username and '
                        'password'))
    host = prompt.query('Hostname:')
    username = prompt.query('Username:')
    password = prompt.query('Password:')

    dsauth = DigitalStromAuthentication(host)
    apptoken = dsauth.getApplicationToken()
    temptoken = dsauth.getTempToken(username, password)
    if dsauth.activateApplicationToken(apptoken, temptoken):
        puts('')
        puts(colored.green('Your application token is activated:'))
        puts(colored.green(apptoken))
    else:
        puts(colored.red('Application token could not be activated'))


if __name__ == "__main__":
    main()
