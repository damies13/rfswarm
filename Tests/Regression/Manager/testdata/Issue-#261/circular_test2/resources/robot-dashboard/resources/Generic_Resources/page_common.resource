*** Settings ***
Library          SeleniumLibrary    implicit_wait=1s
Library          String
Library          Collections
Library          ../../library/utility.py
Resource         ../../../core-ui/resources/generic-resources/page-common.resource
Resource         ../../../core-ui/resources/generic-resources/ui-common.resource
Resource         ../../../core-ui/resources/generic-resources/ui-browser.resource
Resource         ../../../core-ui/resources/generic-resources/ui-login.resource
Resource         ../../../core-ui/resources/generic-resources/ui-notif-handling.resource
Resource         ../../../core-ui/resources/generic-resources/ui-sf-menu.resource
Resource         ../../../core-ui/resources/generic-resources/ui-vis-change.resource
Resource         ../../../core-ui/resources/generic-resources/ui-vis-lists.resource
Resource         ../../../core-ui/resources/generic-resources/ui-vis-tables.resource