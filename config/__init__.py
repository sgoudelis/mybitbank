MainConfig = {
              'globals' : {
                    'site_brand': "MyBitBank"
               },
                  
              'site_sections' : [
                    {'name': 'dashboard', 'path':"/dashboard", 'title': 'Dashboard'},
                    {'name': 'accounts', 'path':"/accounts", 'title': 'Accounts', 'subsections': 
                     [
                         {'name': 'all', 'path':"/accounts", 'title': 'All'},
                         {'name': 'add', 'path':"/accounts/create", 'title': 'Create account'},
                         {'name': 'details', 'path':"/accounts/details", 'title': 'Account details'},
                     ]
                    },
                    {'name': 'transactions', 'path':"/transactions/1", 'title': "Transactions", 'subsections':
                     [
                         {'name': 'all', 'path':"/transactions/", 'title': 'All'},
                         {'name': 'pages', 'path':"/transactions/1", 'title': 'Pages'},
                     ]
                    },
                    {'name': 'transfer', 'path':"/transfer", 'title': "Transfer", 'subsections': 
                     [
                         # {'name': 'transfer', 'path':"/transfer/", 'title': 'All transactions'}
                     ]
                    },
                    {'name': 'addressbook', 'path':"/addressbook", 'title': "Addressbook", 'subsections': 
                     [
                        {'name': 'add', 'path':"/addressbook/add", 'title': 'Add address'},
                     
                     ]},
               ]
              }