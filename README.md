installer-firstboot
===================

Abiquo configuration tool for post-installation settings,
should be run at first boot.

Uses newt/snack for a ncurses interface.

profiles:

##monolithic
['abiquo-monolithic']

##remote services
['abiquo-distributed', 'abiquo-remote-services']

##server
['abiquo-distributed', 'abiquo-server']

##api
['abiquo-distributed', 'abiquo-standalone-api']

##api
['abiquo-distributed', 'abiquo-ui']
