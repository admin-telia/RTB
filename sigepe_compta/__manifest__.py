{
    'name' : 'Gestion Comptable',
    'author' : 'Telia Informatique',
    'version' : "1.0",
    'depends' : ['base','sigepe_budget'],
    'description' : 'Gestion de la comptabilit√© RTB',
    'summary' : "Gestion de la Comptabilit√© RTB",
    'data' : ['views/typec.xml', 'views/compta.xml', 'views/report_compta.xml', 'data/compta_data.xml', 'security/ir.model.access.csv', 'security/compta_security.xml',],
    'installable' : True,
    'auto_install' : False,
}
