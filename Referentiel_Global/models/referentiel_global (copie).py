from odoo import fields,api,models
from datetime import datetime
from email.policy import default

class RefContinent(models.Model):
    _name = "ref_continent"
    _order = 'sequence, id'
    sequence = fields.Integer(help="Gives the sequence when displaying a list of continent.", default=10)
    name = fields.Char(string = "Libéllé long", required = True,size = 65)
    libcourt = fields.Char(string = "Libéllé court",size = 35)
    code_continent = fields.Char(string = "Code",required = True,size = 2)
    description = fields.Text(string = "Description",size = "1000")

    _sql_constraints = [('code_continent_unique', 'unique(code_continent)', 
                     'Ce code d identification du continent existe dejà, svp entrer un autre code')]
    
     
class RefPays(models.Model):
    _name = "ref_pays"
    _order = 'sequence, id'
    sequence = fields.Integer(help="Gives the sequence when displaying a list of Pays.", default=10)
    country_id = fields.Many2one('res.country', string = 'Nationalité (Pays)', groups="hr.group_hr_user")
    name = fields.Char(string = "Libéllé court", required = True,size = 35)
    ref_continent_id = fields.Many2one('ref_continent', string = 'Continent')
    code_pays = fields.Char(string = "Code",required = True,size = 2)
    _sql_constraints = [('code_pays_unique', 'unique(code_pays)', 
                     'Ce code d identification du pays existe dejà, svp entrer un autre code')]
   
    
class RefRegion(models.Model):
    _name = "ref_region"
    _order = 'sequence, id'
    sequence = fields.Integer(help="Gives the sequence when displaying a list of region.", default=10)
    name = fields.Char(string = "Libéllé long", required = True)
    libcourt = fields.Char(string = "Libéllé court", size = 35)
    ref_pays_id = fields.Many2one('ref_pays', string = 'Pays')
    code_region = fields.Char(string = "Code",required = True,size = 2)
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
    name = fields.Char(string = "Libéllé long", required = True, size = 65)
    libcourt = fields.Char(string = "Libéllé court", size = 35)
    chef_lieu = fields.Char(string = "Chef lieu")
    code_province = fields.Char(string = "Code",required = True) 
    ref_region_id = fields.Many2one('ref_region', string = 'Région')
    _sql_constraints = [('code_province_unique', 'unique(code_province)', 
                     'Ce code d identification de province existe dejà, svp entrer un autre code')]

    
class RefDepartement(models.Model):
    _name = "ref_departement"
    _order = 'sequence, id'
    sequence = fields.Integer(help="Gives the sequence when displaying a list of departement.", default=10)
    name = fields.Char(string = "Libéllé long", required = True, size = 65)
    libcourt = fields.Char(string = "Libéllé court",size = 35)
    ref_province_id = fields.Many2one('ref_province', string = 'Province') 
    code_dep = fields.Char(string = "Code",required = True)
    _sql_constraints = [('code_dep_unique', 'unique(code_dep)', 
                     'Ce code d identification de departement existe dejà, svp entrer un autre code')]


    
class RefCommune(models.Model):
    _name = "ref_commune"
    _order = 'sequence, id'
    sequence = fields.Integer(help="Gives the sequence when displaying a list of commune.", default=10)
    name = fields.Char(string = "Libéllé long", required = True,size = 65)
    libcourt = fields.Char(string = "Libéllé court", size = 35)
    ref_departement_id = fields.Many2one('ref_departement', string = 'Département') 
    ref_province_id = fields.Many2one('ref_province', string = 'Province') 
    code_commune = fields.Char(string = "Code",required = True)
    _sql_constraints = [('code_commune_unique', 'unique(code_commune)', 
                     'Ce code d identification de commune existe dejà, svp entrer un autre code')]


    
class RefLocalite(models.Model):
    _name = "ref_localite"
    _order = 'sequence, id'
    sequence = fields.Integer(help="Gives the sequence when displaying a list of localité.", default=10)
    name = fields.Char(string = "Libéllé long", required = True, size = 65)
    libcourt = fields.Char(string = "Libéllé court", size = 35)
    ref_departement_id = fields.Many2one('ref_departement', string = 'Département') 
    ref_province_id = fields.Many2one('ref_province', string = 'Province') 
    code_localite = fields.Char(string = "Code",required = True)
    _sql_constraints = [('code_localite_unique', 'unique(code_localite)', 
                     'Ce code d identification de localité existe dejà, svp entrer un autre code')]



class RefCategorieStructure(models.Model):
    
    _name = "ref_categorie_structure"
    _order = 'sequence, id'
    sequence = fields.Integer(help="Gives the sequence when displaying a list of cat.Struct.", default=10)
    code_cat_struct = fields.Char(string = 'Code',size = 2, required = True)
    abreg = fields.Char(string = "Abrégé")
    name = fields.Char(string = "Libellé long", required = True, size = 65)
    lib_court = fields.Char(string = "Libellé court", size = 35)
    _sql_constraints = [('code_cat_struct_unique', 'unique(code_cat_struct)', 
                     'Ce code d identification de categorie structure existe dejà, svp entrer un autre code')]



class RefTypeStructure(models.Model):
    
    _name = "ref_type_structure"
    _order = 'sequence, id'
    sequence = fields.Integer(help="Gives the sequence when displaying a list of type structure.", default=10)
    name = fields.Char(string = "Libellé long", required = True, size = 65)
    lib_court = fields.Char(string = "Libellé court", size = 35)
    actif = fields.Boolean() 
    #code_type_struct = fields.Char(string = 'Code',size = 2,required = True)
    



class RefProfilStructure(models.Model):
    
    _name = "ref_profil_structure"
    _order = 'sequence, id'
    sequence = fields.Integer(help="Gives the sequence when displaying a list of profil strucutre.", default=10)
    name = fields.Char(string = "Libellé long", required = True, size = 65)
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
    ref_type_struct_id = fields.Many2one('ref_type_structure', string = 'Type Structure')
    ref_cat_struct_id = fields.Many2one('ref_categorie_structure', string = 'Catégorie Structure')
    ref_localite_id = fields.Many2one('ref_localite', string = 'Localité')
    code_struct = fields.Char(string = 'Code',size = 5) 
    actif = fields.Boolean() 
    """_sql_constraints = [('code_struct_unique', 'unique(code_struct)', 
                     'Ce code d identification de structure existe dejà, svp entrer un autre code')]"""
    
    
class RefPoste(models.Model):
    _name = "ref_poste"
    _order = 'sequence, id'
    sequence = fields.Integer(help="Gives the sequence when displaying a list of Poste.", default=10)
    name = fields.Char(string = "Titre/Poste", required = True)
    code_post_struct = fields.Char(string = 'Code',size = 2,required = True)
    description = fields.Text(string = "Description", size = "1000")


class RefExercice(models.Model):
    
    _name = "ref_exercice"
    _rec_name = "no_ex"
    _order = 'sequence, id'
    sequence = fields.Integer(help="Gives the sequence when displaying a list of Exercice.", default=10)
    name = fields.Char(string = "Libellé long", required = True,size = 65)
    no_ex = fields.Char(string = "N°Exercice", required = True)
    lib_court = fields.Char(string = "Libellé court", size = 35)
    code_exo_struct = fields.Char(string = 'Code',size = 2,required = True) 
    etat = fields.Selection([
        (1,'Y'),
        (2,'N'),
         
        ], string = "Etat", default=1)
    
class HrUsers(models.Model):
    
    _inherit = "res.users"
    x_exercice_id = fields.Many2one('ref_exercice',string = 'Choisir Exercice', default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]))
    

class RefTypepiece(models.Model):
    _name = "ref_type_piece"
    _order = 'sequence, id'
    sequence = fields.Integer(help="Gives the sequence when displaying a list of type pièce.", default=10)
    name = fields.Char(string = "Libéllé long", required = True, size = 65)
    libcourt = fields.Char(string = "Libéllé court", size = 35)
    code_type_piec_struct = fields.Char(string = 'Code',size = 2,required = True)
    description = fields.Text(string = "Description",size = 1000)



class RefSecteurActivite(models.Model):
    _name = "ref_secteur_activite"
    _order = 'sequence, id'
    sequence = fields.Integer(help="Gives the sequence when displaying a list of Activities.", default=10)
    name = fields.Char(string = "Libéllé long", required = True, size = 65)
    libcourt = fields.Char(string = "Libéllé court", size = 35)
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


"""class RefBanque(models.Model):
    _name = "ref_banque"

    code_swift = fields.Char(string = "Code SWIFT", required = True)
    sigle = fields.Char(string = "Sigle", required = True)
    lib_long = fields.Char(string = "Libellé long", required = True)
    name = fields.Char(string = "Libellé court")
    actif = fields.Boolean()  """ 
    
    
    
class temp_change_exo_user(models.Model):
    _name = "temp_change_exo_user"
    user_id = fields.Integer('res.users', default=lambda self: self.env.user)
    x_exercice_en_cours = fields.Char(string = 'Exercice en cours')
    #user_idd = fields.Integer(string = 'User Current')
    #company_id = fields.Many2one('res.company')
    """x_exercice_temp_id = fields.Many2one('ref_exercice',default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]))
    x_datetime = fields.Datetime(default=fields.Datetime.now)
    x_exercice_temps = fields.Char(string = 'Exercice en cours')
    x_exercice_temp_idd = fields.Many2one('ref_exercice', string = 'Choisir Exercice ')"""
   

    
    
    """@api.onchange('x_exercice_temp')
    def temp_valider(self):
        
        cd_user = int(self.user_id)
        print('lidentifiant',cd_user)
        no_ex = self.env['ref_exercice'].search([('etat','=',1)])
        nox = int(no_ex)
        print('exo',nox)
        
        sql = self.env.cr.execute("select count(*) from temp_change_exo_user WHERE user_id = %d " %(cd_user))
        print('sql',sql)
        
        if sql ==0:
            print('sql ok')
        
            self.env.cr.execute("insert into temp_change_exo_user (user_id) VALUES (%d )" %(cd_user))
            
        else:
            print('sql non ok')
            self.env.cr.execute("UPDATE temp_change_exo_user SET x_exercice_temp = %d WHERE user_id = %d  " %(nox,cd_user))
        """
        
    #@api.onchange('x_exercice_temp_idd')
    def temp_changer_exercice(self):
        #formatage de l'utilisateur en cours
        cd_user = int(self.user_id)
        #recuperation de l'id de l'exercice qu'il va selectionné dans le comba 
        nox = int(self.x_exercice_temp_idd)
        #pointage a partir de la table temp_change_exo_user pour acceder a la table ref_exercice et au champ no_ex
        nox_lib = self.x_exercice_temp_idd.no_ex
        print('exo',nox)
        #cherche dans la table temp_change_exo_user pour voir si l'utilisateur connecté et l'exercice courant s'y trouve 
        res = self.env['temp_change_exo_user'].search([('user_id','=', cd_user),('x_exercice_temps','!=', '')])
        #Mise à jour de la table temp_change_exo_user avec les informations telles que no_ex et le id de l'exercice selectionné precedemment
        self.env.cr.execute("UPDATE temp_change_exo_user SET x_exercice_temp_id = %d, x_exercice_temps = %s WHERE user_id = %d  " %(nox,nox_lib,cd_user))
        
    """def exercice_en_cours(self):
        
        
        #user_idd = user_id
        cd_user = int(self.user_id)
        res = self.env['temp_change_exo_user'].search([('user_id','=', cd_user)])
        user_ident = int(res.user_id)
        print('User connecté',user_ident)
        #current_date = datetime.now()
        #nox = current_date.year
        nbre_user = self.env.cr.execute("SELECT count(*) FROM temp_change_exo_user WHERE user_id = %d" %(user_ident))
        if nbre_user == 1:
            res = self.env['ref_exercice'].search([('etat','=', 1)])
            no_exo = int(res.id)
            no_exo_ex = str(res.no_ex)
            print('Id exercice',no_exo)
            print('Exercice n°',no_exo_ex)
            print('Nombre enregistrment', nbre_user)
            
            self.env.cr.execute("UPDATE temp_change_exo_user SET x_exercice_temp_id = %d  WHERE user_id = %d" %(no_exo,user_ident))
            self.env.cr.execute("SELECT T.id AS identif FROM temp_change_exo_user T, ref_exercice E WHERE T.x_exercice_temp_id = E.id AND E.etat = 1 AND T.user_id = %d " %(user_ident))
            res = self.env.cr.fetchone()[0]
            resu = int(res)
            print('RESU',res)
            self.env.cr.execute("UPDATE res_users SET x_exercice_tmp_id = %d WHERE id = %d" %(resu,user_ident))
            
            self.x_exercice_temps = no_exo_ex
            #self.x_datetime = datetime.now()
        elif nbre_user == 2:
            self.env.cr.execute("DELETE FROM temp_change_exo_user WHERE user_id = %d AND x_datetime < current_timestamp" %(user_ident))
        """
            
        
    
    
    def exercice_cours(self):
        current_date = datetime.now()
        nox = current_date.year
        #current_user = fields.Many2one('res.users','Current User', default=lambda self: self.env.user)

        cd_user = int(self.user_id)
        print('USER',cd_user)
        x_exo = current_date.year
        x_exon = int(x_exo)
        print('NUM',x_exon)

        self.env.cr.execute("UPDATE res_users SET x_exercice_tmp_id = 11 WHERE id = 2")
        
        res = self.env['res.users'].search([('user_id','=', cd_user)])
        self.x_exercice_temps = res.x_exercice_tmp_id.no_ex
        """val_temp = self.x_exercice_temp
        print('VAL EXO',val_temp)
        if val_temp == 0:
            self.env.cr.execute("UPDATE temp_change_exo_user SET x_exercice_temps = %s WHERE user_id = %d  " %(nox,cd_user))
         """
            
        #resul = int(self.env.cr.execute("select count(*) from temp_change_exo_user WHERE user_id = %d " %(cd_user)))
        #resul = self.env['temp_change_exo_user'].search([('user_id','=',cd_user)])
        #res = resul
        #print('result',res)
        """if resul == 0:
            self.x_exercice_temp = current_date.year
            vals = self.x_exercice_temp
            print('Valeur date =',vals)
            self.env.cr.execute("insert into temp_change_exo_user (user_id,x_exercice_temp) VALUES (%d )" %(cd_user,vals))
        """

