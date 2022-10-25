from odoo import fields,api,models
from datetime import datetime
from email.policy import default


#les elements de GRH 

#Creation de la classe classe avec ses attributs      
class HrClasse(models.Model):
    _name = "hr_classe"
    _order = 'sequence, id'
    sequence = fields.Integer(help="Gives the sequence when displaying a list of classe.", default=10) 
  
    name = fields.Char(string = "Libéllé long", required = True)
    libcourt = fields.Char(string = "Libéllé court", required = True)
    description = fields.Text(string = "Description")
    company_id = fields.Many2one('res.company',string = "Structure", default=lambda self: self.env.user.company_id.id)
    active = fields.Boolean(string = "Etat", default=True)
  
#Creation de la classe categorie avec ses attributs   
class HrCategorie(models.Model):
    _name = "hr_categorie"
    _order = 'sequence, id'
    sequence = fields.Integer(help="Gives the sequence when displaying a list of categorie.", default=10) 
  
    name = fields.Char(string = "Libéllé long", required = True)
    libcourt = fields.Char(string = "Libéllé court",  required = True)
    description = fields.Text(string = "Description")
    company_id = fields.Many2one('res.company',string = "Structure", default=lambda self: self.env.user.company_id.id)
    active = fields.Boolean(string = "Etat", default=True)
  
#Creation de la classe echelle avec ses attributs     
class HrEchelle(models.Model):
    _name = "hr_echelle"
    _order = 'sequence, id'
    sequence = fields.Integer(help="Gives the sequence when displaying a list of echelle.", default=10) 
  
    name = fields.Char(string = "Libéllé long", required = True)
    libcourt = fields.Char(string = "Libéllé court", required = True)
    description = fields.Text(string = "Description")
    company_id = fields.Many2one('res.company',string = "Structure", default=lambda self: self.env.user.company_id.id)
    active = fields.Boolean(string = "Etat", default=True)

#Creation de la classe echellon avec ses attributs     
class HrEchellon(models.Model):
    _name = "hr_echellon"
    _order = 'sequence, id'
    sequence = fields.Integer(help="Gives the sequence when displaying a list of echelon.", default=10) 
  
    name = fields.Char(string = "Libéllé long", required = True)
    libcourt = fields.Char(string = "Libéllé court",required = True)
    description = fields.Text(string = "Description")
    company_id = fields.Many2one('res.company',string = "Structure", default=lambda self: self.env.user.company_id.id)
    active = fields.Boolean(string = "Etat", default=True)
    
#Creation de la classe zone avec ses attributs        
class HrZone(models.Model):
    _name = "hr_zone"
    name = fields.Char(string = "Libéllé long", required = True)
    libcourt = fields.Char(string = "Libéllé court", required = True) 
    description = fields.Text(string = "Description") 
    company_id = fields.Many2one('res.company',string = "Structure", default=lambda self: self.env.user.company_id.id)
    active = fields.Boolean(string = "Etat", default=True)
    
#Creation de la classe diplôme avec ses attributs        
class HrDiplome(models.Model):
    _name = "hr_diplome"
    name = fields.Char(string = "Libéllé long", required = True)
    libcourt = fields.Char(string = "Libéllé court", required = True) 
    active = fields.Boolean(string = "Etat", default=True)
    
#Creation de la classe typeindemnite avec ses attributs     
class HrTypeIndemnite(models.Model):
    _name = "hr_typeindemnite"
    _rec_name = "concat_fields"
    concat_fields = fields.Char(compute = "_concat_type")
    name = fields.Char(string = "Libéllé long", required = True)
    code = fields.Char(string = "Code", required = True)
    libcourt = fields.Char(string = "Libéllé court", required = True) 
    description = fields.Text(string = "Description") 
    active = fields.Boolean(string = "Etat", default=True)
    
    #fonction de concatenation
    @api.depends('code','name')
    def _concat_type(self):
      for tests in self:
        tests.concat_fields = (tests.code or '')+' '+(tests.name or '')
        

#Creation de la classe type pièce    
class HrTypePiece(models.Model):
    _name = "hr_typepiece"
    _order = 'sequence, id'
    sequence = fields.Integer(help="Gives the sequence when displaying a list of type pièce.", default=10) 
    name = fields.Char(string = "Libéllé court", required = True)
    lib_long = fields.Char(string = "Libellé long", size = 35, required = True)
    company_id = fields.Many2one('res.company',string = "Structure", default=lambda self: self.env.user.company_id.id)
    active = fields.Boolean(string = "Etat", default=True) 
    
    
#Creation de la classe grille des fonctionnaires du burkina faso avec ses attributs  
class HrGrilleSalarialeFonctionnaire(models.Model):
    _name = "hr_grillesalariale"
    _rec_name = "x_salbase"
    x_class_id = fields.Many2one('hr_classe', string='Classe', required=True)
    x_categorie_id = fields.Many2one('hr_categorie', string='Catégorie', required=True)        
    x_echelle_id = fields.Many2one('hr_echelle', string='Echelle', required=True)    
    x_echellon_id = fields.Many2one('hr_echellon', string='Echelon', required=True)
    x_indice = fields.Float(string = "Indice", required=True) 
    x_point_indiciaire = fields.Float(string = "Point Indiciare", default = "2331", required=True) 
    x_salbase = fields.Float(string = "Solde indiciaire", required=True)
    #company_id = fields.Many2one('res.company',string = "Structure", default=lambda self: self.env.user.company_id.id)
    #x_exercice_id = fields.Many2one('ref_exercice', default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]))
    active = fields.Boolean(string = "Etat", default=True)
    
    #fonction de calcul du salaire de base en fonction du point indiciare et de l'indice du onctionnaire
    @api.onchange('x_indice', 'x_point_indiciaire')
    def onchange_field(self):
        for v in self:
            if v.x_indice or v.x_point_indiciaire:
                v.x_salbase = round((v.x_indice * v.x_point_indiciaire)/12)
                
    

#Creation de la classe categorie de l'employé avec ses attributs     
class HrCategorieEmploye(models.Model):
    _name = "hr_catemp"
    name = fields.Char(string = "Libéllé long", required = True)
    lib_court = fields.Char(string = "Libéllé court", required = True) 
    active = fields.Boolean(string = "Etat", default=True)
    
    






class RefContinent(models.Model):
    _name = "ref_continent"
    _order = 'sequence, id'
    sequence = fields.Integer(help="Gives the sequence when displaying a list of continent.", default=10)
    name = fields.Char(string = "Libéllé long", required = True,size = 65)
    libcourt = fields.Char(string = "Libéllé court", required= True)
    code_continent = fields.Char(string = "Code",required = True,size = 2)
    description = fields.Text(string = "Description")

    _sql_constraints = [('code_continent_unique', 'unique(code_continent)', 
                     'Ce code d identification du continent existe dejà, svp entrer un autre code')]
    
     
class RefPays(models.Model):
    _name = "ref_pays"
    _order = 'sequence, id'
    sequence = fields.Integer(help="Gives the sequence when displaying a list of Pays.", default=10)
    country_id = fields.Many2one('res.country', string = 'Nationalité (Pays)', groups="hr.group_hr_user")
    name = fields.Char(string = "Libéllé court", required = True, size = 35)
    lib_long = fields.Char(string = "Libéllé long", required = True)
    ref_continent_id = fields.Many2one('ref_continent', string = 'Continent')
    code_pays = fields.Char(string = "Code",required = True, size = 2)

    _sql_constraints = [('code_pays_unique', 'unique(code_pays)', 
                     'Ce code d identification du pays existe dejà, svp entrer un autre code')]
   
    
class RefRegion(models.Model):
    _name = "ref_region"
    _order = 'sequence, id'
    sequence = fields.Integer(help="Gives the sequence when displaying a list of region.", default=10)
    name = fields.Char(string = "Libéllé long", required = True)
    libcourt = fields.Char(string = "Libéllé court", size = 35, required= True)
    ref_pays_id = fields.Many2one('res.country', string = 'Pays')
    code_region = fields.Char(string = "Code",required = False,size = 2)
    ref_region_ids = fields.One2many("ref_region_line","ref_region_id")
    _sql_constraints = [('code_region_unique', 'unique(code_region)', 
                     'Ce code d identification de region existe dejà, svp entrer un autre code')]



class refRegionLine(models.Model):
    _name = "ref_region_line"
    ref_region_id = fields.Many2one("ref_region")
    ref_province_id = fields.Many2one("ref_province",string = "Ajouter les provinces liées a cette région")
    ref_code_province = fields.Char(string = "Code")
 

    
    
class RefProvince(models.Model):
    _name = "ref_province"
    _order = 'sequence, id'
    sequence = fields.Integer(help="Gives the sequence when displaying a list of Province.", default=10)
    name = fields.Char(string = "Libéllé long", required = True)
    libcourt = fields.Char(string = "Libéllé court", required= True, size = 35)
    chef_lieu = fields.Char(string = "Chef lieu")
    code_province = fields.Char(string = "Code",required = True, size = 2) 
    ref_region_id = fields.Many2one('ref_region', string = 'Région')
    _sql_constraints = [('code_province_unique', 'unique(code_province)', 
                     'Ce code d identification de province existe dejà, svp entrer un autre code')]

    
class RefDepartement(models.Model):
    _name = "ref_departement"
    _order = 'sequence, id'
    sequence = fields.Integer(help="Gives the sequence when displaying a list of departement.", default=10)
    name = fields.Char(string = "Libéllé long", required = True)
    libcourt = fields.Char(string = "Libéllé court",size = 35, required= True)
    ref_province_id = fields.Many2one('ref_province', string = 'Province') 
    code_dep = fields.Char(string = "Code",required = True, size = 2)
    _sql_constraints = [('code_dep_unique', 'unique(code_dep)', 
                     'Ce code d identification de departement existe dejà, svp entrer un autre code')]


    
class RefCommune(models.Model):
    _name = "ref_commune"
    _order = 'sequence, id'
    sequence = fields.Integer(help="Gives the sequence when displaying a list of commune.", default=10)
    name = fields.Char(string = "Libéllé long", required = True)
    libcourt = fields.Char(string = "Libéllé court", required= True, size = 35)
    ref_departement_id = fields.Many2one('ref_departement', string = 'Département') 
    ref_province_id = fields.Many2one('ref_province', string = 'Province') 
    code_commune = fields.Char(string = "Code",required = True)
    _sql_constraints = [('code_commune_unique', 'unique(code_commune)', 
                     'Ce code d identification de commune existe dejà, svp entrer un autre code')]


    
class RefLocalite(models.Model):
    _name = "ref_localite"
    _order = 'sequence, id'
    sequence = fields.Integer(help="Gives the sequence when displaying a list of localité.", default=10)
    name = fields.Char(string = "Libéllé long", required = True)
    libcourt = fields.Char(string = "Libéllé court", required= True, size = 35)
    ref_departement_id = fields.Many2one('ref_departement', string = 'Département') 
    ref_province_id = fields.Many2one('ref_province', string = 'Province') 
    code_localite = fields.Char(string = "Code",required = True)
    _sql_constraints = [('code_localite_unique', 'unique(code_localite)', 
                     'Ce code d identification de localité existe dejà, svp entrer un autre code')]



class RefCategorieStructure(models.Model):
    
    _name = "ref_categorie_structure"
    _order = 'sequence, id'
    sequence = fields.Integer(help="Gives the sequence when displaying a list of cat.Struct.", default=10)
    code_cat_struct = fields.Char(string = 'Code',size = 6, required = True)
    abreg = fields.Char(string = "Abrégé")
    name = fields.Char(string = "Libellé long", required = True)
    lib_court = fields.Char(string = "Libellé court", required= True, size = 35)
    type_struct= fields.Many2one("ref_type_structure", string= "Type structure", required= False)
    _sql_constraints = [('code_cat_struct_unique', 'unique(code_cat_struct)', 
                     'Ce code d identification de categorie structure existe dejà, svp entrer un autre code')]



class RefTypeStructure(models.Model):
    
    _name = "ref_type_structure"
    _order = 'sequence, id'
    sequence = fields.Integer(help="Gives the sequence when displaying a list of type structure.", default=10)
    code= fields.Char(string= "Code", required= True, size=4)
    name = fields.Char(string = "Libellé long", required = True)
    lib_court = fields.Char(string = "Libellé court", required= True, size = 35)
    ministere= fields.Many2one("ref_ministere", required= False, string= "Ministère")
    actif = fields.Boolean() 
    #code_type_struct = fields.Char(string = 'Code',size = 2,required = True)
    



class RefProfilStructure(models.Model):
    
    _name = "ref_profil_structure"
    _order = 'sequence, id'
    sequence = fields.Integer(help="Gives the sequence when displaying a list of profil strucutre.", default=10)
    name = fields.Char(string = "Libellé long", required = True)
    lib_court = fields.Char(string = "Libellé court", size = 35)
    ref_fonction_id = fields.Many2one('ref_fonction', string = 'Titre responsable') 
    actif = fields.Boolean() 
    ref_employe_id = fields.Many2one('hr.employee', string = 'Nom responsable') 
    code_profil_struct = fields.Char(string = 'Code',size = 2,required = True)
 
#heritage de la classe Company
class ResCompany(models.Model):
    _inherit = 'res.company'
    _order = 'sequence, id'
    sequence = fields.Integer(help="Gives the sequence when displaying a list of strucutre.", default=10)
    ministere= fields.Many2one("ref_ministere", string= "Ministère", required= True) 
    ref_type_struct_id = fields.Many2one('ref_type_structure', string = 'Type Structure', required = True)
    ref_cat_struct_id = fields.Many2one('ref_categorie_structure', string = 'Catégorie Structure', required = True)
    ref_localite_id = fields.Many2one('ref_localite', string = 'Localité', required = True)
    code_struct = fields.Char(string = 'Code',size = 10, required = True) 
    actif = fields.Boolean() 
    """_sql_constraints = [('code_struct_unique', 'unique(code_struct)', 
                     'Ce code d identification de structure existe dejà, svp entrer un autre code')]"""


#classe ministère
class RefMinistere(models.Model):
    _name = 'ref_ministere'
    _order = 'sequence, id'
    sequence = fields.Integer(help="Gives the sequence when displaying a list of ministere.", default=10) 
    name = fields.Char(string = "Libéllé court", size = 35,required = True)
    code_ministere = fields.Char(string = 'Code',size = 2,required = True)
    lib_long = fields.Char(string = "Libellé long", required= True)
    x_structure_id = fields.Many2one('res.company', string = 'Structure')
    active = fields.Boolean(string = "Etat", default=True) 
    
    
class RefNationalite(models.Model):
    _name = "ref_nationalite"
    _order = 'sequence, id'
    sequence = fields.Integer(help="Gives the sequence when displaying a list of Poste.", default=10)
    name = fields.Char(string = "libéllé court", required = True)
    lib_long = fields.Char(string = "Libellé long", required = True)
    code_nationalite = fields.Char(string = 'Code',size = 2,required = True)
    active = fields.Boolean(string = "Etat", default=True)

class RefExercice(models.Model):
    
    _name = "ref_exercice"
    _rec_name = "no_ex"
    _order = 'sequence, id'
    sequence = fields.Integer(help="Gives the sequence when displaying a list of Exercice.", default=10)
    name = fields.Char(string = "Libellé long", required = True,size = 65)
    no_ex = fields.Integer(string = "Exercice", required = True)
    lib_court = fields.Char(string = "Libellé court", required= True, size = 35)
    code_exo_struct = fields.Char(string = 'Code',size = 2,required = True) 
    etat = fields.Selection([
        (1,'Y'),
        (2,'N'),
         
        ], string = "Etat", default=1)
    
class HrUsers(models.Model):
    
    _inherit = "res.users"
    x_exercice_id = fields.Many2one('ref_exercice',string = 'Choisir Exercice', default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]))
    x_service_id = fields.Many2one('ref_service', string='Service')

#Creation de la classe direction avec ses attributs 
class RefDirection(models.Model):
    _name = "ref_direction"
    code = fields.Char("Code", required= True)
    name = fields.Char(string = "Libéllé long", required = True)
    libcourt = fields.Char(string = "Libéllé court", required = True, size = 35) 
    company_id = fields.Many2one('res.company',string = "Structure", default=lambda self: self.env.user.company_id.id)
    active = fields.Boolean(string = "Etat", default=True)


#Creation de la classe service avec ses attributs 
class RefService(models.Model):
    _name = "ref_service"
    x_direction_id = fields.Many2one('ref_direction', string = "Direction", required = True)
    code = fields.Char(string='Code', required=True, size = 65)
    name = fields.Char(string = "Libéllé long", required = True)
    libcourt = fields.Char(string = "Libéllé court", required = True, size = 35) 
    company_id = fields.Many2one('res.company',string = "Structure", default=lambda self: self.env.user.company_id.id)
    active = fields.Boolean(string = "Etat", default=True)
    
 
 
#Creation de la classe service liee a une direction avec ses attributs 
"""class RefServiceDirection(models.Model):
    _name = "ref_servicedirection"
    name = fields.Many2one('ref_direction', string = "Direction", required = True)
    x_service_ids = fields.Many2many('ref_service','ref_service_direction_id', string = "Service", required = True)
    company_id = fields.Many2one('res.company',string = "Structure", default=lambda self: self.env.user.company_id.id)
    active = fields.Boolean(string = "Etat", default=True)"""
    #x_lines_ids = fields.One2many('ref_service_line', 'x_service_id', string = "Ajout des services ")
   
#Creation de la classe service liee a une direction avec ses attributs 
"""class RefServiceLine(models.Model):
    _name = "ref_service_line"
    x_service_id = fields.Many2one('ref_service')
    name = fields.Char(string = "Libéllé long", required = True, size = 65)
    libcourt = fields.Char(string = "Libéllé court", required = True, size = 35) """
    

class RefTypepiece(models.Model):
    _name = "ref_type_piece"
    _order = 'sequence, id'
    sequence = fields.Integer(help="Gives the sequence when displaying a list of type pièce.", default=10)
    name = fields.Char(string = "Libéllé long", required = True)
    libcourt = fields.Char(string = "Libéllé court", required= True, size = 35)
    code_type_piec_struct = fields.Char(string = 'Code',size = 2,required = True)
    description = fields.Text(string = "Description",size = 1000)



class RefSecteurActivite(models.Model):
    _name = "ref_secteur_activite"
    _order = 'sequence, id'
    sequence = fields.Integer(help="Gives the sequence when displaying a list of Activities.", default=10)
    name = fields.Char(string = "Libéllé long", required = True)
    libcourt = fields.Char(string = "Libéllé court", required= True, size = 35)
    code_sect_struct = fields.Char(string = 'Code',size = 2,required = True)
    description = fields.Text(string = "Description",size = 1000)


#heritage de la classe Bank
class ResPartnerBank(models.Model):
    _inherit = 'res.bank' 
    _order = 'sequence, id'
    sequence = fields.Integer(help="Gives the sequence when displaying a list of bank.", default=10)
    
    #_inherit = ['res.partner.bank','res.bank']
    #libelle_banque = fields.Char(string = "Nom banque")
    cd_agence_bceao = fields.Char(string = "Code banque BCEAO") 
    cd_banque_bceao = fields.Char(string = "Code agence BCEAO")
    code_swift = fields.Char(string = "Code SWIFT", required = True)
    sigle = fields.Char(string = "Sigle")
    uemoa = fields.Selection([
        ('uemoa', 'UEMOA'),
        ('hors', 'Hors UEMOA'),
	('local', 'Local'),
    ], string='uemoa', index=True, readonly=False, copy=False, default='uemoa')
    _sql_constraints = [('code_swift_unique', 'unique(code_swift)', 
                     'Ce code SWIFT existe dejà, svp entrer un autre code')]



"""class RefModePaiement(models.Model):
    _name = "ref_mode_paiement"
    name = fields.Char(string = "Libellé long", required = True)
    lib_court = fields.Char(string = "Libellé court")
    encaissement = fields.Boolean(string = "Encaissement") 
    decaissement = fields.Boolean(string = "Décaissement")"""


class RefStructureCompteBanque(models.Model):
    _name = "ref_structcomptebanque"
    name = fields.Many2one('res.company', string = 'Structure', required = True)

    _order = 'sequence, id'
    sequence = fields.Integer(help="Gives the sequence when displaying a list of bank.", default=10)
    
    x_lines_ids = fields.One2many('ref_structcomptebanque_line', 'x_structcomptebanque_id', string = 'Ajout compte')

    
class RefStructureCompteBanqueLine(models.Model):
    _name = "ref_structcomptebanque_line"
    x_structcomptebanque_id = fields.Many2one('ref_structcomptebanque')
    x_banque_id = fields.Many2one('res.bank', string = "Banque", required = True)
    num_compte = fields.Char(string = "Numéro compte", required = True)
    lib_long = fields.Char(string = "Libellé long")
    lib_court = fields.Char(string = "Libellé court")


    
    
class temp_change_exo_user(models.Model):
    _name = "temp_change_exo_user"
    user_id = fields.Integer('res.users', default=lambda self: self.env.user)
    x_exercice_en_cours = fields.Char(string = 'Exercice en cours')
    x_exercices_id = fields.Many2one('ref_exercice',string='Changer Exercice')
    x_datetime = fields.Datetime(string = 'Date Heure', default=fields.Datetime.now)    
    #@api.onchange('x_exercice_temp_idd')
    def changer_exercice(self):
        #formatage de l'utilisateur en cours
        cd_user = int(self.user_id)
        #recuperation de l'id de l'exercice qu'il va selectionné dans le comba 
        nox = int(self.x_exercices_id)
        #Mise à jour de la table user avec les informations telles que no_ex et le id de l'exercice selectionné precedemment
        self.env.cr.execute("UPDATE res_users SET x_exercice_id = %d WHERE id = %d  " %(nox,cd_user))
        return {
                'type': 'ir.actions.client',
                'tag': 'reload',
                'target' : 'current',
                }
        
    
    
    
    def afficher_exercice_en_cours(self):
        #formatage de l'utilisateur en cours
        cd_user = int(self.user_id)
        self.env.cr.execute("SELECT E.no_ex FROM ref_exercice E, res_users U WHERE E.id = U.x_exercice_id and U.id = %d " %(cd_user))
        res = self.env.cr.fetchone()[0]
        self.x_exercice_en_cours = res
       


class RefCompte(models.Model):
    
    @api.depends('compte','lb_long')
    def _concatenate_cpte(self):
        for test in self:
            test.concate_cpte = str(test.compte)+ " " +str(test.lb_long)
    
        
    _name = "ref_compte"
    _rec_name = 'compte'
    
    concate_cpte = fields.Char(compute='_concatenate_cpte')
    #sous_classe = fields.Many2one("ref_sousclasse_pcg", 'Sous classe')
    cpte = fields.Char("Compte", size=3)
    compte = fields.Char("Comptes", size=3, required= True)
    souscpte = fields.Char("Sous compte")
    lb_court = fields.Char("Libellé court")
    lb_long = fields.Char("Libellé long", required= True)
    fg_sens = fields.Selection([
        ('D', 'Dédit'),
        ('C', 'Crédit'),
        ('M', 'Mixte'),
        ], 'Sens')
    fg_terminal = fields.Boolean('Terminal')
    active = fields.Boolean('Actif',default=True)
    plancompta_id = fields.Many2one('ref_plan_comptable')
    #souscpte_ids = fields.One2many('ref_souscompte', 'cpte_id')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    type_structure = fields.Many2one("ref_type_structure", required=True)
    
    @api.onchange('company_id')
    def test(self):
        if self.company_id:
            self.type_structure = self.company_id.ref_type_struct_id
   
        

class RefPlanCompta(models.Model):
    _name = "ref_plan_comptable"
    _rec_name = "sous_classe_id"

    sous_classe_id = fields.Many2one("ref_sousclasse_pcg","Sous classe")
    compte_ids = fields.One2many('ref_compte','plancompta_id')
    

class RefSousCompte(models.Model):
    
    @api.depends('souscpte','lb_long')
    def _concatenate_souscpte(self):
        for test in self:
            test.concate_souscpte = str(test.souscpte)+ " " +str(test.lb_long)

    _name = "ref_souscompte"
    _rec_name = 'souscpte'
    
    concate_souscpte = fields.Char(compute = '_concatenate_souscpte', store=True)
    souscpte = fields.Char("Sous Compte", required= True)
    lb_long = fields.Char("Libellé long", size=100, required= True)
    lb_court = fields.Char("Libellé court", size=35)
    active = fields.Boolean('Actif',default=True)
    type_struct = fields.Many2one("ref_type_structure", "Type Structure", required=True)
    


class cl_cpt_pcg(models.Model):
    
    @api.depends('cl_cpt_pcg','lb_long')
    def _concatenate_class(self):
        for test in self:
            test.concate_class = str(test.cl_cpt_pcg)+ "-" +str(test.lb_long)


    _name = "ref_classe_pcg"
    _rec_name = 'concate_class'

    concate_class = fields.Char(compute="_concatenate_class")
    cl_cpt_pcg = fields.Char(string="Classe",size=2, required= True)
    name = fields.Char(string="Libellé court", size=25)
    lb_long = fields.Char(string="Libellé long", size=65, required= True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    scl_cpt_pcg_ids = fields.One2many('ref_sousclasse_pcg','cl_cpt_pcg_id', string="Sous compte")
    type_structure = fields.Many2one("ref_type_structure", "Type Structure")

class Scl_cpt_pcg(models.Model):
    
    @api.depends('scl_cpt_pcg','lb_long')
    def _concatenate_sousclass(self):
        for test in self:
            test.concate_sousclass = str(test.scl_cpt_pcg)+ "-" +str(test.lb_long)

    _name = "ref_sousclasse_pcg"
    _rec_name = 'concate_sousclass'
    
    concate_sousclass = fields.Char(compute="_concatenate_sousclass")
    cl_cpt_pcg_id = fields.Many2one("ref_classe_pcg", "Classe", required= True)
    scl_cpt_pcg = fields.Char(string="Sous classe",size=2, required= True)
    name = fields.Char(string="Libellé court", size=25)
    lb_long = fields.Char(string="Libellé long", size=65, required= True)
    type_structure = fields.Many2one("ref_type_structure", "Type Structure")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    
class RefBanqueAgence(models.Model):
    _name = "ref_banque_agence"
    _rec_name = "lb_long"
    
    banque_id = fields.Many2one('res.bank', 'Banque', required=True)
    code_agence = fields.Char("Code agence", required=True)
    lb_court = fields.Char("Libellé court", required=True)
    lb_long = fields.Char('Libellé long', required=True)
    adresse = fields.Text("Adresse")
    active = fields.Boolean("Actif", default=True)
    



class RefTitre(models.Model):
    @api.depends('cd_titre','lb_long')
    def _concatenate_titre(self):
        for test in self:
            test.titre = str(test.cd_titre)+ " " +str(test.lb_long)

    _name = "ref_titre"
    _rec_name = 'cd_titre'

    sequence = fields.Integer(default=10)
    titre = fields.Char("Titre", compute="_concatenate_titre")
    cd_titre = fields.Char(string = "Titre",size=2, required=True)
    lb_court = fields.Char(string = "Libellé court", required=True)
    lb_long = fields.Char(string = "Libellé long",required=True)
    type_titre = fields.Char("Type de titre", size=1)


class RefSection(models.Model):
    @api.depends('cd_section','lb_long')
    def _concatenate_section(self):
        for test in self:
            test.section = str(test.cd_section)+ " " +str(test.lb_long)

    _name = "ref_section"
    _rec_name = "cd_section"
    
    sequence = fields.Integer(default=10)
    section = fields.Char("Section", compute="_concatenate_section")
    cd_section = fields.Char(string = "Section",required=True)
    lb_court = fields.Char(string = "Libellé court", required=True)
    lb_long = fields.Char(string = "Libellé long", required=True)

class RefChapitre(models.Model):
    @api.depends('cd_chapitre','lb_long')
    def _concatenate_chapitre(self):
        for test in self:
            test.chapitre = str(test.cd_chapitre)+ " " +str(test.lb_long)

    _name = "ref_chapitre"
    _rec_name = "cd_chapitre"

    sequence = fields.Integer(default=10)
    chapitre = fields.Char("Chapitre", compute="_concatenate_chapitre")   
    cd_chapitre = fields.Char(string = "Chapitre", ondelete ="cascade", required=True)
    lb_court = fields.Char(string = "Libellé court", required=True)
    lb_long = fields.Char(string = "Libellé long", required=True)

    
class RefArticle(models.Model):
    @api.depends('cd_article','lb_long')
    def _concatenate_article(self):
        for test in self:
            test.article = str(test.cd_article)+ " " +str(test.lb_long)

    _name = "ref_article"
    _rec_name = "cd_article"
    
    sequence = fields.Integer(default=10)
    article = fields.Char("Article", compute="_concatenate_article", store=True)
    cd_article = fields.Char(string = "Article", ondelete ="cascade", required=True)    
    lb_court = fields.Char(string = "Libellé court", required=True)
    lb_long = fields.Char(string = "Libellé long", required=True)


class RefParagraphe(models.Model):
    @api.depends('cd_paragraphe','lb_long')
    def _concatenate_paragraphe(self):
        for test in self:
            test.paragraphe = str(test.cd_paragraphe)+ " " +str(test.lb_long)

    _name = "ref_paragraphe"
    _rec_name = "cd_paragraphe"

    sequence = fields.Integer(default=10)
    paragraphe = fields.Char("Paragraphe", compute="_concatenate_paragraphe")      
    cd_paragraphe = fields.Char(string = "Paragraphe", ondelete ="cascade", required=True)    
    lb_court = fields.Char(string = "Libellé court", required=True)
    lb_long = fields.Char(string = "Libellé long", required=True)


class RefRubrique(models.Model):
    @api.depends('cd_rubrique','lb_long')
    def _concatenate_rubrique(self):
        for test in self:
            test.rubrique = str(test.cd_rubrique)+ " " +str(test.lb_long)

    _name = "ref_rubrique"
    _rec_name = "rubrique"

    sequence = fields.Integer(default=10)
    rubrique = fields.Char("Rubrique", compute="_concatenate_rubrique")
    cd_rubrique = fields.Char(string = "Rubrique", required=True)    
    lb_court = fields.Char(string = "Libellé court", size =35, required=True)
    lb_long = fields.Char(string = "Libellé long", size=65, required=True)
    

class Ref_Piece_Justificative(models.Model):

    _name = "ref_piece_justificatives"
    _rec_name = "lb_long"
    
    lb_court = fields.Char("Libellé court", required=True)
    lb_long = fields.Char("Libellé long", required=True)
    refe = fields.Char("Code")
    modereg = fields.Many2one("ref_modereglement", string="Mode de règlement")
    fg_guichet = fields.Selection([
        ('Y', 'Oui'),
        ('N', 'Non')], 'Guichet')
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)


class Ref_Modereglement(models.Model):

    _name = "ref_modereglement"
    _rec_name = "lb_long"

    sequence = fields.Integer(default=10)
    mode_reg = fields.Char(string = "Code", size = 2)
    lb_court = fields.Char(string = "Libellé court", size = 25, required=True)
    lb_long = fields.Char(string = "Libellé long", size = 100, required=True)
    active = fields.Boolean('Actif',default=True)

    _sql_constraints = [
        ('mode_reg', 'unique (mode_reg)', "Ce code existe déjà. Veuillez changer de code !"),
    ]
        
    
    
class RefDomaine(models.Model):
    _name = 'ref_domaine'
    _rec_name = 'lb_long'
    
    sequence = fields.Integer(help="Gives the sequence when displaying a list of bank.", default=10)
    lb_court = fields.Char('Libellé court', required = True)
    lb_long = fields.Char('Libellé long', required = True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)



class BudgTitre(models.Model):

	_name = "budg_titre"
	_rec_name = "titre"

	sequence = fields.Integer(default=10)
	titre = fields.Many2one("ref_titre", "Titre", required=True)
	cd_titre = fields.Char(string = "Titre", ondelete ="cascade",size=2)
	name = fields.Char(string = "Libellé court")
	lb_long = fields.Char(string = "Libellé long")
	type_titre = fields.Char("Type de titre", size=1)
	active = fields.Boolean('Actif',default=True)
	
	
	@api.onchange('titre')
	def TypeTitre(self):
		
		self.type_titre = self.titre.type_titre


class BudgSection(models.Model):
	_name = "budg_section"
	_rec_name = "section"
	
	sequence = fields.Integer(default=10)
	section = fields.Many2one("ref_section", required=True)
	cd_titre_id = fields.Many2one("budg_titre", string = "Titre", required=True)
	active = fields.Boolean('Actif',default=True)
	

class BudgChapitre(models.Model):

	_name = "budg_chapitre"
	_rec_name = "chapitre"

	sequence = fields.Integer(default=10)
	cd_titre_id = fields.Many2one("budg_titre", string = "Titre", required=True)
	cd_section_id = fields.Many2one("budg_section", string ="Section", required=True)	
	chapitre = fields.Many2one("ref_chapitre", string="Chapitre", required=True)
	active = fields.Boolean('Actif',default=True)

class BudgParamArticle(models.Model):
	_name = 'budg_param_article'
	_rec_name = "article"
	
	sequence = fields.Integer(default=10)
	cd_titre_id = fields.Many2one("budg_titre", string = "Titre", required=True)
	cd_section_id = fields.Many2one("budg_section", string = "Section", required=True)
	cd_chapitre_id = fields.Many2one("budg_chapitre", string="Chapitre", required=True)	
	article = fields.Many2one("ref_article",string = "Article", required=True)
	active = fields.Boolean('Actif',default=True)

class BudgParagraphe(models.Model):
	_name = "budg_paragraphe"
	_rec_name = "paragraphe"

	sequence = fields.Integer(default=10)
	cd_titre_id = fields.Many2one("budg_titre", string = "Titre", required=True)
	cd_section_id = fields.Many2one("budg_section", string = "Section", required=True)
	cd_chapitre_id = fields.Many2one("budg_chapitre", string="Chapitre", required=True)	
	cd_article_id = fields.Many2one("budg_param_article", string = "Article", required=True)
	paragraphe = fields.Many2one("ref_paragraphe", string="Paragraphe", required=True)		
	active = fields.Boolean('Actif',default=True)


class ResCountry(models.Model):
    _inherit = 'res.country'
    
    continent_id = fields.Many2one("ref_continent",string="Continent")
    
"""
class Ref_TypeContribuable(models.Model):

    _name = "ref_typecontribuable"
    _rec_name = "lb_long"

    sequence = fields.Integer(default=10)
    cd_type_contribuable = fields.Char(string = "Code", default=lambda self: self.env['ir.sequence'].next_by_code('cd_type_contribuable'), readonly = True)
    lb_long = fields.Char(string = "Libellé court", size = 25, required=False)
    name = fields.Char(string = "Libellé long", size = 100, required=True)
    active = fields.Boolean('Actif',default=True)
    cate_id = fields.Many2one("ref_categoriecontribuable", required=True,string = "Catégorie de contribuable")
    cpte_client = fields.Many2one("compta_plan_line",string = "Compte tiers", required=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)

    _sql_constraints = [
        ('cd_type_contribuable', 'unique (cd_type_contribuable)', "Ce code existe déjà. Veuillez changer de code !"),
    ]
"""


"""
class BudgContribuable(models.Model):

    _name = "ref_contribuable"
    _rec_name = 'nm_rs'
    
    
    no_contrib = fields.Char(string="Identifiant", default=lambda self: self.env['ir.sequence'].next_by_code('no_contrib'), readonly = True)
    type_contribuable_id = fields.Many2one("ref_typecontribuable",string="Type de contribuable")
    nm_rs = fields.Char(string="Raison sociale/Nom")
    nm_rs2 = fields.Char(string=" ")
    an_agre = fields.Date(string="Année agrément")
    no_agre = fields.Integer(string="N° Agrément")
    no_ifu = fields.Char(string="N° IFU", size=11)
    cd_citib = fields.Char(string="Cd_CITIB")
    activite = fields.Char(string="Activité", size  = 50)
    ap_rue = fields.Char(string="Rue")
    ap_bp = fields.Char(string="Boite Postale")
    ap_cd_post = fields.Char(string="Code Postale")
    ap_region = fields.Many2one("ref_region",string="Région")
    ap_ville = fields.Char(string="Ville")
    ap_province = fields.Many2one("ref_province",string="Province")
    ap_pays = fields.Many2one("ref_pays",string="Pays")
    rf_txt_agre = fields.Char(string="Texte n°")
    dt_txt_agre = fields.Date(string="Du")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    bank_id = fields.Many2one("res.partner.bank", string = "Banque")
    fg_eng = fields.Char()
    active = fields.Boolean('Actif',default=True)
    agence_bank_id = fields.Char(string = "N° Agence")
    acc_number = fields.Char(string = "N° compte")
    tel = fields.Char(string="Téléphone")
    mail = fields.Char(string="Mail")
    cpte_client = fields.Many2one("ref_souscompte", string = "Compte tiers")
    cpte_fournisseur = fields.Many2one("ref_souscompte", string = "Compte tiers")"""


class RefBailleur(models.Model):

    _name = "ref_bailleur"
    _rec_name = "nm_bail"
    
    name = fields.Char()
    cd_bail = fields.Char(string="Code Bailleur", default=lambda self: self.env['ir.sequence'].next_by_code('cd_bail'), readonly = True)
    type_bailleur = fields.Selection([
        ('P', 'Particulier'),
        ('S', 'Société/Institution'),
        ], string ="Type de bailleur", default='P')
    nm_bail = fields.Char(string="Nom Bailleur", size=60)
    lb_sigle = fields.Char(string="Libellé sigle", size=60)
    na_bail = fields.Char(string="na_bail", size=1)
    cd_categ = fields.Char(string="Catégorie", size=4)
    ap_rue = fields.Char(string="Rue", size=35)
    ap_bp = fields.Char(string="Boite Postale", size=8)
    ap_cd_post = fields.Char(string="Code Postale", size=6)
    ap_ville = fields.Char(string="Ville", size=30)
    ap_pays = fields.Many2one("ref_pays",string="Pays", size=3)
    as_rue = fields.Char(string="Rue 2nd", size=35)
    as_bp = fields.Char(string="Boite Postale 2nd", size=8)
    as_cd_post = fields.Char(string="Code Postale 2nd", size=6)
    as_ville = fields.Char(string="Ville 2nd", size=30)
    as_pays = fields.Many2one("ref_pays",string="Pays 2nd", size=8)
    tel = fields.Char(string="Téléphone", size=30)
    mail = fields.Char(string="Mail", size=50)
    site = fields.Char(string="Site WEB", size=50)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    bank_id = fields.Many2one("res.bank", string = "Banque")
    acc_bank_id = fields.Char(string = "N° Compte", size=30)
    active = fields.Boolean('Actif',default=True)

    _sql_constraints = [
        ('cd_bail', 'unique (cd_bail)', "Ce code existe déjà. Veuillez changer de code !"),
    ]
    

class RefCategorieContribualbe(models.Model):

    _name = "ref_categoriecontribuable"

    sequence = fields.Integer(default=10)
    lb_court = fields.Char(string = "Libellé court", size = 25)
    name = fields.Char(string = "Libellé long", size = 100, required=True)
    active = fields.Boolean('Actif',default=True)
    
    
class RefCategorieBeneficiaire(models.Model):

    _name = "ref_categoriebeneficiaire"

    sequence = fields.Integer(default=10)
    lb_court = fields.Char(string = "Libellé court", size = 25)
    name = fields.Char(string = "Libellé long", size = 100, required=True)
    active = fields.Boolean('Actif',default=True)
    
"""class ref_TypeBeneficiaire(models.Model):

    _name = "ref_typebeneficiaire"
    _rec_name = "lb_long"

    sequence = fields.Integer(default=10)
    cd_type_beneficiaire = fields.Char(string = "Code", size = 2)
    name = fields.Char(string = "Libellé court", size = 25, required=True)
    lb_long = fields.Char(string = "Libellé long", size = 100, required=True)
    cat_id = fields.Many2one("ref_categoriebeneficiaire", string = "Catégorie de bénéficiaire", required=True)
    cpte_client = fields.Many2one("compta_plan_line",string = "Compte tiers", required=True)
    active = fields.Boolean('Actif',default=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)

    _sql_constraints = [
        ('cd_type_beneficiaire', 'unique (cd_type_beneficiaire)', "Ce code existe déjà. Veuillez changer de code !"),
    ]    
 

class RefBeneficiaire(models.Model):

    _name = "ref_beneficiaire"
    _rec_name = "nm"
    
    name = fields.Char(string="Identifiant", default=lambda self: self.env['ir.sequence'].next_by_code('name'), readonly = True)
    no_beneficiaire = fields.Char(string="Raison sociale", size=65)
    type_beneficiaire_id = fields.Many2one("ref_typebeneficiaire",string="Type de bénéficiaire", required=True)
    nm = fields.Char(string="Intitulé", size=20)
    pn = fields.Char(string="Prénom", size=40)
    no_ifu = fields.Char(string="N° IFU", size=20)
    domaine_id = fields.Many2one('ref_secteur_activite', "Domaine d'activité", required=False)
    cd_mat = fields.Char(string="Matricule", size=20)
    no_eng = fields.Integer(string="No_Eng")
    ex_last = fields.Integer(string="Ex_last")
    ap_rue = fields.Char(string="Rue", size=35)
    ap_bp = fields.Char(string="Boite postale", size=8)
    ap_cd_post = fields.Char(string="Code postal", size=6)
    ap_ville = fields.Char(string="Ville", size=30)
    ap_pays = fields.Many2one("ref_pays",string="Pays")
    tel = fields.Char(string="Téléphone", size=30)
    nm_officiel = fields.Char(string="Titre officiel", size=50)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    bank_id = fields.Many2one("res.bank", string = "Banque")
    active = fields.Boolean('Actif',default=True)
    fg_bloc = fields.Char()
    cpte_client = fields.Many2one("ref_souscompte", string = "Compte tiers")
    cpte_fournisseur = fields.Many2one("compta_plan_line", string = "Compte tiers")
    agence_bank_id = fields.Char(string = "N° Agence")
    acc_number = fields.Char(string = "N° compte")
    cat_fournisseur = fields.Selection([
        ('S', 'Société'),
        ('P', 'Particulier')], 'Catégorie ')"""


class Compta_compte(models.Model):
    _name='compta_plan'
    _rec_name='sousclasse_id'
    
    sousclasse_id = fields.Many2one("ref_sousclasse_pcg", 'Sous classe', domain="[('type_structure','=', structure)]", required= True)
    plan_line = fields.One2many("compta_plan_line", 'plan_id')
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    structure = fields.Many2one("ref_type_structure")
    
    
    @api.onchange('company_id')
    def test(self):
        if self.company_id:
         self.structure = self.company_id.ref_type_struct_id
    

class Compta_compte_line(models.Model):
    _name='compta_plan_line'
    _rec_name = 'souscpte'
    
    plan_id = fields.Many2one('compta_plan')
    cpte = fields.Many2one('ref_compte', 'Compte', required= True, domain="[('type_structure','=', type_structure)]")
    souscpte = fields.Many2one('ref_souscompte', 'Sous compte', required= True,domain="[('type_struct','=', type_structure)]")
    libelle = fields.Char("Libellé", readonly=True)
    fg_sens = fields.Selection([
        ('D', 'Débit'),
        ('C', 'Crébit'),
        ('M', 'Mixte'),
        ], 'Sens', required= True)
    fg_lettrage = fields.Boolean(string="Let.")
    fg_attente = fields.Boolean(string="Att.")
    fg_bloque = fields.Boolean()
    fg_finance = fields.Boolean(string="Fin.")
    fg_ng = fields.Boolean(string="Ng")
    
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    type_structure = fields.Many2one("ref_type_structure")
    
    @api.onchange("souscpte")
    def OnchangeSouscompte(self):
        
        if self.souscpte:
            self.libelle = self.souscpte.lb_long
            
    
    @api.onchange('company_id')
    def test(self):
        if self.company_id:
            self.type_structure = self.company_id.ref_type_struct_id
