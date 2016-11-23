# -*- coding: UTF-8 -*-
from clint.textui import puts, prompt

from pydigitalstrom.authorization import DigitalStromAuthentication


def main():
    puts('---------------------')
    puts('Generate an application token to access your digitalSTROM API')
    puts('Username and password will not be stored')
    puts('---------------------')
    puts('')
    host = prompt.query(
        'Please enter the hostname/ip')
    username = prompt.query(
        'Please enter the username')
    password = prompt.query(
        'Please enter the password')

    dsauth = DigitalStromAuthentication(host)
    apptoken = dsauth.getApplicationToken()
    temptoken = dsauth.getTempToken(username, password)
    if dsauth.activateApplicationToken(apptoken, temptoken):
        puts('Your application token is activated:')
        puts(apptoken)
    else:
        puts('Application token could not be activated')


if __name__ == "__main__":
    main()
